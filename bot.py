import requests
import re
import logging
from flask import Flask, request

# Logging for Koyeb console troubleshooting
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = Flask(name)

# Credentials
TOKEN = "1952280080:AAHREEZV5XK_nbiPCbZ-dhpu5yzNUDyCqo8"
RHASH = "ca7875208a06d7"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    
    # We only care about channel posts
    msg = update.get("channel_post")
    if not msg or "text" not in msg:
        return "OK", 200

    text = msg["text"]
    chat_id = msg["chat"]["id"]
    message_id = msg["message_id"]

    # Match kooxda.com links
    match = re.search(r"https://kooxda\.com/\S+", text)
    if match and "t.me/iv?" not in text:
        original_url = match.group(0)

        # CLEANING: Remove the link and domain text
        clean_title = text.replace(original_url, "").replace("- Kooxda.com", "").replace("Kooxda.com", "").strip()
        if not clean_title:
            clean_title = "Wararka Ciyaaraha"

        # INVISIBLE LINK: Zero-width space trick for Instant View
        iv_link = f"https://t.me/iv?url={original_url}&rhash={RHASH}"
        invisible_char = "\u200b"
        
        # Format: Bold title with hidden link
        final_text = f'<b><a href="{iv_link}">{invisible_char}</a>{clean_title}</b>'

        # EDIT: Modify original post
        try:
            requests.post(f"{API_URL}/editMessageText", json={
                "chat_id": chat_id,
                "message_id": message_id,
                "text": final_text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            })
        except Exception as e:
            logging.error(f"Edit failed: {e}")

    return "OK", 200

@app.route("/")
def index():
    # Trigger this by visiting your app URL
    webhook_url = f"https://{request.host}/{TOKEN}"
    response = requests.get(f"{API_URL}/setWebhook", params={
        "url": webhook_url,
        "drop_pending_updates": True
    })
    return f"Setup Result: {response.json()}", 200

if name == "main":
    # Koyeb requires port 8000
    app.run(host="0.0.0.0", port=8000)