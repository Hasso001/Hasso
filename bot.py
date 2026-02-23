import os
import requests
import re
import time
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running!", 200

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '1952280080:AAE1jKGdPbFtOklxyd2DzAdRRuhMfvDlgQI')
RHASH = os.getenv('RHASH', 'ca7875208a06d7')
DOMAIN = "kooxda.com"

def fix_links():
    print("Bot is active and searching for links...")
    offset = 0
    while True:
        try:
            # Increased timeout and limit to 1 to focus on one big message at a time
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {"offset": offset, "timeout": 60, "limit": 1}
            response = requests.get(url, params=params).json()

            if "result" in response:
                for update in response["result"]:
                    if "message" in update and "text" in update["message"]:
                        text = update["message"]["text"]
                        chat_id = update["message"]["chat_id"]

                        # Optimized search for long messages
                        link_match = re.search(r'https://kooxda\.com/\S+', text)
                        
                        if link_match and "t.me/iv?" not in text:
                            original_url = link_match.group(0)
                            iv_link = f"https://t.me/iv?url={original_url}&rhash={RHASH}"
                            
                            # We use a fixed headline to save processing time on long texts
                            new_text = f'<b><a href="{iv_link}">WARARKA KOOXDA (INSTANT VIEW)</a></b>'

                            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                         json={"chat_id": chat_id, "text": new_text, "parse_mode": "HTML"})
                    
                    if "update_id" in update:
                        offset = update["update_id"] + 1
                
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(2)

if __name__ == "__main__":
    threading.Thread(target=fix_links, daemon=True).start()
    app.run(host='0.0.0.0', port=8000)
