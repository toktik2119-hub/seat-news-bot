import os
import json
import time
import requests
import feedparser
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
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
TZ = ZoneInfo("Europe/Madrid")
DESDE = datetime(2026, 10, 1, tzinfo=TZ)  # solo noticias desde esta fecha


def fecha_noticia(e):
    p = e.get("published_parsed")
    if not p:
        return None
    return datetime(*p[:6], tzinfo=timezone.utc).astimezone(TZ)


def cargar_vistos():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def guardar_vistos(vistos):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(vistos), f)


def enviar(texto):
    for _ in range(5):
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": texto},
            timeout=30,
        )
        if r.status_code == 429:
            espera = r.json().get("parameters", {}).get("retry_after", 5)
            time.sleep(espera + 1)
            continue
        return
    

def main():
    vistos = cargar_vistos()
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
            if e.link in vistos:
                continue
            vistos.add(e.link)
            f = fecha_noticia(e)
            if f and f >= DESDE:
                nuevas.append((f, e.title, e.link))

    # Las más antiguas primero
    nuevas.sort(key=lambda x: x[0])
    print("Noticias a enviar:", len(nuevas))

    for f, titulo, link in nuevas:
        enviar(f"📰 {titulo}\n🕒 {f.strftime('%d/%m %H:%M')}\n{link}")
        time.sleep(1)

    guardar_vistos(vistos)


if __name__ == "__main__":
    main()
