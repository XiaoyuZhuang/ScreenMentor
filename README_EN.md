# ScreenMentor
An open-source Python tool that automatically analyzes your workflow by taking periodic screenshots and calling a vision AI model to generate actionable productivity improvement reports.

# 🤖 ScreenMentor: Your AI Productivity Mentor

**ScreenMentor** is a personal productivity coaching tool based on periodic screen captures and AI analysis. It acts like a personal mentor who can see your screen, helping you reflect on your digital habits, stay focused, and improve your efficiency.

[![Language](https://img.shields.io/badge/Language-Python-blue.svg)](https://www.python.org/)

## ✨ Overview

Do you often end your day feeling busy but unsure of where your time actually went? ScreenMentor is designed to solve this problem. It will:

1.  Silently record your screen activity in the background.
2.  Periodically compile these screenshots and send them to a powerful vision AI model for analysis.
3.  Generate a **summary, reflection, and set of recommendations** about your work during that period in an encouraging and guiding tone.
4.  Ultimately, help you build better work habits and focus your energy on what matters most.

---

## 🚀 Key Features

* **💻 Cross-Platform & Multi-Monitor Support**: Automatically captures all connected displays at regular intervals, providing a complete record of your workspace.
* **⚙️ Highly Configurable**: You can freely set the screenshot frequency, the AI analysis interval, and the specific AI model to be used.
* **🖼️ Smart Image Processing**: Screenshots are automatically downscaled and stitched into a single vertical image, saving resources and simplifying the analysis.
* **🧠 Flexible AI Integration**: Easily connect to any image-input-capable AI model API (like OpenAI's GPT-4V, Gemini Pro Vision, etc.) just by changing the configuration.
* **📂 Automated File Management**:
    * Automatically creates and manages a screenshot folder (`activity_logs`) and a reports folder (`analysis_reports`).
    * Temporary screenshots are deleted after each analysis to keep the project directory clean.
    * AI-generated analysis reports are permanently saved as timestamped `.txt` files in the `analysis_reports` folder.
* **✍️ Instant Feedback**: After each analysis, the latest report is automatically opened with your system's default text editor, giving you immediate insights.

---

## 🔧 How It Works

The script's logic is simple and straightforward:

1.  **Start a Monitoring Cycle** (e.g., every 2 minutes).
2.  **Capture Screenshots Periodically** (e.g., capture all screens every 10 seconds).
3.  **Process Images at Cycle End**: All screenshots from the cycle are stitched together vertically into a single composite image.
4.  **Call AI for Analysis**: The composite image is sent to your configured AI model.
5.  **Save and Open Report**: The AI's response is saved as a `.txt` file and opened automatically.
6.  **Clean Up Temporary Files**: The individual screenshots and the composite image from the cycle are deleted.
7.  **Repeat**: The next monitoring cycle begins.

---

## 🛠️ Getting Started

### 1. Prerequisites

* Python 3.6+

### 2. Installation

1.  **Clone this repository**
    ```bash
    git clone [https://github.com/XiaoyuZhuang/ScreenMentor.git](https://github.com/XiaoyuZhuang/ScreenMentor.git)
    cd ScreenMentor
    ```

2.  **Install dependencies**
    ```bash
    pip install mss Pillow requests
    ```

### 3. Configuration

Open the Python script file in the project (e.g., `screen_mentor.py`) and modify the **user configuration section** at the top:

```python
# --- User Configuration ---
# AI Service Configuration
API_KEY = "YOUR_API_KEY"  # Replace with your API key
BASE_URL = "YOUR_AI_API_BASE_URL" # Replace with your API endpoint
AI_MODEL = "gpt-5-mini" # Replace with the model name you want to use

# Functional Configuration
SCREENSHOT_INTERVAL_SECONDS = 10  # Interval in seconds for taking screenshots
ANALYSIS_INTERVAL_MINUTES = 2     # Interval in minutes for running analysis
RESIZE_FACTOR = 0.5               # Screenshot resize factor (0.5 means half the width and height)
# --- End of Configuration ---
```
* `API_KEY`: Your secret key from your AI service provider.
* `BASE_URL`: The API endpoint for your AI service.
* `AI_MODEL`: The specific model name you wish to use.
* Other parameters can be adjusted to suit your preferences.

### 4. Running

Once configured, simply run the script from your terminal:

```bash
python screen-ai.py
```

The program will start capturing screenshots in the background. After each analysis cycle, the report will pop up automatically. To stop the program, press `Ctrl + C` in the terminal window where the script is running.

---

## 📁 File Structure

After running, your project folder will be organized as follows:

```
/ScreenMentor
├── screen_mentor.py     <-- Your Python script
├── README.md
├── activity_logs/       <-- Temporary storage for screenshots (auto-cleaned)
└── analysis_reports/    <-- Permanent storage for AI analysis reports
    └── report_xxxxxxxx_xxxxxx.txt
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit an Issue or Pull Request to improve this project.

## 📄 License

This project is licensed under the [MIT License](LICENSE).
