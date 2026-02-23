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
        # Added a strict 3-second timeout so the bot doesn't hang
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, timeout=3, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find the title, otherwise use fallback
        if soup.title and soup.title.string:
            return soup.title.string.split('-')[0].strip()
        return "Wararka Ciyaaraha"
    except Exception as e:
        print(f"Scrape error: {e}")
        return "Wararka Ciyaaraha"

def fix_links():
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {"offset": offset, "timeout": 20, "limit": 1}
            res = requests.get(url, params=params).json()

            for upd in res.get("result", []):
                msg = upd.get("message") or upd.get("channel_post")
                if msg:
                    text = msg.get("text") or msg.get("caption") or ""
                    chat_id = msg["chat"]["id"]

                    match = re.search(r'https://kooxda\.com/\S+', text)
                    if match and "t.me/iv?" not in text:
                        original_url = match.group(0)
                        
                        # Get headline or fallback
                        article_headline = get_article_title(original_url)
                        iv_url = f"https://t.me/iv?url={original_url}&rhash={RHASH}"
                        
                        # Format: Bold Title with hidden Instant View link
                        reply = f'<b><a href="{iv_url}">{article_headline}</a></b>'
                        
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                     json={"chat_id": chat_id, "text": reply, "parse_mode": "HTML"})
                
                offset = upd["update_id"] + 1
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    threading.Thread(target=fix_links, daemon=True).start()
    app.run(host='0.0.0.0', port=8000)
