import requests, re, os
from flask import Flask, request

app = Flask(__name__)

# Hardcoded to ensure no environment errors
TOKEN = "1952280080:AAE1jKGdPbFtOklxyd2DzAdRRuhMfvDlgQI"
RHASH = "ca7875208a06d7"

def get_headline(url):
    try:
        res = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        title = re.search('<title>(.*?)</title>', res.text, re.I)
        return title.group(1).split('-')[0].strip() if title else "Wararka Ciyaaraha"
    except:
        return "Wararka Ciyaaraha"

@app.route(f'/{TOKEN}', methods=['POST'])
def respond():
    update = request.get_json()
    # Check for channel posts or messages
    msg = update.get("channel_post") or update.get("message")
    
    if msg and "text" in msg:
        text = msg["text"]
        chat_id = msg["chat"]["id"]
        message_id = msg["message_id"]
        
        match = re.search(r'https://kooxda\.com/\S+', text)
        if match and "t.me/iv?" not in text:
            url = match.group(0)
            title = get_headline(url)
            iv_link = f"https://t.me/iv?url={url}&rhash={RHASH}"
            
            # Invisible link trick to hide "kooxda.com"
            clean_text = f'<a href="{iv_link}">\u200b</a><b>{title}</b>'
            
            # EDIT the original message
            requests.post(f"https://api.telegram.org/bot{TOKEN}/editMessageText", 
                         json={
                             "chat_id": chat_id,
                             "message_id": message_id,
                             "text": clean_text,
                             "parse_mode": "HTML"
                         })
    return "OK", 200

@app.route('/')
def setup():
    # This automatically connects your bot to Koyeb when you visit the URL
    webhook_url = f"https://{request.host}/{TOKEN}"
    requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}")
    return "Bot is Connected!", 200
