import os
import time
import base64
import requests
import platform
import subprocess
from mss import mss
from PIL import Image

# --- 用户配置区域 ---
# AI 服务配置
API_KEY = "sk-hB8k74BN6h0ovyvUN6h"  # 替换为你的 API 密钥
BASE_URL = "https://api/v1/chat/completions" # 替换为你的 API 地址
AI_MODEL = "gpt-5-mini" # 替换为你要调用的模型名称

# 功能配置
SCREENSHOT_INTERVAL_SECONDS = 5   # 每隔多少秒截取一次屏幕
ANALYSIS_INTERVAL_MINUTES = 3     # 每隔多少分钟分析一次
OCR_BATCH_SIZE = 3                # 每 3 张截图合并进行一次 OCR 提取

# --- 路径配置 (自动设置) ---
script_dir = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_FOLDER = os.path.join(script_dir, "activity_logs")
REPORTS_FOLDER = os.path.join(script_dir, "analysis_reports")
# --- 配置结束 ---

def take_screenshot(sct, output_path):
    """截取主屏幕的视图并保存。"""
    screenshot = sct.grab(sct.monitors[0]) # monitor[1] 通常是主屏幕
    img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
    img.save(output_path, "JPEG", quality=95)

def encode_image_to_base64(image_path):
    """将图片文件编码为 Base64 字符串。"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_text_with_ai_ocr(image_paths):
    """使用多模态 API 从一批图片中提取文字。"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # 构建包含 OCR 指令和多张图片的内容列表
    content_list = [
        {"type": "text", "text": "你是一个精准的OCR工具。请从以下图片中提取所有可见的文字。按照图片顺序，将所有文字合并成一个连贯的文本块返回。不要添加任何解释或评论，只返回提取的纯文本。"}
    ]
    for path in image_paths:
        base64_image = encode_image_to_base64(path)
        content_list.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        })

    payload = {
        "model": AI_MODEL,
        "messages": [{"role": "user", "content": content_list}],
        "max_tokens": 2000 # 为 OCR 结果预留足够空间
    }

    try:
        response = requests.post(BASE_URL, headers=headers, json=payload, timeout=180) # 增加超时
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"API OCR 请求失败: {e}")
        return ""
    except (KeyError, IndexError) as e:
        print(f"解析 API OCR 响应失败: {e}\n响应内容: {response.text}")
        return ""

