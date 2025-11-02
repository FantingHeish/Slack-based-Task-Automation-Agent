import os
import json
import requests
import pandas as pd
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime
from io import StringIO

import gradio as gr

# === CONFIG ===
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_USER_ID = os.getenv("SLACK_USER_ID")
SLACK_CHANNEL = SLACK_USER_ID
SLACK_CLIENT = WebClient(token=SLACK_BOT_TOKEN) if SLACK_BOT_TOKEN else None

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")

GOOGLE_SHEET_PATH = "sheet.csv"
MAX_MSG_LENGTH = 3500

# === UTILS ===
def chunk_text(text, max_length=MAX_MSG_LENGTH):
    """將長文本分割成多個較短的片段"""
    chunks = []
    while len(text) > max_length:
        split_index = text[:max_length].rfind('\n')
        if split_index == -1:
            split_index = max_length
        chunks.append(text[:split_index])
        text = text[split_index:].lstrip('\n')
    if text:
        chunks.append(text)
    return chunks

def send_to_slack(text, filename="task_summary.txt"):
    """發送訊息到 Slack（分段 + 檔案）"""
    if not SLACK_CLIENT:
        return "Slack 未設定，無法發送訊息"
    
    try:
        # 分段發送訊息
        for part in chunk_text(text):
            SLACK_CLIENT.chat_postMessage(
                channel=SLACK_CHANNEL,
                text=f"```\n{part}\n```"
            )
        
        # 上傳完整 txt 檔
        SLACK_CLIENT.files_upload_v2(
            channel=SLACK_CHANNEL,
            content=text,
            filename=filename,
            title="完整任務總結"
        )
        return "✅ 成功發送到 Slack"
    except SlackApiError as e:
        return f"Slack 發送失敗: {e.response['error']}"

# === LLM FUNCTIONS ===
def use_openai(prompt):
    """使用 OpenAI GPT-4 API（新版）"""
    if not OPENAI_API_KEY:
        return json.dumps({"error": "OpenAI API Key 未設定"})
    
    try:
        # 使用新版 OpenAI API (v1.0+)
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"error": f"OpenAI 錯誤: {str(e)}"})

def use_huggingface(prompt):
    """使用 HuggingFace Mixtral 模型"""
    if not HF_API_KEY:
        return json.dumps({"error": "HuggingFace API Key 未設定"})
    
    endpoint = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1024,
            "temperature": 0.2
        }
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            generated = result[0].get("generated_text", "")
            # 移除原始 prompt，只保留生成的部分
            if prompt in generated:
                return generated.split(prompt)[-1].strip()
            return generated
        else:
            return json.dumps({"error": "HuggingFace 模型回應格式異常"})
    except Exception as e:
        return json.dumps({"error": f"HuggingFace 錯誤: {str(e)}"})

