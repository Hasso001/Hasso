import os
import requests
import re

# These come from the "Secrets" you just added
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RHASH = os.getenv('RHASH')
DOMAIN = "kooxda.com"

def fix_links():
    # 1. Look for the most recent posts in the channel
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url).json()

    if not response.get("ok"):
        print("Could not connect to Telegram")
        return

    for item in response.get("result", []):
        post = item.get("channel_post")
        if not post or "text" not in post:
            continue

        text = post["text"]
        msg_id = post["message_id"]

        # 2. Find links that need the Instant View rhash
        pattern = rf'https?://{DOMAIN}/\S+'
        match = re.search(pattern, text)

        if match and "rhash=" not in text:
            original_url = match.group(0)
            # This creates the special Instant View link
            iv_link = f"https://t.me/iv?url={original_url}&rhash={RHASH}"
            new_text = text.replace(original_url, iv_link)

            # 3. Edit the post to add the Instant View button
            edit_url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
            requests.post(edit_url, data={
                "chat_id": CHAT_ID,
                "message_id": msg_id,
                "text": new_text
            })
            print(f"Success! Fixed message {msg_id}")

if __name__ == "__main__":
    fix_links()
  
