import requests
import re
import os
from flask import Flask, request

app = Flask(__name__)

# 🔐 PUT YOUR NEW TOKEN HERE (REGENERATE FIRST)
TOKEN = "1952280080:AAE1jKGdPbFtOklxyd2DzAdRRuhMfvDlgQI"
RHASH = "ca7875208a06d7"

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"


# ===============================
# Get Clean Headline From Website
# ===============================
def get_headline(url):
    try:
        res = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        title = re.search(r"<title>(.*?)</title>", res.text, re.I)

        if title:
            clean = title.group(1).split("-")[0].strip()
            return clean

        return "Wararka Ciyaaraha"

    except Exception as e:
        print("Headline Error:", e)
        return "Wararka Ciyaaraha"


# ===============================
# Telegram Webhook Route
# ===============================
@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_update():

    update = request.get_json()

    msg = update.get("channel_post") or update.get("message")

    if not msg:
        return "OK", 200

    if "text" not in msg:
        return "OK", 200

    text = msg["text"]
    chat_id = msg["chat"]["id"]
    message_id = msg["message_id"]

    # Detect Kooxda link
    match = re.search(r"https://kooxda\.com/\S+", text)

    if not match:
        return "OK", 200

    # Avoid re-edit loop
    if "t.me/iv?" in text:
        return "OK", 200

    original_url = match.group(0)

    # Get headline
    title = get_headline(original_url)

    # Create Instant View link
    iv_link = f"https://t.me/iv?url={original_url}&rhash={RHASH}"

    # Final edited message format
    new_text = f"<b>{title}</b>\n\n{iv_link}"

    # Edit message
    requests.post(
        f"{TELEGRAM_API}/editMessageText",
        json={
            "chat_id": chat_id,
            "message_id": message_id,
            "text": new_text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
    )

    return "OK", 200


# ===============================
# Webhook Setup Route
# ===============================
@app.route("/")
def set_webhook():

    webhook_url = f"https://{request.host}/{TOKEN}"

    requests.get(
        f"{TELEGRAM_API}/setWebhook",
        params={"url": webhook_url}
    )

    return "Webhook Set Successfully!", 200


# ===============================
# Run (Local Only)
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)