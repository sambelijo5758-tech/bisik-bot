import os, requests
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY = os.getenv("VERIFY_TOKEN", "bisik123")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

def ai_reply(text):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        p = f"Kamu BISIK bot keuangan Indonesia. User bilang: '{text}'. Balas singkat, catat sebagai pengeluaran/pemasukan dengan format: Oke dicatat! [kategori] Rp[jumlah] untuk [keperluan]. Jika bukan keuangan, jawab ramah."
        r = model.generate_content(p)
        return r.text
    except Exception as e:
        return f"Dicatat: {text}. (AI error: {e})"

def send_wa(to, msg):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    h = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    d = {"messaging_product":"whatsapp","to":to,"type":"text","text":{"body":msg}}
    requests.post(url, headers=h, json=d)

@app.route("/")
def home():
    return "BISIK hidup!"

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY:
        return request.args.get("hub.challenge")
    return "fail", 403

@app.route("/webhook", methods=["POST"])
def hook():
    data = request.get_json()
    try:
        v = data["entry"][0]["changes"][0]["value"]
        if "messages" in v:
            m = v["messages"][0]
            txt = m.get("text",{}).get("body","")
            frm = m["from"]
            balasan = ai_reply(txt)
            send_wa(frm, balasan)
    except:
        pass
    return jsonify(status="ok")

if __name__ == "__main__":
    app.run()
