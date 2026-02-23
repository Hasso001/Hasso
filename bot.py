import os, requests, re, time, threading
from flask import Flask

app = Flask(__name__)
@app.route('/')
def health(): return "OK", 200

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '1952280080:AAE1jKGdPbFtOklxyd2DzAdRRuhMfvDlgQI')
RHASH = os.getenv('RHASH', 'ca7875208a06d7')
DOMAIN = "kooxda.com"

def fix_links():
    offset = 0
    print("Bot is searching Text + Photo Captions...")
    while True:
        try:
            # We explicitly ask for ALL message types
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {"offset": offset, "timeout": 30, "allowed_updates": ["message", "edited_message", "channel_post"]}
            res = requests.get(url, params=params).json()

            for upd in res.get("result", []):
                # Check every possible place text could hide
                msg = upd.get("message") or upd.get("edited_message") or upd.get("channel_post")
                
                if msg:
                    chat_id = msg["chat"]["id"]
                    # This captures regular text AND text under photos/videos
                    content = msg.get("text") or msg.get("caption") or ""
                    
                    if content:
                        # Find the link anywhere in the block
                        match = re.search(r'https://kooxda\.com/\S+', content)
                        
                        if match and "t.me/iv?" not in content:
                            link = match.group(0)
                            iv_url = f"https://t.me/iv?url={link}&rhash={RHASH}"
                            
                            # Simplify the reply to ensure it sends even on low memory
                            reply_text = f'<b><a href="{iv_url}">WARARKA KOOXDA (INSTANT VIEW)</a></b>'
                            
                            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                         json={"chat_id": chat_id, "text": reply_text, "parse_mode": "HTML"})
                
                offset = upd["update_id"] + 1
        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    threading.Thread(target=fix_links, daemon=True).start()
    app.run(host='0.0.0.0', port=8000)
