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
# The code will check Koyeb's environment variables first, then use your keys as backup
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

                        # Check if the message contains the link
                        match = re.search(rf'https://{DOMAIN}/\S+', text)
                        
                        if match and "t.me/iv?" not in text:
                            original_url = match.group(0)
                            iv_link = f"https://t.me/iv?url={original_url}&rhash={RHASH}"
                            
                            # Extract headline or use default
                            headline = text.split('\n')[0].replace(original_url, "").strip()
                            if not headline:
                                headline = "Wararka"
                            
                            # Format with hidden link for 'Instant View'
                            words = headline.split(' ')
                            link_space = f'<a href="{iv_link}"> </a>'
                            new_text = f"<b>{link_space.join(words)}</b>"

                            # Send the fixed message back
                            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                         json={"chat_id": chat_id, "text": new_text, "parse_mode": "HTML"})
                    
                    if "update_id" in update:
                        offset = update["update_id"] + 1
                
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # Start the link-fixing loop in a separate thread
    threading.Thread(target=fix_links, daemon=True).start()
    # Run the web server on Port 8000 for Koyeb
    app.run(host='0.0.0.0', port=8000)
