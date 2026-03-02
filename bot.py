import requests, re, logging
from flask import Flask, request

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# Your verified credentials
TOKEN = "1952280080:AAHREEZV5XK_nbiPCbZ-dhpu5yzNUDyCqo8"
RHASH = "ca7875208a06d7"
API = f"https://api.telegram.org/bot{TOKEN}"

@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    msg = update.get("channel_post") or update.get("message")
    
    if msg and "text" in msg:
        text = msg["text"]
        chat_id = msg["chat"]["id"]
        message_id = msg["message_id"]

        # 1. Match the link
        match = re.search(r"https://kooxda\.com/\S+", text)
        if match and "t.me/iv?" not in text:
            url = match.group(0)

            # 2. Clean the title text
            clean_title = text.replace(url, "").replace("- Kooxda.com", "").replace("Kooxda.com", "").strip()
            if not clean_title:
                clean_title = "Wararka Ciyaaraha"

            # 3. Create the IV link
            iv_link = f"https://t.me/iv?url={url}&rhash={RHASH}"
            
            # THE FIX: We wrap the invisible character (\u200b) in the link 
            # and place it at the VERY START to force the Instant View button.
            final_text = f'<a href="{iv_link}">\u200b</a><b>{clean_title}</b>'

            # 4. Edit with preview ENABLED
            requests.post(f"{API}/editMessageText", json={
                "chat_id": chat_id,
                "message_id": message_id,
                "text": final_text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False  # This MUST be False for the button to show
            })
    return "OK", 200

@app.route('/')
def home():
    webhook_url = f"https://{request.host}/{TOKEN}"
    requests.get(f"{API}/setWebhook", params={"url": webhook_url, "drop_pending_updates": True})
    return "Bot is Active!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
