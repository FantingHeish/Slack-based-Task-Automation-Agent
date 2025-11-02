# Slack-based-Task-Automation-Agent
## 專案簡介
此專案是一個整合 **Slack、Google Sheets、與大型語言模型（LLM）** 的自動化任務整理系統。  
使用者可從 Gradio 介面一鍵執行，Agent 會：
1. 抓取指定 Slack Workspace 的訊息（含頻道與私訊）。  
2. 自動分析訊息內容、發送者、截止日期、負責人。  
3. 將結果與 Google Sheets 任務清單比對，分類為「已登錄任務」與「未登錄任務」。  
4. 以 Markdown 表格格式回傳至使用者的 Slack 私訊，並可自動上傳 `.txt` 報告檔。

## 技術架構
| 類別         | 技術 / 套件                                           | 功能描述            |
| ---------- | ------------------------------------------------- | --------------- |
| **Backend** |  Python 3.10+, Slack SDK, Google Sheets API        | 抓取訊息、任務比對       |
| **LLM 模型** |  OpenAI GPT / HuggingFace Mistral-7B / ChatGLM3-6B | 自然語言理解與比對任務     |
| Interface  | Gradio                                            | 前端 Web 介面，一鍵執行  |
| Output     | Slack Bot + `.txt` file                           | 自動上傳整理結果至 Slack |
| Deployment | Hugging Face Space                                | 提供固定網址、雲端執行環境   |


## 架構圖
```mermaid
flowchart TD
    A["Gradio UI"] --> B["Slack Agent"]

    %% Slack 處理路徑
    B --> C["Fetch Slack messages"]
    C --> D["Preprocess to JSON"]
    D --> E["LLM Task Classifier"]

    %% Google Sheet 並行路徑
    B --> S["Load Google Sheet tasks"]

    %% 匯流點
    E --> F{"Sheet available?"}
    S --> F

    %% Decision 分支
    F -- Yes --> G["Task Matcher: existing vs new"]
    F -- No --> R["Report Builder: unmatched only"]

    %% 後續流程
    G --> H["Update or mark new"]
    H --> R["Report Builder"]
    R --> U["Slack Sender"]
    U --> V["User receives report"]

 ```

### 檔案說明
- `config.py`： 儲存系統設定與環境變數管理
- `llm_utils.py`： 整合 LLM 模型介面，支援 OpenAI GPT-4 與 Hugging Face 模型呼叫
- `slack_utils.py`： 負責與 Slack API 溝通，包括訊息擷取、分段上傳與檔案傳送
- `task_pipeline.py`： 核心流程模組：將 Slack 訊息比對 Google Sheet 任務清單並生成報告
- `ui.py`： 建立 Gradio Web 介面，讓使用者可上傳 Slack JSON、選擇模型並一鍵執行
- `slack_agent.py`： 主執行入口，串接 UI 與 pipeline，整合 LLM 模組與 Slack 回傳

