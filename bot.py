import os
import random
import requests
from requests.auth import HTTPBasicAuth
from playwright.sync_api import sync_playwright

HC_COOKIE = os.environ["HC_COOKIE"]
INSTAPAPER_USERNAME = os.environ["INSTAPAPER_USERNAME"]
INSTAPAPER_PASSWORD = os.environ["INSTAPAPER_PASSWORD"]

def send_html_to_instapaper(title, html, url):
    response = requests.post(
        "https://www.instapaper.com/api/add",
        data={
            "url": url,
            "title": title,
            "content": html
        },
        auth=HTTPBasicAuth(INSTAPAPER_USERNAME, INSTAPAPER_PASSWORD),
        timeout=60
    )
    response.raise_for_status()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()

    # Injecter le cookie abonné
    context.add_cookies([{
        "name": "magellan",
        "value": HC_COOKIE,
        "domain": "www.histoire-et-civilisations.com",
        "path": "/"
    }])

    page = context.new_page()
    page.goto("https://www.histoire-et-civilisations.com", timeout=60000)

    # Supprimer overlays (cookies + popup accueil)
    page.evaluate("""
    () => {
      document.querySelectorAll(
        '.gdpr-glm-standard, iframe, #popin-accueil'
      ).forEach(e => e.remove());
    }
    """)

    page.wait_for_timeout(4000)

    # Récupérer tous les liens d’articles depuis la homepage
    links = page.eval_on_selector_all(
        "article a",
        "els => els.map(e => e.href)"
    )

    links = list(set(links))

    if len(links) >= 3:
        selected = random.sample(links, 3)
    else:
        selected = links

    # Ouvrir chaque article, extraire le HTML réel, envoyer à Instapaper
    for url in selected:
        page.goto(url, timeout=60000)
        page.wait_for_selector("article", timeout=30000)

        title = page.title()
        html = page.eval_on_selector("article", "el => el.innerHTML")

        send_html_to_instapaper(title, html, url)

    browser.close()
