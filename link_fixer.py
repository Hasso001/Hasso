import os
import requests
import re

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RHASH = os.getenv('RHASH')
DOMAIN = "kooxda.com"

def fix_links():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url, params={"allowed_updates": ["channel_post"]}).json()

    if not response.get("ok"): return

    for update in response.get("result", []):
        post = update.get("channel_post")
        if not post or "text" not in post: continue

        msg_text = post["text"]
        msg_id = post["message_id"]

        pattern = rf'https?://{DOMAIN}/\S+'
        match = re.search(pattern, msg_text)

        if match and "t.me/iv?" not in msg_text:
            original_url = match.group(0)
            iv_link = f"https://t.me/iv?url={original_url}&rhash={RHASH}"
            
            # THE HYPERLINK MAGIC:
            # 1. Take the text before the link (this is your heading/title)
            title = msg_text.split(original_url)[0].strip()
            
            # 2. If there is no text, use a default title
            if not title:
                title = "Halkan ka aqriso warka"

            # 3. Create the hyperlinked text
            new_html_text = f'<b><a href="{iv_link}">{title}</a></b>'

            # 4. Update the post
            edit_url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
            requests.post(edit_url, data={
                "chat_id": CHAT_ID,
                "message_id": msg_id,
                "text": new_html_text,
                "parse_mode": "HTML"
            })
            print(f"Hyperlink created for {msg_id}")

if __name__ == "__main__":
    fix_links()
    
