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
    print("Bot is listening...")
    offset = 0
    while True:
        try:
            # Added a 60-second timeout to handle very long messages without crashing
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {"offset": offset, "timeout": 60, "allowed_updates": ["message"]}
            response = requests.get(url, params=params).json()

            if "result" in response:
                for update in response["result"]:
                    if "message" in update and "text" in update["message"]:
                        text = update["message"]["text"]
                        chat_id = update["message"]["chat_id"]

                        # This finds the link anywhere, even in giant 4000-character posts
                        match = re.search(rf'https://{DOMAIN}/[a-zA-Z0-9\-\/]+', text)
                        
                        if match and "t.me/iv?" not in text:
                            original_url = match.group(0)
                            iv_link = f"https://t.me/iv?url={original_url}&rhash={RHASH}"
                            
                            # For long messages, we just use a standard title to avoid errors
                            headline = "Wararka Kooxda (Instant View)"
                            
                            new_text = f'<b><a href="{iv_link}">{headline}</a></b>'

                            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                         json={"chat_id": chat_id, "text": new_text, "parse_mode": "HTML"})
                    
                    if "update_id" in update:
                        offset = update["update_id"] + 1
                
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    threading.Thread(target=fix_links, daemon=True).start()
    app.run(host='0.0.0.0', port=8000)
