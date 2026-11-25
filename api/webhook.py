import json
from http.server import BaseHTTPRequestHandler
import requests
from config import BOT_TOKEN, WEBHOOK_SECRET
from core.bot import handle, muta_estado
from core import painel

API = f"https://api.telegram.org/bot{BOT_TOKEN}"

class handler(BaseHTTPRequestHandler):
    def _ok(self, body=b"ok"):
        self.send_response(200); self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        self._ok(b"Cofre Viagem bot no ar")

    def do_POST(self):
        try:
            #setWebhook faz o telegram mandar o secret webhook
            if self.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
                self.send_response(403); self.end_headers(); return
            update = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            msg = update.get("message") or {}
            chat_id = msg.get("chat", {}).get("id")
            user_id = msg.get("from", {}).get("id")
            text, mid = msg.get("text", ""), msg.get("message_id")
            if chat_id and user_id and text:
                if text.strip().startswith("/chatid"):
                    reply = f"Chat ID: {chat_id}"
                else:
                    try:
                        if text.strip().startswith("/chatid"):
                            reply = f"Chat ID: {chat_id }"
                        reply = handle(text, user_id, mid)
                    except Exception as e:
                        print("Erro no handle:", e)
                        reply = "Falha ao acessar a planilha, tenta de novo aí."
                    requests.post(f"{API}/sendMessage",
                                  json={"chat_id": chat_id, "text": reply}, timeout=10)
                    if muta_estado(text):
                        try:
                            painel.atualzar()
                        except Exception as e:
                            print("painel:", e)
        except Exception as e:
            print("Erro no webHook:", e)
        self._ok() #pra evitar loop de reenvio

