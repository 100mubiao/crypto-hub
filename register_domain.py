#!/usr/bin/env python3
"""
DigitalPlat FreeDomain (.us.kg) domain auto-registration script.

Usage:
  export DOMAIN_PASSWORD="your_password"
  python3 register_domain.py              # headful (visible browser)
  python3 register_domain.py --headless   # headless
  python3 register_domain.py --prompt     # interactive password
"""

import argparse
import getpass
import os
import re
import sys
import time

CONFIG = {
    "USER_EMAIL": "wisepound@163.com",
    "USER_NAME": "Wang Zhuo",
    "DOMAIN_PREFIX": "cryptodata",
    "DOMAIN_EXT": ".us.kg",
    "NS1": "ns1.cloudflare.com",
    "NS2": "ns2.cloudflare.com",
    "NS3": "",
    "NS4": "",
    "BASE_URL": "https://dash.domain.digitalplat.org",
}


def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")


def prompt_password() -> str:
    pw = os.environ.get("DOMAIN_PASSWORD")
    if pw:
        return pw
    if "--prompt" in sys.argv:
        return getpass.getpass("Enter your DigitalPlat password: ")
    print("ERROR: Password not found.")
    print("  Set DOMAIN_PASSWORD environment variable or use --prompt flag.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Register .us.kg domain via DigitalPlat")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--prompt", action="store_true", help="Prompt for password interactively")
    parser.add_argument("--email", help="Override USER_EMAIL from config")
    parser.add_argument("--prefix", help="Override DOMAIN_PREFIX from config")
    args = parser.parse_args()

    password = prompt_password()
    email = args.email or CONFIG["USER_EMAIL"]
    prefix = args.prefix or CONFIG["DOMAIN_PREFIX"]
    full_domain = f"{prefix}{CONFIG['DOMAIN_EXT']}"

    log(f"目标域名: {full_domain}")
    log(f"账号邮箱: {email}")
    log(f"NS: {CONFIG['NS1']}, {CONFIG['NS2']}")

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout
    except ImportError:
        log("Playwright not installed. Run: pip3 install playwright && python3 -m playwright install chromium")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=args.headless,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="en-US",
            timezone_id="America/New_York",
        )
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)
        page = context.new_page()
        page.set_default_timeout(30000)

        try:
            log("Step 1/4: Opening login page...")
            page.goto(f"{CONFIG['BASE_URL']}/auth/login", wait_until="networkidle")
            time.sleep(2)

            if full_domain in page.url or "/domains" in page.url or "/dashboard" in page.url:
                log("  Already logged in, skipping login step.")
            else:
                email_input = page.locator('input[type="email"]').first
                if email_input.count() == 0:
                    email_input = page.get_by_placeholder("you@example.com").first
                email_input.fill(email)

                pw_input = page.locator('input[type="password"]').first
                if pw_input.count() == 0:
                    pw_input = page.get_by_placeholder("Password").first
                pw_input.fill(password)

                time.sleep(1)
                login_btn = page.get_by_role("button", name="Login").first
                if login_btn.count() == 0:
                    login_btn = page.get_by_role("button", name=re.compile("登录|Sign")).first
                if login_btn.count() == 0:
                    login_btn = page.locator("button[type='submit']").first
                
                if login_btn.is_disabled():
                    page.locator("text=By continuing").first.click()
                    time.sleep(0.5)

                login_btn.click()
                log("  Waiting for login redirect...")
                
                try:
                    page.wait_for_url(lambda url: "/domains" in url or "/dashboard" in url or "/panel" in url, timeout=20000)
                    log("  Login successful!")
                except PwTimeout:
                    current = page.url
                    log(f"  Post-login URL: {current}")
                    if "login" not in current:
                        log("  Seems logged in.")
                    else:
                        err = page.locator(".error, .alert-danger, [role='alert']").first
                        if err.count() and err.is_visible():
                            log(f"  Login failed: {err.text_content()}")
                        page.screenshot(path="/tmp/login_state.png")

            log("Step 2/4: Navigating to domain registration page...")
            page.goto(f"{CONFIG['BASE_URL']}/registration", wait_until="networkidle")
            time.sleep(3)

            if "login" in page.url:
                log("  Session expired. Please check credentials.")
                browser.close()
                sys.exit(1)

            log(f"Step 3/4: Checking availability for {full_domain}...")

            name_input = page.locator('input[name="name"]').first
            if name_input.count() == 0:
                name_input = page.get_by_placeholder("Domain name").first
            if name_input.count() > 0:
                name_input.fill(prefix)

            ext_select = page.locator("select").first
            if ext_select.count() > 0:
                ext_select.select_option(CONFIG["DOMAIN_EXT"])

            terms_cb = page.locator('input[type="checkbox"]').first
            if terms_cb.count() > 0 and not terms_cb.is_checked():
                terms_cb.check()

            time.sleep(1)
            check_btn = page.get_by_role("button", name=re.compile("Check", re.IGNORECASE)).first
            if check_btn.count() == 0:
                check_btn = page.locator("button[type='submit']").first
            if check_btn.count() > 0:
                check_btn.click()
            else:
                log("  Check button not found.")
                page.screenshot(path="/tmp/check_page.png")

            time.sleep(5)
            try:
                page.wait_for_url(lambda url: "check" in url or "buy" in url or "checkout" in url, timeout=15000)
            except PwTimeout:
                pass

            current_page = page.url
            log(f"  Current page: {current_page}")

            if "check" in current_page or "buy" in current_page or "checkout" in current_page:
                log("Step 4/4: Filling nameservers and submitting registration...")

                ns_mapping = {"ns1": CONFIG["NS1"], "ns2": CONFIG["NS2"], "ns3": CONFIG["NS3"], "ns4": CONFIG["NS4"]}
                for key, value in ns_mapping.items():
                    if not value:
                        continue
                    ns_input = page.locator(f'input[name="{key}"]').first
                    if ns_input.count() == 0:
                        ns_input = page.get_by_placeholder(key.upper()).first
                    if ns_input.count() > 0:
                        ns_input.fill(value)

                time.sleep(1)
                register_btn = page.get_by_role("button", name=re.compile("Register|Submit|Confirm", re.IGNORECASE)).first
                if register_btn.count() == 0:
                    register_btn = page.locator("button[type='submit']").first
                
                if register_btn.count() > 0:
                    register_btn.click()
                    log("  Submitting registration...")
                    time.sleep(5)

                    try:
                        page.wait_for_url(lambda url: "success" in url or "domain" in url or "overview" in url, timeout=20000)
                    except PwTimeout:
                        pass

                    page.screenshot(path="/tmp/register_result.png")
                    body_text = page.locator("body").text_content()
                    if "success" in body_text.lower() or "congratulations" in body_text.lower() or "registered" in body_text.lower():
                        log(f"  Domain {full_domain} registered successfully!")
                    elif "already" in body_text.lower() or "taken" in body_text.lower():
                        log(f"  Domain {full_domain} may already be taken.")
                    else:
                        log(f"  Registration status unknown. Check screenshot: /tmp/register_result.png")
                else:
                    log("  Register button not found.")
                    page.screenshot(path="/tmp/register_no_btn.png")
            else:
                body_text = page.locator("body").text_content()
                if "unavailable" in body_text.lower() or "taken" in body_text.lower() or "already" in body_text.lower():
                    log(f"  Domain {full_domain} is unavailable.")
                elif "available" in body_text.lower():
                    log(f"  Domain {full_domain} is available but page format unexpected.")
                    page.screenshot(path="/tmp/available_page.png")
                else:
                    log(f"  Availability check result unknown.")
                    page.screenshot(path="/tmp/unknown_state.png")

            log("Done! Browser stays open for 10s for inspection...")
            time.sleep(10)

        except Exception as e:
            log(f"❌ 出错: {e}")
            page.screenshot(path="/tmp/register_error.png")
            log(f"错误截图已保存: /tmp/register_error.png")
            raise
        finally:
            browser.close()


if __name__ == "__main__":
    main()
