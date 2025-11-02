# Slack-based-Task-Automation-Agent
以 LLM（大型語言模型）驅動的 Slack 任務整合系統，自動擷取頻道與私訊內容、比對 Google Sheets 任務清單，並自動生成結構化的任務報告，提升團隊工作追蹤與協作效率。

## 專案簡介
在企業或團隊的 Slack 溝通中，任務訊息常分散在不同頻道與私訊中，導致追蹤困難與資訊遺漏。  
本專案透過整合 **Slack API、OpenAI / HuggingFace LLM、Google Cloud API**，  
自動完成以下流程：

1. 擷取 Slack 頻道與私訊內容  
2. 以 LLM 模型分析訊息語意、辨識任務內容  
3. 與 Google Sheets 任務清單比對（確認負責人、進度、截止時間）  
4. 自動生成 Markdown 格式任務報告  
5. 將結果回傳至 Slack（訊息 + 附件檔案）

## 架構

```mermaid
flowchart TD
    A[Slack Channels & DMs] --> B[Slack API]
    B --> C[LLM 任務分類器 (Prompt-driven Retrieval)]
    C --> D[Google Sheets API]
    D --> E[比對與報告生成 (JSON → Markdown)]
    E --> F[回傳至 Slack]
技術架構
主要語言：Python
開發框架：Gradio（Web 介面）
雲端串接：
Slack SDK, Google Cloud Platform / Google Sheets API

模型支援：
OpenAI GPT-4（高精度語意理解）, HuggingFace Mixtral（節省 API 成本）

專案檔案說明
檔案	功能說明
app.py	主入口（Gradio 介面）
task_pipeline.py	核心任務分析與比對流程
llm_utils.py	LLM 模型整合（OpenAI / HF）
slack_utils.py	Slack 訊息傳遞與上傳模組
config.py	系統設定與環境變數管理
sheet.csv	Google Sheets 任務匯出範例
.env.example	範例環境設定檔
requirements.txt	套件需求清單
