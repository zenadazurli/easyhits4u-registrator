#!/usr/bin/env python3
# app.py - Versione con API REST di browserless

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
    ]

BROWSERLESS_URL = "https://production-sfo.browserless.io"
PASSWORD = os.environ.get('ACCOUNT_PASSWORD', 'Test123!@#')

OUTPUT_DIR = "/tmp/easyhits4u"

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
    """Crea account usando API REST di browserless"""
    log(f"🔑 Usando API key: {api_key[:20]}...")
    
    # Usa l'endpoint REST /function
    url = f"{BROWSERLESS_URL}/function?token={api_key}&stealth=true&proxy=residential&proxyCountry=it"
    
    # Script JavaScript che fa tutto
    js_code = f"""
    const puppeteer = require('puppeteer-core');
    
    async function run() {{
        const browser = await puppeteer.connect({{ browserWSEndpoint: process.env.BROWSER_WS_ENDPOINT }});
        const page = await browser.newPage();
        
        // Naviga alla pagina
        await page.goto('https://www.easyhits4u.com/?ref=nicolacaporale', {{ waitUntil: 'networkidle2', timeout: 60000 }});
        
        // Clicca sul link di registrazione
        await page.click('a[href*="join_popup_show"]');
        await page.waitForTimeout(3000);
        
        // Compila il form
        await page.type('#reg_form #name', '{username}');
        await page.type('#reg_form #email', '{email}');
        await page.type('#reg_form #login', '{username}');
        await page.type('#reg_form #pass', '{PASSWORD}');
        await page.type('#reg_form #cpass', '{PASSWORD}');
        
        // Attendi Turnstile
        await page.waitForTimeout(15000);
        
        // Clicca submit
        await page.click('#reg_form input[type="submit"]');
        await page.waitForTimeout(5000);
        
        // Ottieni cookie
        const cookies = await page.cookies();
        const cookieString = cookies.map(c => `${{c.name}}=${{c.value}}`).join(';');
        
        // Screenshot
        await page.screenshot({{ path: 'screenshot.png', fullPage: true }});
        
        await browser.close();
        
        return cookieString;
    }}
    
    module.exports = run;
    """
    
    try:
        log("📡 Invio richiesta a browserless REST API...")
        start_time = time.time()
        
        response = requests.post(
            url,
            data=js_code,
            headers={"Content-Type": "application/javascript"},
            timeout=180
        )
        
        elapsed = time.time() - start_time
        log(f"⏱️ Richiesta completata in {elapsed:.1f} secondi")
        
        if response.status_code != 200:
            log(f"❌ Errore HTTP: {response.status_code}")
            log(f"   Risposta: {response.text[:500]}")
            return None, None
        
        cookies_str = response.text.strip()
        
        # Parsing cookie
        cookies = {}
        for cookie in cookies_str.split(";"):
            if "=" in cookie:
                key, val = cookie.strip().split("=", 1)
                cookies[key] = val
        
        log(f"🔑 Cookie keys: {list(cookies.keys())}")
        
        if 'user_id' in cookies:
            log(f"✅✅✅ REGISTRAZIONE RIUSCITA! user_id: {cookies['user_id']}")
            return True, cookies
        else:
            log(f"❌ Registrazione fallita - user_id non trovato")
            return False, cookies
            
    except Exception as e:
        log(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
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
    accounts_file = f"{OUTPUT_DIR}/accounts.json"
    if Path(accounts_file).exists():
        with open(accounts_file, "r") as f:
            try:
                accounts = json.load(f)
            except:
                accounts = []
    
    accounts.append(account_data)
    
    with open(accounts_file, "w") as f:
        json.dump(accounts, f, indent=2)
    
    with open(f"{OUTPUT_DIR}/accounts.txt", "a") as f:
        f.write(f"{email} | {PASSWORD} | user_id: {cookies.get('user_id')}\n")
    
    log(f"💾 Account salvato")

def main():
    log("=" * 60)
    log("🚀 BROWSERLESS ACCOUNT CREATOR (REST API)")
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
                log(f"⚠️ Fallito con questa chiave")
                time.sleep(3)
        
        if not success:
            log(f"❌ Account {i+1} fallito")
        
        if i < num_accounts - 1:
            pause = random.randint(30, 60)
            log(f"⏸️ Pausa di {pause} secondi...")
            time.sleep(pause)
    
    log("\n" + "=" * 60)
    log(f"🏁 PROCESSO COMPLETATO!")
    log(f"✅ Account creati: {success_count}/{num_accounts}")
    log("=" * 60)

if __name__ == "__main__":
    main()
