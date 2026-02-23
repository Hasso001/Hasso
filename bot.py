import os, requests, re, time, threading
from flask import Flask

app = Flask(__name__)
@app.route('/')
def health(): return "OK", 200

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '1952280080:AAE1jKGdPbFtOklxyd2DzAdRRuhMfvDlgQI')
RHASH = os.getenv('RHASH', 'ca7875208a06d7')
DOMAIN = "kooxda.com"

def fix_links():
    print("Bot is searching both Text and Captions...")
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            # Limit 1 ensures the Nano server doesn't crash on giant posts
            params = {"offset": offset, "timeout": 60, "limit": 1}
            res = requests.get(url, params=params).json()

            for upd in res.get("result", []):
                msg = upd.get("message") or upd.get("edited_message")
                if msg:
                    # FIX: This now looks at 'text' OR 'caption' for photos
                    raw_text = msg.get("text") or msg.get("caption") or ""
                    chat_id = msg["chat"]["id"]

                    # Search for the link anywhere in the message
                    match = re.search(r'https://kooxda\.com/\S+', raw_text)
                    
                    if match and "t.me/iv?" not in raw_text:
                        link = match.group(0)
                        iv_url = f"https://t.me/iv?url={link}&rhash={RHASH}"
                        
                        # Static text prevents errors with long string manipulation
                        reply = f'<b><a href="{iv_url}">WARARKA KOOXDA (INSTANT VIEW)</a></b>'
                        
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                     json={"chat_id": chat_id, "text": reply, "parse_mode": "HTML"})
                
                offset = upd["update_id"] + 1
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    threading.Thread(target=fix_links, daemon=True).start()
    app.run(host='0.0.0.0', port=8000)
