import os, requests, re, time, threading
from flask import Flask
from bs4 import BeautifulSoup

app = Flask(__name__)
@app.route('/')
def health(): return "OK", 200

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '1952280080:AAE1jKGdPbFtOklxyd2DzAdRRuhMfvDlgQI')
RHASH = os.getenv('RHASH', 'ca7875208a06d7')

def get_article_title(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'lxml')
        # This grabs the actual <title> of the webpage
        return soup.title.string.split('-')[0].strip() 
    except:
        return "Wararka Ciyaaraha" # Fallback if site is slow

def fix_links():
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {"offset": offset, "timeout": 30, "limit": 1}
            res = requests.get(url, params=params).json()

            for upd in res.get("result", []):
                msg = upd.get("message")
                if msg:
                    text = msg.get("text") or msg.get("caption") or ""
                    chat_id = msg["chat"]["id"]

                    match = re.search(r'https://kooxda\.com/\S+', text)
                    if match and "t.me/iv?" not in text:
                        original_url = match.group(0)
                        
                        # STEP 1: Get the real headline from the website
                        article_headline = get_article_title(original_url)
                        
                        # STEP 2: Create the IV link
                        iv_url = f"https://t.me/iv?url={original_url}&rhash={RHASH}"
                        
                        # STEP 3: Put that headline in the bold title spot
                        reply = f'<b><a href="{iv_url}">{article_headline}</a></b>'
                        
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                     json={"chat_id": chat_id, "text": reply, "parse_mode": "HTML"})
                
                offset = upd["update_id"] + 1
        except:
            time.sleep(2)

if __name__ == "__main__":
    threading.Thread(target=fix_links, daemon=True).start()
    app.run(host='0.0.0.0', port=8000)
