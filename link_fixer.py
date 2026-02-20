import os
import requests
import re

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RHASH = os.getenv('RHASH')

def fix_links():
    # Force look at the last 15 updates
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url, params={"limit": 15}).json()

    if not response.get("ok"): return

    for update in response.get("result", []):
        post = update.get("channel_post")
        if not post or "text" not in post: continue

        msg_text = post["text"]
        msg_id = post["message_id"]

        # Look for the kooxda link
        match = re.search(rf'https?://kooxda\.com/\S+', msg_text)

        # Only edit if we find a link and it's not already an IV link
        if match and "t.me/iv?" not in msg_text:
            original_url = match.group(0)
            iv_link = f"https://t.me/iv?url={original_url}&rhash={RHASH}"
            
            # Use the first line as headline
            headline = msg_text.split('\n')[0].replace(original_url, "").strip()
            if not headline: headline = "Wararka Ciyaaraha"

            # TRICK: Put the link in the spaces to keep headline BLACK
            words = headline.split(' ')
            link_space = f'<a href="{iv_link}"> </a>'
            new_text = f"<b>{link_space.join(words)}</b>"

            # Execute the Edit
            edit_url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
            requests.post(edit_url, data={
                "chat_id": CHAT_ID,
                "message_id": msg_id,
                "text": new_text,
                "parse_mode": "HTML"
            })
            print(f"Updated message {msg_id}")

if __name__ == "__main__":
    fix_links()
    
