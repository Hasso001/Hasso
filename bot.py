import os, requests, re, time, threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def health():
    return "OK", 200

TOKEN = "1952280080:AAE1jKGdPbFtOklxyd2DzAdRRuhMfvDlgQI"
RHASH = "ca7875208a06d7"

def get_headline(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, timeout=10, headers=headers)
        title_search = re.search('<title>(.*?)</title>', response.text, re.IGNORECASE)
        if title_search:
            # Grabs the clean title
            return title_search.group(1).split('-')[0].strip()
        return "Wararka Ciyaaraha"
    except:
        return "Wararka Ciyaaraha"

def fix_links():
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            res = requests.get(url, params={"offset": offset, "timeout": 20}).json()
            if "result" in res:
                for upd in res["result"]:
                    msg = upd.get("message") or upd.get("channel_post")
                    if msg:
                        chat_id = msg["chat"]["id"]
                        text = msg.get("text") or msg.get("caption") or ""
                        match = re.search(r'https://kooxda\.com/\S+', text)
                        
                        if match and "t.me/iv?" not in text:
                            link = match.group(0)
                            title = get_headline(link)
                            iv_url = f"https://t.me/iv?url={link}&rhash={RHASH}"
                            
                            # THE TRICK: \u200b is an invisible character that holds the link
                            # This makes the title plain bold and NOT clickable.
                            invisible_link = f'<a href="{iv_url}">\u200b</a>'
                            message_text = f'{invisible_link}<b>{title}</b>'
                            
                            payload = {
                                "chat_id": chat_id,
                                "text": message_text,
                                "parse_mode": "HTML"
                            }
                            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload)
                    
                    offset = upd["update_id"] + 1
        except:
            time.sleep(5)

threading.Thread(target=fix_links, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
