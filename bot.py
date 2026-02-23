
import os, requests, re, time, threading
from flask import Flask
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def health():
    return "OK", 200

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '1952280080:AAE1jKGdPbFtOklxyd2DzAdRRuhMfvDlgQI')
RHASH = os.getenv('RHASH', 'ca7875208a06d7')

def get_headline(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, timeout=5, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.title and soup.title.string:
            # Grabs the actual article title for Ciyaaraha Dunida
            return soup.title.string.split('-')[0].strip()
        return "Wararka Ciyaaraha"
    except:
        return "Wararka Ciyaaraha"

def fix_links():
    offset = 0
    while True:
        try:
            # Check for new messages every 20 seconds
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            res = requests.get(url, params={"offset": offset, "timeout": 20}).json()
            for upd in res.get("result", []):
                msg = upd.get("message") or upd.get("channel_post")
                if msg:
                    chat_id = msg["chat"]["id"]
                    text = msg.get("text") or msg.get("caption") or ""
                    # Match links from kooxda.com
                    match = re.search(r'https://kooxda\.com/\S+', text)
                    if match and "t.me/iv?" not in text:
                        link = match.group(0)
                        title = get_headline(link)
                        iv_url = f"https://t.me/iv?url={link}&rhash={RHASH}"
                        # Send the bold headline with the IV link
                        reply = f'<b><a href="{iv_url}">{title}</a></b>'
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                     json={"chat_id": chat_id, "text": reply, "parse_mode": "HTML"})
                offset = upd["update_id"] + 1
        except:
            time.sleep(2)

# Start the background thread for Telegram
threading.Thread(target=fix_links, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
