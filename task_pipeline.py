import os, json, pandas as pd
from datetime import datetime
from config import GOOGLE_SHEET_PATH
from slack_utils import send_to_slack
from llm_utils import use_openai, use_huggingface

def run_pipeline(slack_messages_json, llm_mode):
    if not os.path.exists(GOOGLE_SHEET_PATH):
        return f"找不到任務清單檔案: {GOOGLE_SHEET_PATH}"
    
    try:
        df_sheet = pd.read_csv(GOOGLE_SHEET_PATH)
    except Exception as e:
        return f"讀取 Google Sheet 失敗: {str(e)}"
    
    try:
        slack_messages = json.loads(slack_messages_json)
        if not isinstance(slack_messages, list):
            return "Slack 訊息格式錯誤"
    except json.JSONDecodeError:
        return "JSON 格式錯誤"

    matched, unmatched = [], []
    for msg in slack_messages:
        text = msg.get("text", "")
        ts = msg.get("ts", "0")
        user = msg.get("user", "Unknown")
        dt = datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M")
        
        prompt = f"""你是一個任務分析助手。請判斷下列 Slack 訊息是否與任務列表中某筆任務相關。
任務列表：{df_sheet.to_json(orient='records', force_ascii=False, indent=2)}
訊息內容：{text}
"""
        result = use_openai(prompt) if "OpenAI" in llm_mode else use_huggingface(prompt)
        # 解析結果（略，同妳原本版本）
        # ...
