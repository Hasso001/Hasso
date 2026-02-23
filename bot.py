import os
import requests
import re
import time
import threading
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
            return soup.title.string.split('-')[0].strip()
        return "Wararka Ciyaaraha"
    except:
        return "Wararka Ciyaaraha"

def fix_links():
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {"offset": offset, "timeout": 20}
            res = requests.get(url, params=params).json()
            for upd in res.get("result", []):
                msg = upd.get("message") or upd.get("channel_post")
                if msg:
                    chat_id = msg["chat"]["id"]
                    content = msg.get("text") or msg.get("caption") or ""
                    match = re.search(r'https://kooxda\.com/\S+', content)
                    if match and "t.me/iv?" not in content:
                        link = match.group(0)
                        title = get_headline(link)
                        iv_url = f"https://t.me/iv?url={link}&rhash={RHASH}"
                        reply = f'<b><a href="{iv_url}">{title}</a></b>'
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                     json={"chat_id": chat_id, "text": reply, "parse_mode": "HTML"})
                offset = upd["update_id"] + 1
        except:
            time.sleep(2)

if __name__ == "__main__":
    threading.Thread(target=fix_links, daemon=True).start()
    app.run(host='0.0.0.0', port=8000)
