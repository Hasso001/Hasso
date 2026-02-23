import requests
import re
import logging
from flask import Flask, request

# -----------------------------
# Logging Setup
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app = Flask(__name__)

# -----------------------------
# Bot Config
# -----------------------------
TOKEN = "1952280080:AAHREEZV5XK_nbiPCbZ-dhpu5yzNUDyCqo8"  # <- Replace with your new token
RHASH = "ca7875208a06d7"
API = f"https://api.telegram.org/bot{TOKEN}"


# -----------------------------
# Get headline from website
# -----------------------------
def get_headline(url):
    try:
        logging.info(f"Fetching headline for: {url}")
        res = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        title = re.search(r"<title>(.*?)</title>", res.text, re.I)
        if title:
            clean_title = title.group(1).strip()
            logging.info(f"Raw headline found: {clean_title}")
            return clean_title
        logging.warning("No title found, using default")
        return "Wararka Ciyaaraha"
    except Exception as e:
        logging.error(f"Error fetching headline: {e}")
        return "Wararka Ciyaaraha"


# -----------------------------
# Telegram Webhook Receiver
# -----------------------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    logging.info(f"Update received: {update}")

    msg = update.get("channel_post") or update.get("message")
    if not msg:
        logging.info("No message found in update.")
        return "OK", 200
    if "text" not in msg:
        logging.info("Message has no text, ignoring.")
        return "OK", 200

    text = msg["text"]
    chat_id = msg["chat"]["id"]
    message_id = msg["message_id"]

    # Prevent infinite loop
    if "t.me/iv?" in text:
        logging.info("Message already contains IV link, ignoring.")
        return "OK", 200

    # Detect kooxda.com link
    match = re.search(r"https://kooxda\.com/\S+", text)
    if not match:
        logging.info("No kooxda.com link found, ignoring.")
        return "OK", 200

    original_url = match.group(0)
    title = get_headline(original_url)

    # -----------------------------
    # Clean headline text
    # -----------------------------
    clean_title = title.replace("- Kooxda.com", "").replace("Kooxda.com", "").strip()

    # -----------------------------
    # Embed invisible IV link in spaces
    # -----------------------------
    iv_link = f"https://t.me/iv?url={original_url}&rhash={RHASH}"
    invisible_link = f'<a href="{iv_link}">\u200b</a>'
    # Inject invisible link after each space
    new_text = clean_title.replace(" ", f" {invisible_link} ")

    # -----------------------------
    # Delete original message
    # -----------------------------
    try:
        resp_del = requests.post(
            f"{API}/deleteMessage",
            json={"chat_id": chat_id, "message_id": message_id}
        )
        logging.info(f"Delete message response: {resp_del.json()}")
    except Exception as e:
        logging.error(f"Failed to delete message: {e}")

    # -----------------------------
    # Send new formatted message
    # -----------------------------
    try:
        resp_send = requests.post(
            f"{API}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": new_text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }
        )
        logging.info(f"Send message response: {resp_send.json()}")
    except Exception as e:
        logging.error(f"Failed to send message: {e}")

    return "OK", 200


# -----------------------------
# Webhook Setup Route
# -----------------------------
@app.route("/")
def set_webhook():
    webhook_url = f"https://{request.host}/{TOKEN}"
    try:
        resp = requests.get(
            f"{API}/setWebhook",
            params={"url": webhook_url}
        )
        logging.info(f"Webhook set response: {resp.json()}")
    except Exception as e:
        logging.error(f"Failed to set webhook: {e}")
    return "Webhook Set!", 200


# -----------------------------
# Local Run (Optional)
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)