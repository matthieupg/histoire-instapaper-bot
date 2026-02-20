import os
import random
import requests
from playwright.sync_api import sync_playwright

HC_COOKIE = os.environ["HC_COOKIE"]
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

    # injecter cookie magellan
    context.add_cookies([{
        "name": "magellan",
        "value": HC_COOKIE,
        "domain": "www.histoire-et-civilisations.com",
        "path": "/"
    }])

    page = context.new_page()
    page.goto("https://www.histoire-et-civilisations.com", timeout=60000)

    # supprimer overlays éventuels
    page.evaluate("""
    () => {
      document.querySelectorAll(
        '.gdpr-glm-standard, iframe, #popin-accueil'
      ).forEach(e => e.remove());
    }
    """)

    page.wait_for_timeout(5000)

    #
