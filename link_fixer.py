import os
import requests
import re

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RHASH = os.getenv('RHASH')
DOMAIN = "kooxda.com"

def fix_links():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url, params={"allowed_updates": ["channel_post"], "limit": 10}).json()

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
            
            # Get only the first line/headline
            first_line = msg_text.split('\n')[0].replace(original_url, "").strip()
            if not first_line: first_line = "Wararka Maanta"

            # THE "HIDDEN SPACE" TRICK:
            # We split the headline into words and join them with hyperlinked spaces
            words = first_line.split(' ')
            # This creates a link attached to the space character between words
            linked_space = f'<a href="{iv_link}"> </a>'
            new_html_text = f"<b>{linked_space.join(words)}</b>"

            edit_url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
            requests.post(edit_url, data={
                "chat_id": CHAT_ID,
                "message_id": msg_id,
                "text": new_html_text,
                "parse_mode": "HTML"
            })
        
