import os, requests, re, time, threading
from flask import Flask
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def health():
    return "OK", 200

# Using the IDs from your previous setup
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '1952280080:AAE1jKGdPbFtOklxyd2DzAdRRuhMfvDlgQI')
RHASH = os.getenv('RHASH', 'ca7875208a06d7')

def get_headline(url):
    try:
        # Standard headers to avoid being blocked by the website
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, timeout=5, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Priority 1: Main Page Title (Best for kooxda.com)
        if soup.title and soup.title.string:
            title = soup.title.string.split('-')[0].strip()
            return title
            
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
                    
                    # Search for kooxda.com links [cite: Screenshot_2026022
