import os
from slack_sdk import WebClient

# === CONFIG ===
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_USER_ID = os.getenv("SLACK_USER_ID")
SLACK_CHANNEL = SLACK_USER_ID
SLACK_CLIENT = WebClient(token=SLACK_BOT_TOKEN) if SLACK_BOT_TOKEN else None

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")

GOOGLE_SHEET_PATH = "sheet.csv"
MAX_MSG_LENGTH = 3500