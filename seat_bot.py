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
HEADERS = {"User-Agent": "Mozilla/5.0"}


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
            + "&hl=es&gl=ES&ceid=ES:es"
        )
        r = requests.get(url, headers=HEADERS, timeout=30)
        entradas = feedparser.parse(r.content).entries
        print(q, "-> status", r.status_code, "-> noticias", len(entradas))
        for e in entradas:
            if e.link not in vistos:
                vistos.add(e.link)
                nuevas.append(f"📰 {e.title}\n{e.link}")

    if not primera_vez:
        for n in nuevas:
            enviar(n)

    guardar_vistos(vistos)


if __name__ == "__main__":
    main()
