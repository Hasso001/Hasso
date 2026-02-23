import os
import requests
import re
import time
from flask import Flask

# Minimal web server to keep Koyeb happy
app = Flask(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
RHASH = os.getenv('RHASH')
DOMAIN = "kooxda.com"

def run_bot():
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            r = requests.get(url, params={"offset": offset, "timeout": 30}).json()
            if r.get("ok"):
                for update in r["result"]:
                    msg = update.get("message") or update.get("channel_post")
                    if msg and "text" in msg:
                        text = msg["text"]
                        chat_id = msg["chat"]["id"]
                        match = re.search(rf'https?://{DOMAIN}/\S+', text)
                        if match and "t.me/iv?" not in text:
                            iv_link = f"https://t.me/iv?url={match.group(0)}&rhash={RHASH}"
                            # Send instant reply
                            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                          data={"chat_id": chat_id, "text": f"Xiriirkaaga: {iv_link}"})
                    offset = update["update_id"] + 1
        except:
            time.sleep(10)

@app.route('/')
def home():
    return "Bot is active!"

if __name__ == "__main__":
    # Run the bot in a background thread
    import threading
    threading.Thread(target=run_bot, daemon=True).start()
    # Run the web server
    app.run(host='0.0.0.0', port=8000)
