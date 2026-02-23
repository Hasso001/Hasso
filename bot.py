import os, requests, re, time, threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def health(): return "OK", 200

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '1952280080:AAE1jKGdPbFtOklxyd2DzAdRRuhMfvDlgQI')
RHASH = os.getenv('RHASH', 'ca7875208a06d7')
DOMAIN = "kooxda.com"

def get_headline(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, timeout=10, headers=headers)
        # Finds the article title
        title_search = re.search('<title>(.*?)</title>', response.text, re.IGNORECASE)
        if title_search:
            return title_search.group(1).split('-')[0].strip()
        return "Wararka Ciyaaraha"
    except:
        return "Wararka Ciyaaraha"

def run_bot():
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            r = requests.get(url, params={"offset": offset, "timeout": 30}).json()
            if r.get("ok"):
                for update in r["result"]:
                    # Works for both private messages and channel posts
                    msg = update.get("message") or update.get("channel_post")
                    if msg:
                        text = msg.get("text") or msg.get("caption") or ""
                        chat_id = msg["chat"]["id"]
                        message_id = msg["message_id"]
                        
                        match = re.search(rf'https?://{DOMAIN}/\S+', text)
                        # Only edit if it's a raw link and not already an IV link
                        if match and "t.me/iv?" not in text:
                            original_url = match.group(0)
                            title = get_headline(original_url)
                            iv_link = f"https://t.me/iv?url={original_url}&rhash={RHASH}"
                            
                            # Invisible link + Bold Headline
                            new_text = f'<a href="{iv_link}">\u200b</a><b>{title}</b>'
                            
                            # Use editMessageText to change the existing post
                            requests.post(f"https://api.telegram.org/bot{TOKEN}/editMessageText", 
                                          data={
                                              "chat_id": chat_id,
                                              "message_id": message_id,
                                              "text": new_text,
                                              "parse_mode": "HTML",
                                              "disable_web_page_preview": False
                                          })
                    offset = update["update_id"] + 1
        except:
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=8000)
