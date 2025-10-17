import os
import time
import base64
import requests
import platform
import tkinter as tk
from mss import mss
from PIL import Image

# --- 用户配置区域 ---
# AI 服务配置
API_KEY = "sk-hB8k74BrUN6h"  # 替换为你的 API 密钥
BASE_URL = "https://api" # 替换为你的 API 地址, 例如 "https://api.openai.com/v1/chat/completions"
AI_MODEL = "gpt-5-mini" # 替换为你要调用的模型名称

# 功能配置
SCREENSHOT_INTERVAL_SECONDS = 5  # 每隔多少秒截取一次屏幕
ANALYSIS_INTERVAL_MINUTES = 1     # 每隔多少分钟分析一次
RESIZE_FACTOR = 0.25               # 截图分辨率缩放因子 (0.5 表示长宽各缩小一半)

# --- 路径配置 (自动设置) ---
script_dir = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_FOLDER = os.path.join(script_dir, "activity_logs")
REPORTS_FOLDER = os.path.join(script_dir, "analysis_reports")
# --- 配置结束 ---

def take_and_resize_screenshot(sct, output_path):
    """截取所有屏幕的组合视图，并将其调整大小后保存。"""
    screenshot = sct.grab(sct.monitors[0])
    img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
    
    original_width, original_height = img.size
    new_width = int(original_width * RESIZE_FACTOR)
    new_height = int(original_height * RESIZE_FACTOR)
    
    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    resized_img.save(output_path, "JPEG", quality=85)

def create_composite_image(image_paths, output_path):
    """将多张图片垂直拼接成一张。"""
    if not image_paths:
        return None
    
    images = [Image.open(p) for p in image_paths]
    
    widths, heights = zip(*(i.size for i in images))
    max_width = max(widths)
    total_height = sum(heights)

    composite_img = Image.new('RGB', (max_width, total_height), color='white')
    y_offset = 0
    for img in images:
        composite_img.paste(img, (0, y_offset))
        y_offset += img.height
        img.close()

    composite_img.save(output_path, "JPEG")
    return output_path

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image_with_ai(image_path):
    base64_image = encode_image_to_base64(image_path)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    prompt = """
    请将自己定位为一位专业的生产力教练。附件是我过去几分钟的电脑屏幕活动记录拼接图。请基于这些图片，用亲切、鼓励的语气，完成以下任务：
    1. **活动总结**: 简要总结我在这段时间内做了什么。
    2. **鼓励与反思**: 肯定我做得好的地方，并引导我反思是否存在可以改进之处。
    3. **下一步建议**: 根据我的活动内容，为我指出接下来可以专注的一到两个具体方向。
    
    注意，1，请以纯文本格式返回，只能借助标点符号和表情排版，让内容清晰易读。
    2，这些截图有些是重复的，没有变化的，我并没有反复操作切换任务，请你聚焦在我的操作部分。
    3，简洁描述，我没有时间去详细阅读。
    """
    
    payload = {
        "model": AI_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }

    try:
        response = requests.post(BASE_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        return content
    except requests.exceptions.RequestException as e:
        return f"API 请求失败: {e}"
    except (KeyError, IndexError) as e:
        return f"解析 API 响应失败: {e}\n响应内容: {response.text}"

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
    # 自动创建所需的文件夹
    if not os.path.exists(SCREENSHOT_FOLDER):
        os.makedirs(SCREENSHOT_FOLDER)
    if not os.path.exists(REPORTS_FOLDER):
        os.makedirs(REPORTS_FOLDER)

    analysis_interval_seconds = ANALYSIS_INTERVAL_MINUTES * 60

    try:
        with mss() as sct:
            while True:
                print(f"开始新的 {ANALYSIS_INTERVAL_MINUTES} 分钟监控周期...")
                analysis_start_time = time.time()
                screenshot_paths = []
                
                while time.time() - analysis_start_time < analysis_interval_seconds:
                    loop_start_time = time.time()
                    
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"screenshot_{timestamp}.jpg"
                    output_path = os.path.join(SCREENSHOT_FOLDER, filename)
                    
                    take_and_resize_screenshot(sct, output_path)
                    screenshot_paths.append(output_path)
                    print(f"截图已保存: {filename} (所有屏幕)")
                    
                    elapsed_time = time.time() - loop_start_time
                    sleep_time = max(0, SCREENSHOT_INTERVAL_SECONDS - elapsed_time)
                    time.sleep(sleep_time)

                print("\n监控周期结束，准备生成分析报告...")
                if screenshot_paths:
                    composite_image_path = os.path.join(SCREENSHOT_FOLDER, "composite.jpg")
                    create_composite_image(screenshot_paths, composite_image_path)
                    
                    print("正在调用 AI 进行分析，请稍候...")
                    ai_feedback = analyze_image_with_ai(composite_image_path)
                    
                    # --- 保存报告到 TXT 文件并自动打开 ---
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

                    # --- 清理本次周期的截图和拼接图 ---
                    os.remove(composite_image_path)
                    for p in screenshot_paths:
                        os.remove(p)
                else:
                    print("未截取到任何屏幕，跳过分析。")

    except KeyboardInterrupt:
        print("\n程序已停止。")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":

    main()

