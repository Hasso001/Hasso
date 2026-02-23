import requests
import re
import logging
from flask import Flask, request

# Logging setup for Koyeb console
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = Flask(__name__)

# Bot Config
TOKEN = "1952280080:AAHREEZV5XK_nbiPCbZ-dhpu5yzNUDyCqo8"
RHASH = "ca7875208a06d7"
API = f"https://api.telegram.org/bot{TOKEN}"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    
    # Skip edited posts to prevent infinite loops
    if "edited_channel_post" in update or "channel_post" not in update:
        return "OK", 200

    msg = update["channel_post"]
    text = msg.get("text", "")
    chat_id = msg["chat"]["id"]
    message_id = msg["message_id"]

    # Match kooxda.com links
    match = re.search(r"https://kooxda\.com/\S+", text)
    if not match or "t.me/iv?" in text:
        return "OK", 200

    original_url = match.group(0)

    # Clean the title by removing the link and domain
    clean_title = text.replace(original_url, "").replace("- Kooxda.com", "").replace("Kooxda.com", "").strip()
    if not clean_title:
        return "OK", 200

    # Hidden IV link trick
    iv_link = f"https://t.me/iv?url={original_url}&rhash={RHASH}"
    invisible_link = f'<a href="{iv_link}">\u200b</a>'

    # Insert invisible link between the first and second word
    words = clean_title.split(" ", 1)
    new_text = f"{words[0]}{invisible_link} {words[1]}" if len(words) > 1 else f"{clean_title}{invisible_link}"

    # EDIT the message instantly
    try:
        requests.post(f"{API}/editMessageText", json={
            "chat_id": chat_id,
            "message_id": message_id,
            "text": f"<b>{new_text}</b>", # Added <b> for bold
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        })
    except Exception as e:
        logging.error(f"Edit failed: {e}")

    return "OK", 200

@app.route("/")
def set_webhook():
    # Automatically links Telegram to your Koyeb URL
    webhook_url = f"https://{request.host}/{TOKEN}"
    requests.get(f"{API}/setWebhook", params={"url": webhook_url})
    return "Webhook Set Successfully!", 200

if __name__ == "__main__":
    # Must use port 8000 for Koyeb
    app.run(host="0.0.0.0", port=8000)
