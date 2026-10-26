import os
import json
import requests
import feedparser
from urllib.parse import quote

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

BUSQUEDAS = [
    "SEAT Martorell",
    "SEAT convenio",
    "SEAT ERTE",
    "CUPRA Martorell",
    "SEAT producción",
]

SEEN_FILE = "seen.json"


def cargar_vistos():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    return None


def guardar_vistos(vistos):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(vistos), f)


def enviar(texto):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": texto},
        timeout=30,
    )


def main():
    vistos = cargar_vistos()
    primera_vez = vistos is None
    vistos = vistos or set()
    nuevas = []

    for q in BUSQUEDAS:
        url = (
            "https://news.google.com/rss/search?q="
            + quote(q)
            + "+when:1d&hl=es&gl=ES&ceid=ES:es"
        )
        for e in feedparser.parse(url).entries:
            if e.link not in vistos:
                vistos.add(e.link)
                nuevas.append(f"📰 {e.title}\n{e.link}")

    if not primera_vez:
        for n in nuevas:
            enviar(n)

    guardar_vistos(vistos)


if __name__ == "__main__":
    main()

