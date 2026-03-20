#!/usr/bin/env python3
# app.py - Versione per Render con sintassi corretta

import requests
import json
import base64
import time
import random
import os
from datetime import datetime
from pathlib import Path

# ==================== CONFIGURAZIONE ====================
API_KEYS = os.environ.get('BROWSERLESS_KEYS', '').split(',')

if not API_KEYS or API_KEYS[0] == '':
    API_KEYS = [
        "2UBQ5qEPkTsCBv63a4077ae6c54e5490f1efd231f724e110f",
        "2UBQ8GwsajXwbXs10e72471480af4adaeb28a5a6a01ac89a7",
        "2UBQFmSYHD4NZGdb2f0eedc0e05b5de53a6746218bcdc139a",
    ]

BROWSERLESS_URL = "https://production-sfo.browserless.io/chrome/bql"
PASSWORD = os.environ.get('ACCOUNT_PASSWORD', 'Test123!@#')
REFERER_URL = "https://www.easyhits4u.com/?ref=nicolacaporale"

OUTPUT_DIR = "/tmp/easyhits4u"
ACCOUNTS_FILE = f"{OUTPUT_DIR}/accounts.json"
ACCOUNTS_TXT = f"{OUTPUT_DIR}/accounts.txt"

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {msg}", flush=True)

def setup_output_dir():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def generate_username():
    syllables = ["ka","lo","mi","ta","ne","za","ga","ra","chi","lu","no","be","ce","re","di","sa"]
    count = random.randint(3, 5)
    return "u" + "".join(random.choice(syllables) for _ in range(count))

def create_account_via_browserless(api_key, username, email):
    log(f"🔑 Usando API key: {api_key[:20]}...")
    
    bql_url = f"{BROWSERLESS_URL}?token={api_key}&stealth=true&proxy=residential&proxyCountry=it"
    
    # La stringa JavaScript deve essere su una riga singola per evitare problemi di indentazione
    js_function = "async () => { await new Promise(r => setTimeout(r, 2000)); const usernameField = document.querySelector('#reg_form #name'); if (usernameField) { usernameField.value = arguments[0]; usernameField.dispatchEvent(new Event('input', { bubbles: true })); } const emailField = document.querySelector('#reg_form #email'); if (emailField) { emailField.value = arguments[1]; emailField.dispatchEvent(new Event('input', { bubbles: true })); } const loginField = document.querySelector('#reg_form #login'); if (loginField) { loginField.value = arguments[0]; loginField.dispatchEvent(new Event('input', { bubbles: true })); } const passField = document.querySelector('#reg_form #pass'); if (passField) { passField.value = arguments[2]; passField.dispatchEvent(new Event('input', { bubbles: true })); } const cpassField = document.querySelector('#reg_form #cpass'); if (cpassField) { cpassField.value = arguments[2]; cpassField.dispatchEvent(new Event('input', { bubbles: true })); } await new Promise(r => setTimeout(r, 3000)); const submitBtn = document.querySelector('#reg_form input[type=\"submit\"], #reg_form button[type=\"submit\"]'); if (submitBtn) { submitBtn.click(); } await new Promise(r => setTimeout(r, 5000)); return document.cookie; }"
    
    query = f"""
    mutation {{
      goto(url: "https://www.easyhits4u.com/?ref=nicolacaporale", waitUntil: networkIdle, timeout: 60000) {{
        status
        url
      }}
      
      click(selector: "a[href*='join_popup_show']") {{
        clicked
      }}
      
      waitFor(selector: "#reg_form", timeout: 30000) {{
        exists
      }}
      
      solve(type: cloudflare, timeout: 60000) {{
        found
        solved
        token
        time
      }}
      
      evaluate(expression: "{js_function}", args: ["{username}", "{email}", "{PASSWORD}"]) {{
        value
      }}
      
      screenshot(fullPage: true) {{
        base64
      }}
    }}
    """
    
    try:
        response = requests.post(
            bql_url,
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=180
        )
        
        if response.status_code != 200:
            log(f"❌ Errore HTTP: {response.status_code}")
            log(f"   {response.text[:200]}")
            return None, None
        
        data = response.json()
        
        if "errors" in data:
            log(f"❌ Errori: {data['errors']}")
            return None, None
        
        result = data.get("data", {})
        
        cookies_str = result.get("evaluate", {}).get("value", "")
        cookies = {}
        for cookie in cookies_str.split(";"):
            if "=" in cookie:
                key, val = cookie.strip().split("=", 1)
                cookies[key] = val
        
        screenshot_data = result.get("screenshot", {}).get("base64")
        if screenshot_data:
            filename = f"{OUTPUT_DIR}/screenshot_{username}_{int(time.time())}.png"
            with open(filename, "wb") as f:
                f.write(base64.b64decode(screenshot_data))
            log(f"📸 Screenshot: {filename}")
        
        if 'user_id' in cookies:
            log(f"✅ Registrazione riuscita! user_id: {cookies['user_id']}")
            return True, cookies
        else:
            log(f"❌ Registrazione fallita")
            return False, cookies
            
    except Exception as e:
        log(f"❌ Errore: {e}")
        return None, None

def save_account(username, email, cookies):
    account_data = {
        "username": username,
        "email": email,
        "password": PASSWORD,
        "user_id": cookies.get('user_id'),
        "sesids": cookies.get('sesids'),
        "timestamp": datetime.now().isoformat()
    }
    
    accounts = []
    if Path(ACCOUNTS_FILE).exists():
        with open(ACCOUNTS_FILE, "r") as f:
            try:
                accounts = json.load(f)
            except:
                accounts = []
    
    accounts.append(account_data)
    
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=2)
    
    with open(ACCOUNTS_TXT, "a") as f:
        f.write(f"{email} | {PASSWORD} | user_id: {cookies.get('user_id')}\n")
    
    log(f"💾 Account salvato")

def main():
    log("=" * 60)
    log("🚀 BROWSERLESS ACCOUNT CREATOR")
    log("=" * 60)
    
    setup_output_dir()
    
    try:
        num_accounts = int(os.environ.get('NUM_ACCOUNTS', '1'))
    except:
        num_accounts = 1
    
    log(f"📊 Account da creare: {num_accounts}")
    log(f"🔑 API keys disponibili: {len(API_KEYS)}")
    
    success_count = 0
    
    for i in range(num_accounts):
        log(f"\n{'='*60}")
        log(f"📝 CREAZIONE ACCOUNT {i+1}/{num_accounts}")
        log(f"{'='*60}")
        
        username = generate_username()
        email = f"{username}@spaces0.com"
        
        log(f"👤 Username: {username}")
        log(f"📧 Email: {email}")
        
        success = False
        for api_key in API_KEYS:
            if not api_key.strip():
                continue
            result, cookies = create_account_via_browserless(api_key.strip(), username, email)
            if result and cookies and 'user_id' in cookies:
                save_account(username, email, cookies)
                success_count += 1
                success = True
                break
            else:
                log(f"⚠️ Fallito con questa chiave, provo la prossima...")
                time.sleep(5)
        
        if not success:
            log(f"❌ Account {i+1} fallito")
        
        if i < num_accounts - 1:
            pause = random.randint(30, 60)
            log(f"⏸️ Pausa di {pause} secondi...")
            time.sleep(pause)
    
    log("\n" + "=" * 60)
    log(f"🏁 PROCESSO COMPLETATO!")
    log(f"✅ Account creati: {success_count}/{num_accounts}")
    log(f"💾 File salvati in: {OUTPUT_DIR}")
    log("=" * 60)

if __name__ == "__main__":
    main()
