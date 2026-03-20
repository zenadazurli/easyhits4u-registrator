#!/usr/bin/env python3
# app.py - Versione con SeleniumBase per Render

import time
import json
import random
import os
from datetime import datetime
from pathlib import Path
from seleniumbase import Driver
from turnstile_solver import solve

# ==================== CONFIGURAZIONE ====================
PASSWORD = os.environ.get('ACCOUNT_PASSWORD', 'Test123!@#')
OUTPUT_DIR = "/tmp/easyhits4u"

TURNSTILE_SITEKEY = "0x4AAAAAACHvZWqiG5m87_NE"
REFERER_URL = "https://www.easyhits4u.com/?ref=nicolacaporale"
JOIN_URL = "https://www.easyhits4u.com/?join_popup_show=1"

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {msg}", flush=True)

def setup_output_dir():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def generate_username():
    syllables = ["ka","lo","mi","ta","ne","za","ga","ra","chi","lu","no","be","ce","re","di","sa"]
    count = random.randint(3, 5)
    return "u" + "".join(random.choice(syllables) for _ in range(count))

def create_account(username, email):
    """Crea account usando SeleniumBase"""
    log(f"🚀 Avvio browser con SeleniumBase...")
    
    driver = None
    try:
        # Configurazione per Render (headless)
        driver = Driver(
            uc=True,
            headless=True,  # Su Render deve essere headless
            headless2=True,  # Alternativa headless
            disable_csp=True,
            disable_js=True,
            no_sandbox=True,
            disable_gpu=True,
            window_size=(1920, 1080)
        )
        
        # Naviga alla pagina
        log("🌐 Navigazione alla pagina...")
        driver.get(REFERER_URL)
        time.sleep(3)
        
        # Clicca sul link di registrazione
        log("🔗 Clicco sul link di registrazione...")
        join_link = driver.find_element("css selector", "a[href*='join_popup_show']")
        join_link.click()
        time.sleep(3)
        
        # Compila il form
        log("📝 Compilazione form...")
        driver.find_element("css selector", "#reg_form #name").send_keys(username)
        driver.find_element("css selector", "#reg_form #email").send_keys(email)
        driver.find_element("css selector", "#reg_form #login").send_keys(username)
        driver.find_element("css selector", "#reg_form #pass").send_keys(PASSWORD)
        driver.find_element("css selector", "#reg_form #cpass").send_keys(PASSWORD)
        
        # Risolvi Turnstile
        log("🛡️ Risoluzione Turnstile...")
        success = solve(
            driver,
            sitekey=TURNSTILE_SITEKEY,
            detect_timeout=15,
            solve_timeout=60,
            verify=True
        )
        
        if not success:
            log("❌ Risoluzione Turnstile fallita")
            return None
        
        # Invia il form
        log("📤 Invio form...")
        submit_btn = driver.find_element("css selector", "#reg_form input[type='submit']")
        submit_btn.click()
        time.sleep(5)
        
        # Verifica registrazione
        cookies = driver.get_cookies()
        cookie_dict = {c['name']: c['value'] for c in cookies}
        
        if 'user_id' in cookie_dict:
            log(f"✅ Registrazione riuscita! user_id: {cookie_dict['user_id']}")
            return cookie_dict
        else:
            log("❌ Registrazione fallita - user_id non trovato")
            driver.save_screenshot(f"{OUTPUT_DIR}/error_{username}.png")
            return None
            
    except Exception as e:
        log(f"❌ Errore: {e}")
        if driver:
            driver.save_screenshot(f"{OUTPUT_DIR}/crash_{username}.png")
        return None
    finally:
        if driver:
            driver.quit()
            log("🔚 Browser chiuso")

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
    log("🚀 ACCOUNT CREATOR CON SELENIUMBASE")
    log("=" * 60)
    
    setup_output_dir()
    
    try:
        num_accounts = int(os.environ.get('NUM_ACCOUNTS', '1'))
    except:
        num_accounts = 1
    
    log(f"📊 Account da creare: {num_accounts}")
    
    success_count = 0
    
    for i in range(num_accounts):
        log(f"\n{'='*60}")
        log(f"📝 CREAZIONE ACCOUNT {i+1}/{num_accounts}")
        log(f"{'='*60}")
        
        username = generate_username()
        email = f"{username}@spaces0.com"
        
        log(f"👤 Username: {username}")
        log(f"📧 Email: {email}")
        
        cookies = create_account(username, email)
        
        if cookies and 'user_id' in cookies:
            save_account(username, email, cookies)
            success_count += 1
        else:
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
