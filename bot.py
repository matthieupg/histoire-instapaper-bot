import os
import random
import smtplib
from email.message import EmailMessage
from playwright.sync_api import sync_playwright

HC_EMAIL = os.environ["HC_EMAIL"]
HC_PASSWORD = os.environ["HC_PASSWORD"]
INSTAPAPER = os.environ["INSTAPAPER_EMAIL"]

def send_to_instapaper(url):
    msg = EmailMessage()
    msg["From"] = INSTAPAPER
    msg["To"] = INSTAPAPER
    msg["Subject"] = url
    msg.set_content(url)

    with smtplib.SMTP("localhost") as s:
        s.send_message(msg)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("https://www.histoire-et-civilisations.com")

    page.click("text=Se connecter")
    page.fill("input[type=email]", HC_EMAIL)
    page.fill("input[type=password]", HC_PASSWORD)
    page.click("button[type=submit]")

    page.wait_for_timeout(5000)

    links = page.eval_on_selector_all(
        "article a",
        "els => els.map(e => e.href)"
    )

    links = list(set(links))
    selected = random.sample(links, 3)

    for url in selected:
        send_to_instapaper(url)

    browser.close()
