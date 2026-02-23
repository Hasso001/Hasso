import os
import requests
import re

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RHASH = os.getenv('RHASH')

def fix_links():
    # Increase limit to 100 to make sure no posts are missed during long gaps
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url, params={"limit": 100, "allowed_updates": ["channel_post"]}).json()

    if not response.get("ok"): return

    for update in response.get("result", []):
        post = update.get("channel_post")
        if not post or "text" not in post: continue

        msg_text = post["text"]
        msg_id = post["message_id"]

        # Search for the kooxda link
        match = re.search(rf'https?://kooxda\.com/\S+', msg_text)

        # Only edit if it's a raw link and hasn't been fixed yet
        if match and "t.me/iv?" not in msg_text:
            original_url = match.group(0)
            iv_link = f"https://t.me/iv?url={original_url}&rhash={RHASH}"
            
            # Extract headline
            headline = msg_text.split('\n')[0].replace(original_url, "").strip()
            if not headline: headline = "Wararka Ciyaaraha"

            # Hidden space hyperlink to keep text black
            words = headline.split(' ')
            link_space = f'<a href="{iv_link}"> </a>'
            new_text = f"<b>{link_space.join(words)}</b>"

            edit_url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
            requests.post(edit_url, data={
                "chat_id": CHAT_ID,
                "message_id": msg_id,
                "text": new_text,
                "parse_mode": "HTML"
            })
            print(f"Fixed message {msg_id}")

from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running", 200

if __name__ == "__main__":
    # This starts your link fixer in the background
    threading.Thread(target=fix_links, daemon=True).start()
    # This starts the web server on port 8000 for Koyeb
    app.run(host='0.0.0.0', port=8000)
