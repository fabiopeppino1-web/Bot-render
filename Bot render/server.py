from flask import Flask, request, abort, jsonify
import requests
import os

app = Flask(__name__)

# --- CONFIGURAZIONE ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")  # es. "CHANGE_ME_SECRET"

# --- FUNZIONE PER INVIARE MESSAGGI TELEGRAM ---
def send_telegram(text: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("⚠️  TELEGRAM_TOKEN o CHAT_ID non impostati")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code != 200:
            print("⚠️  Errore Telegram API:", r.status_code, r.text)
    except Exception as e:
        print("⚠️  Eccezione Telegram:", e)

# --- ENDPOINT PRINCIPALE /WEBHOOK ---
@app.post("/webhook")
def webhook():
    data = request.get_json(force=True, silent=True) or {}

    # Verifica del secret (se impostato)
    if WEBHOOK_SECRET and data.get("secret") != WEBHOOK_SECRET:
        print("❌ Secret non valido, rifiuto la richiesta")
        abort(403)

    symbol = data.get("symbol", "UNKNOWN")
    signal = data.get("signal_type", "NONE")
    rsi = data.get("rsi", "?")

    msg = f"📈 <b>{symbol}</b>\nSignal: <b>{signal}</b>\nRSI: {rsi}"
    send_telegram(msg)

    return jsonify({"ok": True}), 200

# --- ENDPOINT DI TEST (PING E HEALTH) ---
@app.get("/ping")
def ping():
    """Endpoint per controllare che il bot sia attivo."""
    return jsonify({"status": "pong"}), 200

@app.get("/health")
def health():
    """Endpoint usato per verificare lo stato del servizio."""
    return jsonify({"status": "ok"}), 200

# --- AVVIO LOCALE (Render usa Gunicorn) ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
