import requests, re, logging
from flask import Flask, request

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# Credentials
TOKEN = "1952280080:AAHREEZV5XK_nbiPCbZ-dhpu5yzNUDyCqo8"
RHASH = "ca7875208a06d7"
API = f"https://api.telegram.org/bot{TOKEN}"

@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    # Check for channel post
    msg = update.get("channel_post") or update.get("message")
    
    if msg and "text" in msg:
        text = msg["text"]
        chat_id = msg["chat"]["id"]
        message_id = msg["message_id"]

        # If it's a kooxda link, edit it
        if "kooxda.com" in text and "t.me/iv?" not in text:
            # Simple cleaning for testing
            clean_title = text.replace("https://kooxda.com/", "").replace("/", " ").strip()
            iv_url = f"https://t.me/iv?url={text.strip()}&rhash={RHASH}"
            
            # The simplest possible edit
            requests.post(f"{API}/editMessageText", json={
                "chat_id": chat_id,
                "message_id": message_id,
                "text": f'<b><a href="{iv_url}">\u200b</a>{clean_title}</b>',
                "parse_mode": "HTML"
            })
    return "OK", 200

@app.route('/')
def home():
    # Force Telegram to look at this Koyeb URL
    webhook_url = f"https://{request.host}/{TOKEN}"
    r = requests.get(f"{API}/setWebhook", params={"url": webhook_url, "drop_pending_updates": True})
    return f"Status: {r.json()}", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
