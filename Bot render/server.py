from flask import Flask, request, abort, jsonify
import requests
import os

app = Flask(__name__)

# Read secrets from environment (set these on Render)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")  # e.g., "CHANGE_ME_SECRET"

def send_telegram(text: str):
    """Send a message to Telegram chat_id using the bot token."""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("⚠️  TELEGRAM_TOKEN or CHAT_ID not set")
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
            print("⚠️  Telegram API error:", r.status_code, r.text[:500])
    except Exception as e:
        print("⚠️  Telegram exception:", e)

@app.post("/webhook")
def webhook():
    """Endpoint that TradingView will call via Webhook."""
    data = request.get_json(force=True, silent=True) or {}
    # Optional secret check
    if WEBHOOK_SECRET and data.get("secret") != WEBHOOK_SECRET:
        print("❌ SECRET MISMATCH")
        abort(403)

    symbol = data.get("symbol", "UNKNOWN")
    signal = data.get("signal_type", "NONE")
    rsi = data.get("rsi", "?")

    msg = f"📈 <b>{symbol}</b>\nSignal: <b>{signal}</b>\nRSI: {rsi}"
    send_telegram(msg)
    return jsonify({"ok": True}), 200

@app.get("/ping")
def ping():
    """Simple keep-alive endpoint for uptime checks (e.g., UptimeRobot)."""
    return jsonify({"status": "pong"}), 200

@app.get("/health")
def health():
    """Health check endpoint for the platform."""
    return jsonify({"status": "ok"}), 200

# Local dev entrypoint (Render uses gunicorn to run `server:app`)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
