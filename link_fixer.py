import os
import requests
import re

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RHASH = os.getenv('RHASH')
DOMAIN = "kooxda.com"

def fix_links():
    # 1. Get updates from the channel
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url, params={"allowed_updates": ["channel_post"]}).json()

    if not response.get("ok"):
        return

    for update in response.get("result", []):
        post = update.get("channel_post")
        if not post or "text" not in post: continue

        msg_text = post["text"]
        msg_id = post["message_id"]

        # 2. Look for the kooxda.com link
        pattern = rf'https?://{DOMAIN}/\S+'
        match = re.search(pattern, msg_text)

        if match and "t.me/iv?" not in msg_text:
            original_url = match.group(0)
            # Create the hidden Instant View link
            iv_link = f"https://t.me/iv?url={original_url}&rhash={RHASH}"
            
            # 3. Hide the link inside the first few words of the text
            # This keeps the 'Instant View' button but hides the ugly URL
            clean_text = msg_text.replace(original_url, "").strip()
            hidden_link_text = f'<a href="{iv_link}">🌐 Linkiga rasmiga ah</a>\n\n{clean_text}'

            # 4. Update the message using HTML mode
            edit_url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
            requests.post(edit_url, data={
                "chat_id": CHAT_ID,
                "message_id": msg_id,
                "text": hidden_link_text,
                "parse_mode": "HTML"
            })
            print(f"Hidden link created for message {msg_id}")

if __name__ == "__main__":
    fix_links()
    
