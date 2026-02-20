import os
import random
import requests
from playwright.sync_api import sync_playwright

HC_EMAIL = os.environ["HC_EMAIL"]
HC_PASSWORD = os.environ["HC_PASSWORD"]
INSTAPAPER = os.environ["INSTAPAPER_EMAIL"]

def send_to_instapaper(url):
    requests.post(
        "https://www.instapaper.com/api/add",
        data={
            "url": url,
            "username": INSTAPAPER,
        },
        timeout=30
    )

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.histoire-et-civilisations.com", timeout=60000)

    # accepter cookies
    try:
        page.click("text=Tout accepter", timeout=5000)
    except:
        pass

    # login
    page.click("text=Se connecter")
    page.fill("input[type=email]", HC_EMAIL)
    page.fill("input[type=password]", HC_PASSWORD)
    page.click("button[type=submit]")

    page.wait_for_timeout(5000)

    # récupérer articles homepage
    links = page.eval_on_selector_all(
        "article a",
        "els => els.map(e => e.href)"
    )

    links = list(set(links))
    selected = random.sample(links, 3)

    for url in selected:
        send_to_instapaper(url)

    browser.close()
