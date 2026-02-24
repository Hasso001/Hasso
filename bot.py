import requests
import re
import logging
from flask import Flask, request

# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app = Flask(__name__)

# -----------------------------
# Bot Config
# -----------------------------
TOKEN = "1952280080:AAHREEZV5XK_nbiPCbZ-dhpu5yzNUDyCqo8"  # Replace with your Telegram bot token
RHASH = "ca7875208a06d7"
API = f"https://api.telegram.org/bot{TOKEN}"

# -----------------------------
# Webhook Receiver
# -----------------------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    
    # 🚫 Ignore edited messages to prevent loop
    if "edited_channel_post" in update:
        return "OK", 200

    if "channel_post" not in update:
        return "OK", 200

    msg = update["channel_post"]
    if "text" not in msg:
        return "OK", 200

    text = msg["text"]
    chat_id = msg["chat"]["id"]
    message_id = msg["message_id"]

    # Only process kooxda.com links
    match = re.search(r"https://kooxda\.com/\S+", text)
    if not match:
        return "OK", 200

    original_url = match.group(0)

    # Remove link from visible text
    clean_title = text.replace(original_url, "").replace("- Kooxda.com", "").replace("Kooxda.com", "").strip()
    if not clean_title:
        return "OK", 200

    # -----------------------------
    # Hidden IV link for Instant View
    # -----------------------------
    iv_link = f"https://t.me/iv?url={original_url}&rhash={RHASH}"
    invisible_link = f'<a href="{iv_link}">\u200b</a>'

    # Insert hidden link in first space only
    words = clean_title.split(" ", 1)
    if len(words) > 1:
        new_text = words[0] + invisible_link + " " + words[1]
    else:
        new_text = clean_title + invisible_link

    # -----------------------------
    # Edit the message instantly
    # -----------------------------
    try:
        resp_edit = requests.post(
            f"{API}/editMessageText",
            json={
                "chat_id": chat_id,
                "message_id": message_id,
                "text": new_text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False  # triggers IV preview
            }
        )
        logging.info(f"Message edited instantly: {resp_edit.json()}")
    except Exception as e:
        logging.error(f"Failed to edit message: {e}")

    return "OK", 200

# -----------------------------
# Webhook setup route
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
# Optional local run
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)