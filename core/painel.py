from datetime import datetime, timedelta, timezone
import requests
from config import BOT_TOKEN, PAINEL_CHAT_ID, PAINEL_URL
from core.bot import progresso

API = f"https://api.telegram.org/bot{BOT_TOKEN}"
BR = timezone(timedelta(hours=-3))

def _call(method, **payload):
    r = requests.post(f"{API}/{method}", json=payload, timeout=10)
    r.raise_for_status()
    return r.json().get("result", {})

def _texto():
    agora = datetime.now(BR).strftime("%d/%m %H:%M")
    return("COFRE VIAGEM\n" + progresso() + f"\n\n {agora}" + (f"\n{PAINEL_URL}" if PAINEL_URL else ""))

def atualizar():
    if not PAINEL_CHAT_ID:
        return
    txt = _texto()
    chat = _call("getChat", chat_id=PAINEL_CHAT_ID)
    pin = (chat.get("pinned_mesage") or {}).get("message_id")
    if pin:
        try:
            _call("editMessageText", chat_id=PAINEL_CHAT_ID, message_id=pin, text=txt)
            return
        except requests.HTTPError as e:
            if "not modified" in e.response.text:
                return
    msg = _call("sendMessage", chat_id=PAINEL_CHAT_ID, text=txt)
    _call("pinChatMessage", chat_id=PAINEL_CHAT_ID,
          message_id=msg["message_id"], disable_notification=True)