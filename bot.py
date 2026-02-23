import requests
import re
import logging
from flask import Flask, request

# Logging helps you see what's happening in the Koyeb 'Console' tab
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = Flask(__name__)

# Credentials - Hardcoded for maximum reliability on Koyeb
TOKEN = "1952280080:AAHREEZV5XK_nbiPCbZ-dhpu5yzNUDyCqo8"
RHASH = "ca7875208a06d7"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    
    # We look for channel posts (for your channel) or regular messages (for testing)
    msg = update.get("channel_post") or update.get("message")
    
    if msg and "text" in msg:
        text = msg["text"]
        chat_id = msg["chat"]["id"]
        message_id = msg["message_id"]

        # Only process if it's a kooxda.com link and hasn't been processed yet
        match = re.search(r"https://kooxda\.com/\S+", text)
        if match and "t.me/iv?" not in text:
            original_url = match.group(0)

            # CLEANING: Remove the link and domain names from the visible text
            clean_title = text.replace(original_url, "").replace("- Kooxda.com", "").replace("Kooxda.com", "").strip()
            
            # If the user only sent a link, we need a fallback title
            if not clean_title:
                clean_title = "Wararka Ciyaaraha"

            # INSTANT VIEW: Create the hidden link
            iv_link = f"https://t.me/iv?url={original_url}&rhash={RHASH}"
            invisible_char = "\u200b" # Zero-width space
            
            # Form the final text: Bold headline with the link hidden inside the first character
            # This triggers Instant View but hides the URL and the domain name
            final_text = f'<b><a href="{iv_link}">{invisible_char}</a>{clean_title}</b>'

            # THE EDIT: Transform the existing post instantly
            try:
                requests.post(f"{API_URL}/editMessageText", json={
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "text": final_text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False # Must be False to show Instant View
                })
                logging.info(f"Successfully edited message {message_id}")
            except Exception as e:
                logging.error(f"Failed to edit message: {e}")

    return "OK", 200

@app.route("/")
def index():
    # SET WEBHOOK: This tells Telegram to send messages to your Koyeb URL
    # drop_pending_updates=True clears all 'stuck' messages that were causing headaches
    webhook_url = f"https://{request.host}/{TOKEN}"
    response = requests.get(f"{API_URL}/setWebhook", params={
        "url": webhook_url,
        "drop_pending_updates": True
    })
    return f"Setup Result: {response.json()}", 200

if __name__ == "__main__":
    # Port 8000 is required for Koyeb health checks
    app.run(host="0.0.0.0", port=8000)
