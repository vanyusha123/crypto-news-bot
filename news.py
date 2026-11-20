import os, re, json, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

COINS = {
    "bitcoin": ["BTC", "Bitcoin"], "ethereum": ["ETH", "Ethereum"],
    "solana": ["SOL", "Solana"], "ripple": ["XRP", "Ripple"],
    "dogecoin": ["DOGE", "Dogecoin"], "shiba-inu": ["SHIB", "Shiba"],
    "pepe": ["PEPE", "Pepe"], "bonk": ["BONK", "Bonk"],
    "dogwifcoin": ["WIF", "dogwifhat"], "floki": ["FLOKI", "Floki"],
    "toncoin": ["TON", "Toncoin"], "cardano": ["ADA", "Cardano"],
    "binancecoin": ["BNB"], "sui": ["SUI"],
    "chainlink": ["LINK", "Chainlink"], "avalanche-2": ["AVAX", "Avalanche"],
    "tron": ["TRX", "Tron"], "litecoin": ["LTC", "Litecoin"],
}

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read()

def fmt(v):
    return f"{v:,.2f}" if v >= 1 else f"{v:.8f}"

def mentioned(title):
    found = []
    for cid, keys in COINS.items():
        for k in keys:
            flags = 0 if k.isupper() else re.I
            if re.search(r"\b" + re.escape(k) + r"\b", title, flags):
                found.append(cid)
                break
    return found

def send(text):
    data = urllib.parse.urlencode({
        "chat_id": CHAT, "text": text,
        "disable_web_page_preview": "true"}).encode()
    urllib.request.urlopen(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage", data, timeout=30)

TOKEN = os.environ["TOKEN"].strip()
CHAT = os.environ["CHAT"].strip()

ids = ",".join(COINS)
prices = json.loads(get(
    "https://api.coingecko.com/api/v3/simple/price?ids=" + ids +
    "&vs_currencies=usd&include_24hr_change=true"))

root = ET.fromstring(get("https://cointelegraph.com/rss"))
for it in root.findall(".//item")[:5]:
    title = it.findtext("title")
    ids_found = mentioned(title) or ["bitcoin", "ethereum"]
    lines = []
    for cid in ids_found:
        p = prices.get(cid)
        if p:
            lines.append(f"{COINS[cid][0]} ${fmt(p['usd'])} ({p.get('usd_24h_change', 0):+.1f}% за 24ч)")
    send(f"{title}\n{it.findtext('link')}\n\n" + "\n".join(lines))

try:
    t = json.loads(get("https://api.coingecko.com/api/v3/search/trending"))
    rows = [f"{c['item']['symbol']} — {c['item']['name']}" for c in t["coins"][:7]]
    send("Трендовые монеты CoinGecko сейчас:\n" + "\n".join(rows))
except Exception as e:
    print("trending failed:", e)
