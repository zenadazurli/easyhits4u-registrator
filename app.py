#!/usr/bin/env python3
import requests
import json
import base64
import time
import random
import os
from datetime import datetime
from pathlib import Path

API_KEYS = os.environ.get('BROWSERLESS_KEYS', '').split(',')
if not API_KEYS or API_KEYS[0] == '':
    API_KEYS = ["2UBQ5qEPkTsCBv63a4077ae6c54e5490f1efd231f724e110f"]

BROWSERLESS_URL = "https://production-sfo.browserless.io/chrome/bql"
PASSWORD = os.environ.get('ACCOUNT_PASSWORD', 'Test123!@#')
OUTPUT_DIR = "/tmp/easyhits4u"

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def generate_username():
    syllables = ["ka","lo","mi","ta","ne","za","ga","ra","chi","lu","no","be","ce","re","di","sa"]
    return "u" + "".join(random.choice(syllables) for _ in range(random.randint(3, 5)))

def create_account(api_key, username, email):
    bql_url = f"{BROWSERLESS_URL}?token={api_key}&stealth=true&proxy=residential&proxyCountry=it"
    
    js_script = f"""
    (async () => {{
        window.location.href = 'https://www.easyhits4u.com/?ref=nicolacaporale';
        await new Promise(r => setTimeout(r, 5000));
        
        const joinLink = document.querySelector('a[href*="join_popup_show"]');
        if (joinLink) joinLink.click();
        await new Promise(r => setTimeout(r, 3000));
        
        const nameField = document.querySelector('#reg_form #name');
        if (nameField) nameField.value = '{username}';
        
        const emailField = document.querySelector('#reg_form #email');
        if (emailField) emailField.value = '{email}';
        
        const loginField = document.querySelector('#reg_form #login');
        if (loginField) loginField.value = '{username}';
        
        const passField = document.querySelector('#reg_form #pass');
        if (passField) passField.value = '{PASSWORD}';
        
        const cpassField = document.querySelector('#reg_form #cpass');
        if (cpassField) cpassField.value = '{PASSWORD}';
        
        await new Promise(r => setTimeout(r, 10000));
        
        const submitBtn = document.querySelector('#reg_form input[type="submit"]');
        if (submitBtn) submitBtn.click();
        await new Promise(r => setTimeout(r, 5000));
        
        return document.cookie;
    }})()
    """
    
    query = f"""
    mutation {{
      goto(url: "https://www.easyhits4u.com/?ref=nicolacaporale", waitUntil: networkIdle) {{
        status
        url
      }}
      evaluate(script: {json.dumps(js_script)}) {{
        value
      }}
      screenshot(fullPage: true) {{
        base64
      }}
    }}
    """
    
    try:
        resp = requests.post(bql_url, json={"query": query}, timeout=150)
        if resp.status_code != 200:
            return None, None
        
        data = resp.json()
        if "errors" in data:
            log(f"Errore: {data['errors'][0].get('message')}")
            return None, None
        
        cookies_str = data.get("data", {}).get("evaluate", {}).get("value", "")
        cookies = {}
        for cookie in cookies_str.split(";"):
            if "=" in cookie:
                k, v = cookie.strip().split("=", 1)
                cookies[k] = v
        
        screenshot = data.get("data", {}).get("screenshot", {}).get("base64")
        if screenshot:
            with open(f"{OUTPUT_DIR}/shot_{username}.png", "wb") as f:
                f.write(base64.b64decode(screenshot))
        
        return 'user_id' in cookies, cookies
    except Exception as e:
        log(f"Errore: {e}")
        return None, None

def main():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    num = int(os.environ.get('NUM_ACCOUNTS', '1'))
    success = 0
    
    for i in range(num):
        username = generate_username()
        email = f"{username}@spaces0.com"
        log(f"Account {i+1}: {username}")
        
        ok = False
        for key in API_KEYS:
            if not key.strip():
                continue
            result, cookies = create_account(key.strip(), username, email)
            if result:
                with open(f"{OUTPUT_DIR}/accounts.txt", "a") as f:
                    f.write(f"{email}|{PASSWORD}|user_id:{cookies.get('user_id')}\n")
                success += 1
                ok = True
                break
            time.sleep(3)
        
        if not ok:
            log(f"Account {i+1} fallito")
        if i < num-1:
            time.sleep(random.randint(30, 60))
    
    log(f"Creati: {success}/{num}")

if __name__ == "__main__":
    main()
