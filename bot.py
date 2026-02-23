import os
import requests
import re
import time
import threading
from flask import Flask

# 1. Setup the Web Server for Koyeb Health Checks
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running!", 200

# 2. Your Bot Configuration
# Uses Environment Variables from Koyeb; uses your keys as backup
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '1952280080:AAE1jKGdPbFtOklxyd2DzAdRRuhMfvDlgQI')
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
            response = requests.get(url, params=params).json()

            if "result" in response:
                for update in response["result"]:
                    if "message" in update and "text" in update["message"]:
                        text = update["message"]["text"]
                        chat_id = update["message"]["chat_id"]

                        # SEARCH: This finds the link anywhere in a message/paragraph
                        match = re.search(rf'https://{DOMAIN}/\S+', text)
                        
                        # Only process if it's a new link and NOT already an IV link
                        if match and "t.me/iv?" not in text:
                            original_url = match.group(0)
                            iv_link = f"https://t.me/iv?url={original_url}&rhash={RHASH}"
                            
                            # Extract headline or use default
                            headline = text.split('\n')[0].replace(original_url, "").strip()
                            if not headline or len(headline) < 3:
                                headline = "Wararka Kooxda"
                            
                            # Format with hidden link for 'Instant View'
                            words = headline.split(' ')
                            link_space = f'<a href="{iv_link}"> </a>'
                            new_text = f"<b>{link_space.join(words)}</b>"
