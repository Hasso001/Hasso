import requests
import re
from flask import Flask, request

app = Flask(__name__)

# 🔐 PUT YOUR NEW TOKEN HERE
TOKEN = "1952280080:AAE1jKGdPbFtOklxyd2DzAdRRuhMfvDlgQI"
RHASH = "ca7875208a06d7"

API = f"https://api.telegram.org/bot{TOKEN}"


# ==========================
# Get Headline From Website
# ==========================
def get_headline(url):
    try:
        res = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        title = re.search(r"<title>(.*?)</title>", res.text, re.I)

        if title:
            return title.group(1).split("-")[0].strip()

        return "Wararka Ciyaaraha"

    except Exception as e:
        print("Headline Error:", e)
        return "Wararka Ciyaaraha"


# ==========================
# Telegram Webhook Receiver
# ==========================
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():

    update = request.get_json()

    msg = update.get("channel_post") or update.get("message")

    if not msg:
        return "OK", 200

    if "text" not in msg:
        return "OK", 200

    text = msg["text"]
    chat_id = msg["chat"]["id"]
    message_id = msg["message_id"]

    # Avoid re-processing
    if "t.me/iv?" in text:
        return "OK", 200

    # Detect Kooxda link
    match = re.search(r"https://kooxda\.com/\S+", text)

    if not match:
        return "OK", 200

    original_url = match.group(0)

    # Get clean title
    title = get_headline(original_url)

    # Create Instant View link
    iv_link = f"https://t.me/iv?url={original_url}&rhash={RHASH}"

    # 1️⃣ Delete original message
    requests.post(
        f"{API}/deleteMessage",
        json={
            "chat_id": chat_id,
            "message_id": message_id
        }
    )

    # 2️⃣ Send new formatted message
    requests.post(
        f"{API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": f"<b>{title}</b>\n\n{iv_link}",
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
    )

    return "OK", 200


# ==========================
# Webhook Setup Route
# ==========================
@app.route("/")
def set_webhook():

    webhook_url = f"https://{request.host}/{TOKEN}"

    requests.get(
        f"{API}/setWebhook",
        params={"url": webhook_url}
    )

    return "Webhook Set!", 200


# ==========================
# Local Run (Optional)
# ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)