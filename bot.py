import os
import requests
import re
import time
import threading
from flask import Flask

# 1. Setup the Web Server for Koyeb
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running!", 200

# 2. Your Bot Configuration
# These will be pulled from the 'Environment Variables' you set in Koyeb
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '1952280080:AAE1jKGdPbFtOklxy...') 
RHASH = os.getenv('RHASH', 'ca7875208a06d7')
DOMAIN = "kooxda.com"

def fix_links():
    print("Bot is listening for instant replies...")
    offset = 0
    while True:
        try:
            # Get updates from Telegram
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {"offset": offset, "timeout": 30}
            r = requests.get(url, params=params).json()

            if r.get("ok"):
                for update in r["result"]:
                    # Check both DMs and Channel Posts
                    msg = update.get("message") or update.get("channel_post")
                    
                    if msg and "text" in msg:
                        text = msg["text"]
                        chat_id = msg["chat"]["id"]
                        msg_id = msg["message_id"]

                        # Search for the kooxda.com link
                        match = re.search(rf'https?://{DOMAIN}/\S+', text)
                        
                        if match and "t.me/iv?" not in text:
                            original_url = match.group(0)
                            iv_link = f"https://t.me/iv?url={original_url}&rhash={RHASH}"
                            
                            # Extract headline or use default
                            headline = text.split('\n')[0].replace(original_url, "").strip()
                            if not headline: headline = "Wararka"
                            
                            # Format with hidden link for 'Instant View'
                            words = headline.split(' ')
                            link_space = f'<a href="{iv_link}"> </a>'
                            new_text = f"<b>{link_space.join(words)}</b>"

                            # Send the fixed message
                            send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                            requests.post(send_url, data={
                                "chat_id": chat_id,
                                "text": new_text,
                                "parse_mode": "HTML"
                            })
                            print(f"Fixed link for chat {chat_id}")

                    offset = update["update_id"] + 1
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

# 3. Start everything
if __name__ == "__main__":
    # Runs the link fixer in the background
    threading.Thread(target=fix_links, daemon=True).start()
    
    # Runs the web server on port 8000 for Koyeb
    # Port must match your Koyeb screenshot setting
    app.run(host='0.0.0.0', port=8000)
