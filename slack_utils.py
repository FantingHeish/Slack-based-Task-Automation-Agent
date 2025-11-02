from slack_sdk.errors import SlackApiError
from config import SLACK_CLIENT, SLACK_CHANNEL, MAX_MSG_LENGTH

def chunk_text(text, max_length=MAX_MSG_LENGTH):
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
    if not SLACK_CLIENT:
        return "Slack 未設定，無法發送訊息"
    
    try:
        for part in chunk_text(text):
            SLACK_CLIENT.chat_postMessage(
                channel=SLACK_CHANNEL,
                text=f"```\n{part}\n```"
            )
        
        SLACK_CLIENT.files_upload_v2(
            channel=SLACK_CHANNEL,
            content=text,
            filename=filename,
            title="完整任務總結"
        )
        return "✅ 成功發送到 Slack"
    except SlackApiError as e:
        return f"Slack 發送失敗: {e.response['error']}"