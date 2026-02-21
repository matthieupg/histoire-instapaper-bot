import os
import random
import requests
from requests.auth import HTTPBasicAuth
from playwright.sync_api import sync_playwright

HC_COOKIE = os.environ["HC_COOKIE"]
INSTAPAPER_USERNAME = os.environ["INSTAPAPER_USERNAME"]
INSTAPAPER_PASSWORD = os.environ["INSTAPAPER_PASSWORD"]

def send_to_instapaper(url):
    requests.post(
        "https://www.instapaper.com/api/add",
        data={"url": url},
        auth=HTTPBasicAuth(INSTAPAPER_USERNAME, INSTAPAPER_PASSWORD),
        timeout=30
    )

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()

    context.add_cookies([{
        "name": "magellan",
        "value": HC_COOKIE,
        "domain": "www.histoire-et-civilisations.com",
        "path": "/"
    }])

    page = context.new_page()
    page.goto("https://www.histoire-et-civilisations.com", timeout=60000)

    page.evaluate("""
    () => {
      document.querySelectorAll(
        '.gdpr-glm-standard, iframe, #popin-accueil'
      ).forEach(e => e.remove());
    }
    """)

    page.wait_for_timeout(5000)

    links = page.eval_on_selector_all(
        "article a",
        "els => els.map(e => e.href)"
    )

    links = list(set(links))

    if len(links) >= 3:
        selected = random.sample(links, 3)
    else:
        selected = links

    for url in selected:
        send_to_instapaper(url)

    browser.close()
