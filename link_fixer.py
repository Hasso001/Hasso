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
            
            # THE "HEADLINE ONLY" LOGIC:
            # 1. Grab only the very first line of the message
            first_line = msg_text.split('\n')[0]
            
            # 2. Remove the raw URL from that line if it's there
            clean_headline = first_line.replace(original_url, "").strip()
            
            # 3. If the first line was just the link, use a default
            if not clean_headline:
                clean_headline = "Halkan ka aqriso warka"

            # 4. Set the message to ONLY the bold hyperlink
            new_html_text = f'<b><a href="{iv_link}">{clean_headline}</a></b>'

            edit_url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
            requests.post(edit_url, data={
                "chat_id": CHAT_ID,
                "message_id": msg_id,
                "text": new_html_text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            })
            print(f"Post cleaned to headline only for {msg_id}")

if __name__ == "__main__":
    fix_links()
    