# === MAIN PIPELINE ===
def run_pipeline(slack_messages_json, llm_mode):
    """主要流程：比對任務並生成報告"""
    
    # 檢查 Google Sheet 是否存在
    if not os.path.exists(GOOGLE_SHEET_PATH):
        return f"找不到任務清單檔案: {GOOGLE_SHEET_PATH}"
    
    try:
        df_sheet = pd.read_csv(GOOGLE_SHEET_PATH)
    except Exception as e:
        return f"讀取 Google Sheet 失敗: {str(e)}"
    
    # 解析 Slack 訊息 JSON
    try:
        slack_messages = json.loads(slack_messages_json)
        if not isinstance(slack_messages, list):
            return "Slack 訊息格式錯誤，應為 JSON 陣列"
    except json.JSONDecodeError:
        return "JSON 格式錯誤，請檢查輸入"
    
    matched = []
    unmatched = []
    
    # 處理每則訊息
    for msg in slack_messages:
        ts = msg.get("ts", "0")
        user = msg.get("user", "Unknown")
        text = msg.get("text", "")
        
        try:
            dt = datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M")
        except:
            dt = "未知時間"
        
        # 準備 AI 提示詞
        sheet_json = df_sheet.to_dict(orient="records")
        prompt = f"""你是一個任務分析助手。請判斷下列 Slack 訊息是否與任務列表中某筆任務相關。

任務列表（JSON格式）：
{json.dumps(sheet_json, ensure_ascii=False, indent=2)}

訊息內容：
{text}

判斷規則：
- 如果訊息明確提到某個任務、負責人、截止日期等相關內容，請找出對應的任務
- 如果找到對應任務，回傳該任務的 JSON 物件（包含 Task, Priority, Deadline, In-Charge）
- 如果沒有對應任務，回傳 {{"Unmatched": "訊息內容"}}

請只回傳 JSON 格式，不要有其他說明文字。"""
        
        # 選擇 LLM
        if llm_mode == "OpenAI GPT (精準語意)":
            result = use_openai(prompt)
        else:
            result = use_huggingface(prompt)
        
        # 解析 AI 回應
        try:
            # 嘗試提取 JSON（處理 markdown 格式）
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            data = json.loads(result)
            
            if "error" in data:
                unmatched.append({
                    "text": f"[AI錯誤] {data['error']}",
                    "user": user,
                    "timestamp": dt
                })
            elif "Unmatched" in data:
                unmatched.append({
                    "text": text,
                    "user": user,
                    "timestamp": dt
                })
            else:
                # 確保包含所有必要欄位
                task_data = {
                    "Task": data.get("Task", "N/A"),
                    "Priority": data.get("Priority", "N/A"),
                    "Deadline": data.get("Deadline", "N/A"),
                    "In-Charge": data.get("In-Charge", "N/A")
                }
                matched.append(task_data)
        except json.JSONDecodeError:
            unmatched.append({
                "text": text,
                "user": user,
                "timestamp": dt
            })
    
    # === 格式化報告 ===
    md = ["#任務摘要報告\n"]
    md.append(f"**分析時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md.append(f"**使用模型**: {llm_mode}\n")
    
    if matched:
        md.append("\n## 有對應 Google Sheet 任務的訊息\n")
        md.append("| Task | Priority | Deadline | In-Charge |")
        md.append("|------|----------|----------|-----------|")
        for task in matched:
            md.append(
                f"| {task['Task']} | {task['Priority']} | "
                f"{task['Deadline']} | {task['In-Charge']} |"
            )
    else:
        md.append("\n## ℹ️ 沒有找到對應的任務")
    
    if unmatched:
        md.append("\n## 沒有對應任務表的訊息\n")
        md.append("| 發送者 | 時間 | 摘要 |")
        md.append("|--------|------|------|")
        for item in unmatched:
            # 簡化摘要（取第一行，最多40字）
            first_line = item['text'].replace('\n', ' ')[:40].replace('|', '-')
            md.append(f"| {item['user']} | {item['timestamp']} | {first_line}... |")
    
    md.append(f"\n---\n**統計**: 共 {len(matched)} 則已匹配，{len(unmatched)} 則未匹配")
    
    final_text = "\n".join(md)
    
    # 發送到 Slack
    if SLACK_CLIENT:
        slack_status = send_to_slack(final_text)
        final_text += f"\n\n{slack_status}"
    else:
        final_text += "\n\n Slack 未設定，僅顯示報告內容"
    
    return final_text

# === Gradio UI ===
def main():
    # 範例資料
    example_messages = json.dumps([
        {
            "ts": str(datetime.now().timestamp()),
            "user": "U12345",
            "text": "我已經完成UI設計了，請大家review"
        },
        {
            "ts": str(datetime.now().timestamp()),
            "user": "U67890",
            "text": "今天天氣不錯"
        }
    ], ensure_ascii=False, indent=2)
    
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 📋 Slack 任務整合器
        
        自動分析 Slack 訊息並比對 Google Sheet 任務清單
        
        **功能**：
        - AI 智能語意分析
        - 自動比對任務清單
        - 整理報告發送到 Slack
        """)
        
        with gr.Row():
            with gr.Column():
                slack_input = gr.Textbox(
                    label="📥 Slack 訊息 JSON 陣列",
                    placeholder='[{"ts": "1234567890.123", "user": "U12345", "text": "訊息內容"}]',
                    value=example_messages,
                    lines=10
                )
                
                llm_mode = gr.Radio(
                    choices=[
                        "OpenAI GPT (精準語意)",
                        "HuggingFace LLM (免費節省成本)"
                    ],
                    value="OpenAI GPT (精準語意)",
                    label="🤖 選擇分析模型"
                )
                
                run_button = gr.Button("🚀 執行比對並發送報告", variant="primary")
            
            with gr.Column():
                result_box = gr.Textbox(
                    label="📊 分析結果",
                    lines=20
                )
        
        gr.Markdown("""
        ### 使用說明
        
        1. **準備資料**：確保 `sheet.csv` 在專案根目錄
        2. **輸入訊息**：貼上 Slack 訊息 JSON（或使用預設範例）
        3. **選擇模型**：GPT 更精準，HuggingFace 免費
        4. **執行分析**：點擊按鈕開始處理
        
        ### 🔑 環境變數
        
        ```bash
        SLACK_BOT_TOKEN=xoxb-your-token
        SLACK_USER_ID=U12345678
        OPENAI_API_KEY=sk-your-key
        HF_API_KEY=hf-your-key
        ```
        """)
        
        run_button.click(
            fn=run_pipeline,
            inputs=[slack_input, llm_mode],
            outputs=result_box
        )
    
    demo.launch()

if __name__ == '__main__':
    main()