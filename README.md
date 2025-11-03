<img width="1913" height="991" alt="Gradio UI" src="https://github.com/user-attachments/assets/74d99b74-169b-4eaf-9afd-1afacb49900c" /># Slack-based-Task-Automation-Agent
## 專案簡介
此專案是一個整合 **Slack、Google Cloud Sheets、與大型語言模型（LLM）** 的自動化任務整理系統。  
使用者可從 Gradio 介面一鍵執行，Agent 會：
1. 抓取指定 Slack Workspace 的訊息。  
2. 分析並整理訊息內容、發送者、截止日期、負責人。  
3. 比對Google cloud sheet任務，整理生成任務清單。
5. 回傳至使用者 Slack 私訊，並寄送郵件，另外可以附加任務sheet。

## 技術架構
| 類別         | 技術 / 套件                                           | 功能描述            |
| ---------- | ------------------------------------------------- | --------------- |
| **Backend** |  Python 3.10+, Slack SDK, Google Sheets API        | 抓取訊息、任務比對       |
| **LLM 模型** |  OpenAI GPT / HuggingFace Mistral-7B / ChatGLM3-6B | 自然語言理解與比對任務     |
| **Interface**  | Gradio                                            | 前端 Web 介面，一鍵執行  |
| **Output**     | Slack Bot + `.txt` file                           | 自動上傳整理結果至 Slack |
| **Deployment** | Hugging Face Space                                | 提供固定網址、雲端執行環境   |


## 架構圖

![Gradio UI](https://github.com/user-attachments/assets/761e5110-acb1-433b-8960-d977325fe8b2)

### 檔案說明
- `config.py`： 儲存系統設定與環境變數管理
- `llm_utils.py`： 整合 LLM 模型介面，支援 OpenAI GPT-4 與 Hugging Face 模型呼叫
- `slack_utils.py`： 負責與 Slack API 溝通，包括訊息擷取、分段上傳與檔案傳送
- `task_pipeline.py`： 核心流程模組：將 Slack 訊息比對 Google Sheet 任務清單並生成報告
- `ui.py`： 建立 Gradio Web 介面，讓使用者可上傳 Slack JSON、選擇模型並一鍵執行
- `slack_agent.py`： 主執行入口，串接 UI 與 pipeline，整合 LLM 模組與 Slack 回傳

