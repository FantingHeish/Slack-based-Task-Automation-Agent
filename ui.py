import gradio as gr
import json
from datetime import datetime
from task_pipeline import run_pipeline

def main():
    example_messages = json.dumps([
        {"ts": str(datetime.now().timestamp()), "user": "U123", "text": "完成UI設計，請review"},
        {"ts": str(datetime.now().timestamp()), "user": "U456", "text": "今天天氣不錯"}
    ], ensure_ascii=False, indent=2)
    
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 📋 Slack 任務整合器")
        slack_input = gr.Textbox(label="Slack 訊息 JSON", value=example_messages, lines=10)
        llm_mode = gr.Radio(["OpenAI GPT (精準語意)", "HuggingFace LLM (免費)"], value="OpenAI GPT (精準語意)")
        result_box = gr.Textbox(label="分析結果", lines=20)
        run_button = gr.Button("🚀 執行比對並發送報告", variant="primary")
        run_button.click(fn=run_pipeline, inputs=[slack_input, llm_mode], outputs=result_box)
    demo.launch()

if __name__ == "__main__":
    main()