def analyze_text_with_ai(combined_text):
    """将汇总的文本发送给 AI 进行生产力分析。"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    final_prompt = f"""
    请将自己定位为一位专业的生产力教练。以下是我过去几分钟从电脑屏幕上提取的文本活动记录。请基于这些文本，用亲切、鼓励的语气，完成以下任务：
    1. **活动总结**: 简要总结我在这段时间内做了什么。
    2. **鼓励与反思**: 肯定我做得好的地方，并引导我反思是否存在可以改进之处。
    3. **下一步建议**: 根据我的活动内容，为我指出接下来可以专注的一到两个具体方向。

    注意：
    1. 请以纯文本格式返回，只能借助标点符号和表情排版，让内容清晰易读。
    2. 这些文本记录可能包含重复内容，因为屏幕可能在一段时间内没有变化。请你聚焦在我的核心操作和关注点上。
    3. 简洁描述，我没有时间去详细阅读。

    --- 活动文本记录开始 ---
    {combined_text}
    --- 活动文本记录结束 ---
    """

    payload = {
        "model": AI_MODEL,
        "messages": [{"role": "user", "content": final_prompt}],
        "max_tokens": 1000
    }

    try:
        response = requests.post(BASE_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f"API 分析请求失败: {e}"
    except (KeyError, IndexError) as e:
        return f"解析 API 分析响应失败: {e}\n响应内容: {response.text}"

def open_file_with_default_app(filepath):
    """根据不同操作系统，使用默认程序打开文件。"""
    try:
        if platform.system() == 'Darwin':       # macOS
            subprocess.run(['open', filepath], check=True)
        elif platform.system() == 'Windows':    # Windows
            os.startfile(filepath)
        else:                                   # Linux
            subprocess.run(['xdg-open', filepath], check=True)
    except Exception as e:
        print(f"无法自动打开文件 '{filepath}': {e}")

def main():
    if not os.path.exists(SCREENSHOT_FOLDER):
        os.makedirs(SCREENSHOT_FOLDER)
    if not os.path.exists(REPORTS_FOLDER):
        os.makedirs(REPORTS_FOLDER)

    analysis_interval_seconds = ANALYSIS_INTERVAL_MINUTES * 60

    try:
        with mss() as sct:
            while True:
                print(f"--- 开始新的 {ANALYSIS_INTERVAL_MINUTES} 分钟监控周期 ---")
                analysis_start_time = time.time()
                
                all_screenshot_paths = []
                screenshot_batch = []
                all_extracted_text = ""

                while time.time() - analysis_start_time < analysis_interval_seconds:
                    loop_start_time = time.time()
                    
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"screenshot_{timestamp}.jpg"
                    output_path = os.path.join(SCREENSHOT_FOLDER, filename)
                    
                    take_screenshot(sct, output_path)
                    screenshot_batch.append(output_path)
                    all_screenshot_paths.append(output_path)
                    print(f"截图: {filename} (当前批次 {len(screenshot_batch)}/{OCR_BATCH_SIZE})")

                    # 当批次达到指定大小时，进行 OCR 处理
                    if len(screenshot_batch) >= OCR_BATCH_SIZE:
                        print(f"达到批次大小 {OCR_BATCH_SIZE}，开始 API OCR...")
                        extracted_text = extract_text_with_ai_ocr(screenshot_batch)
                        if extracted_text.strip():
                            print("API OCR 成功。")
                            all_extracted_text += extracted_text + "\n---\n"
                        else:
                            print("API OCR 未返回有效文本。")
                        screenshot_batch.clear() # 清空批次以便重新收集

                    elapsed_time = time.time() - loop_start_time
                    sleep_time = max(0, SCREENSHOT_INTERVAL_SECONDS - elapsed_time)
                    time.sleep(sleep_time)
                
                # 处理周期结束时剩余的、未满一个批次的截图
                if screenshot_batch:
                    print(f"处理剩余的 {len(screenshot_batch)} 张截图...")
                    extracted_text = extract_text_with_ai_ocr(screenshot_batch)
                    if extracted_text.strip():
                        print("API OCR 成功。")
                        all_extracted_text += extracted_text + "\n---\n"
                    screenshot_batch.clear()

                print("\n监控周期结束，汇总文本并生成报告...")
                if all_extracted_text.strip():
                    print("正在调用 AI 进行分析，请稍候...")
                    ai_feedback = analyze_text_with_ai(all_extracted_text)
                    
                    report_timestamp = time.strftime("%Y%m%d_%H%M%S")
                    report_filename = f"report_{report_timestamp}.txt"
                    report_path = os.path.join(REPORTS_FOLDER, report_filename)
                    
                    try:
                        with open(report_path, 'w', encoding='utf-8') as f:
                            f.write(ai_feedback)
                        print(f"AI 分析完成，报告已保存至: {report_path}")
                        open_file_with_default_app(report_path)
                    except IOError as e:
                        print(f"写入报告文件失败: {e}")
                else:
                    print("周期内未提取到任何有效文本，跳过分析。")
                
                print("清理本周期所有临时截图中...")
                for p in all_screenshot_paths:
                    if os.path.exists(p):
                        os.remove(p)
                print("--- 监控周期完成 ---\n")

    except KeyboardInterrupt:
        print("\n程序已停止。")
    except Exception as e:
        print(f"发生未处理的错误: {e}")

if __name__ == "__main__":
    main()