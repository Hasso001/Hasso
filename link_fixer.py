import os
import requests
import re

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RHASH = os.getenv('RHASH')
DOMAIN = "kooxda.com"

def fix_history():
    # This checks the last 20 messages in your channel
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url).json()

    if not response.get("ok"):
        print("Telegram error")
        return

    for update in response.get("result", []):
        post = update.get("channel_post")
        if not post or "text" not in post:
            continue

        msg_text = post["text"]
        msg_id = post["message_id"]

        pattern = rf'https?://{DOMAIN}/\S+'
        match = re.search(pattern, msg_text)

        if match and "rhash=" not in msg_text:
            original_url = match.group(0)
            iv_link = f"https://t.me/iv?url={original_url}&rhash={RHASH}"
            new_text = msg_text.replace(original_url, iv_link)

            edit_url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
            requests.post(edit_url, data={
                "chat_id": CHAT_ID,
                "message_id": msg_id,
                "text": new_text,
                "parse_mode": "HTML"
            })
            print(f"Fixed message {msg_id}")

if __name__ == "__main__":
    fix_history()
