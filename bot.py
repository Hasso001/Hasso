import requests, re, os
from flask import Flask, request

app = Flask(__name__)

# Credentials hardcoded to prevent Environment Variable errors
TOKEN = "1952280080:AAE1jKGdPbFtOklxyd2DzAdRRuhMfvDlgQI"
RHASH = "ca7875208a06d7"

def get_headline(url):
    try:
        res = requests.get(url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        title = re.search('<title>(.*?)</title>', res.text, re.I)
        # Returns the clean headline for Ciyaaraha Dunida
        return title.group(1).split('-')[0].strip() if title else "Wararka Ciyaaraha"
    except:
        return "Wararka Ciyaaraha"

@app.route(f'/{TOKEN}', methods=['POST'])
def telegram_update():
    update = request.get_json()
    # Captures channel posts or group messages
    msg = update.get("channel_post") or update.get("message")
    
    if msg and "text" in msg:
        text = msg["text"]
        chat_id = msg["chat"]["id"]
        message_id = msg["message_id"]
        
        # Look for the news link
        match = re.search(r'https://kooxda\.com/\S+', text)
        if match and "t.me/iv?" not in text:
            url = match.group(0)
            title = get_headline(url)
            iv_link = f"https://t.me/iv?url={url}&rhash={RHASH}"
            
            # \u200b is an invisible character that removes "kooxda.com" from the title
            clean_text = f'<a href="{iv_link}">\u200b</a><b>{title}</b>'
            
            # EDITS the original message instantly
            requests.post(f"https://api.telegram.org/bot{TOKEN}/editMessageText", 
                         json={
                             "chat_id": chat_id,
                             "message_id": message_id,
                             "text": clean_text,
                             "parse_mode": "HTML"
                         })
    return "OK", 200

@app.route('/')
def home():
    # Visit your Koyeb URL once to trigger this setup
    webhook_url = f"https://{request.host}/{TOKEN}"
    requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}")
    return "Bot Setup Complete!", 200
