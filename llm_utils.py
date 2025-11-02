import json, requests
from openai import OpenAI
from config import OPENAI_API_KEY, HF_API_KEY

def use_openai(prompt):
    if not OPENAI_API_KEY:
        return json.dumps({"error": "OpenAI API Key 未設定"})
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return res.choices[0].message.content
    except Exception as e:
        return json.dumps({"error": f"OpenAI 錯誤: {str(e)}"})

def use_huggingface(prompt):
    if not HF_API_KEY:
        return json.dumps({"error": "HuggingFace API Key 未設定"})
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 1024, "temperature": 0.2}}
    try:
        res = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1",
            headers=headers, json=payload, timeout=30)
        result = res.json()
        if isinstance(result, list) and len(result) > 0:
            generated = result[0].get("generated_text", "")
            return generated.split(prompt)[-1].strip() if prompt in generated else generated
        else:
            return json.dumps({"error": "HuggingFace 模型回應格式異常"})
    except Exception as e:
        return json.dumps({"error": f"HuggingFace 錯誤: {str(e)}"})
