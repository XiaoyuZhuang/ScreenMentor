# ScreenMentor
一个开源的Python工具，通过定时截屏并调用视觉AI模型，自动分析你的工作流，并生成可执行的生产力改进报告。

# 🤖 ScreenMentor：你的 AI 生产力导师

**ScreenMentor** 是一个基于定时屏幕截图和 AI 分析的个人生产力教练工具。它就像一位能看见你屏幕的私人导师，通过分析你的数字行为，帮助你反思工作模式、保持专注并提高效率。

[![语言](https://img.shields.io/badge/语言-Python-blue.svg)](https://www.python.org/)

## ✨ 项目简介

您是否常常在一天结束后，感觉忙忙碌碌却不知道时间花在了哪里？ScreenMentor 正是为了解决这个问题而生。它会：

1.  在后台默默记录您的屏幕活动。
2.  定期将活动截图汇总，并发送给强大的视觉 AI 模型进行分析。
3.  以鼓励和引导的口吻，为您生成一份关于您刚刚这段时间工作内容的**总结、反思和建议**。
4.  最终，帮助您形成更好的工作习惯，将精力聚焦在最重要的事情上。

---

## 🚀 主要功能

* **💻 跨平台多屏幕截图**: 自动定时截取所有连接的显示器画面，完整记录您的工作区。
* **⚙️ 高度可配置**: 您可以自由设定截图的频率、AI 分析的周期以及调用的 AI 模型。
* **🖼️ 智能图片处理**: 截图后会自动降低分辨率并拼接成一张活动长图，节省资源并便于分析。
* **🧠 灵活的 AI 集成**: 只需修改配置文件，即可轻松接入任何支持图片输入的 AI 模型 API (如 OpenAI GPT-4V, Gemini Pro Vision 等)。
* **📂 自动化文件管理**:
    * 自动创建并管理截图文件夹 (`activity_logs`) 和报告文件夹 (`analysis_reports`)。
    * 临时截图在每次分析后会自动清理，保持项目整洁。
    * 生成的分析报告会以带时间戳的 `.txt` 文件永久保存在 `analysis_reports` 文件夹中。
* **✍️ 即时反馈**: 每次分析完成后，会自动用系统默认的文本编辑器打开最新的报告，让您第一时间看到反馈。

---

## 🔧 工作流程

脚本的运行逻辑非常简单和清晰：

1.  **启动监控周期** (例如，每 2 分钟)。
2.  **周期内持续截图** (例如，每 10 秒截取一次所有屏幕)。
3.  **周期结束，处理图片**：将周期内截取的所有图片垂直拼接成一张长图。
4.  **调用 AI 分析**：将拼接后的长图发送给您配置的 AI 模型。
5.  **保存并打开报告**：将 AI 返回的文本保存为 `.txt` 文件，并自动打开它。
6.  **清理临时文件**：删除本次周期产生的截图和拼接图。
7.  **循环往复**：开始下一个监控周期。

---

## 🛠️ 安装与使用

### 1. 环境准备

* Python 3.6+

### 2. 安装

1.  **克隆本仓库**
    ```bash
    git clone https://github.com/XiaoyuZhuang/ScreenMentor.git
    cd ScreenMentor
    ```

2.  **安装依赖库**
    ```bash
    pip install mss Pillow requests
    ```

### 3. 配置

打开项目中的 Python 脚本文件 (例如 `screen_mentor.py`)，修改顶部的**用户配置区域**：

```python
# --- 用户配置区域 ---
# AI 服务配置
API_KEY = "YOUR_API_KEY"  # 替换为你的 API 密钥
BASE_URL = "YOUR_AI_API_BASE_URL" # 替换为你的 API 地址
AI_MODEL = "gpt-5-mini" # 替换为你要调用的模型名称

# 功能配置
SCREENSHOT_INTERVAL_SECONDS = 10  # 每隔多少秒截取一次屏幕
ANALYSIS_INTERVAL_MINUTES = 2     # 每隔多少分钟分析一次
RESIZE_FACTOR = 0.5               # 截图分辨率缩放因子 (0.5 表示长宽各缩小一半)
# --- 配置结束 ---
```
* `API_KEY`: 您的 AI 服务提供商的密钥。
* `BASE_URL`: 您的 AI 服务的 API 端点 (Endpoint)。
* `AI_MODEL`: 您希望使用的具体模型名称。
* 其他参数可根据您的使用习惯进行调整。

### 4. 运行

配置完成后，直接在终端运行脚本即可：

```bash
python screen-ai.py
```

程序启动后，会开始在后台截屏。每个分析周期结束后，会自动弹出分析报告。要停止程序，请在运行脚本的终端窗口按下 `Ctrl + C`。

---

## 📁 文件结构

运行后，项目文件夹将保持如下结构：

```
/ScreenMentor
├── screen_mentor.py     <-- 你的Python脚本
├── README.md
├── activity_logs/       <-- 临时截图存放处 (自动清理)
└── analysis_reports/    <-- AI分析报告永久保存处
    └── report_xxxxxxxx_xxxxxx.txt
```

---

## 🤝 贡献

欢迎通过提交 Issue 或 Pull Request 来改进这个项目！

## 📄 许可证

本项目使用 [MIT 许可证](LICENSE) 授权。
