import re
from datetime import date, datetime, timezone
from config import META, USERS
from core import store

AJUDA = (
    "Comandos:\n"
    "/aporte [valor] - registra um depósito \n"
    "/total - progesso atual da meta \n"
    "/desfazer - cancela o último aporte \n"
    "/ajuda - repete esta mensagem"
)

def brl(v): return ("R$ " + f"{v:,.2f}").replace(",", "X").replace(".", ",").replace("X", ".")

def to_float(s):
    s = str(s).replace("R$", "").strip()
    if "," in s: s=s.replace(".", "").replace(",", ".")
    return float(s)

def _interpretar(text):
    t = text.strip()
    parts = t.split()
    if not parts:
        return "", []
    cmd = parts[0].split("@")[0].lower()
    if cmd.startswith("/"):
        return cmd, parts[1:]
    m = re.match(r"^(?:aportei|depositei|guardei|aporte)?\s*(?:r\$\s*)?([\d.,]+)\s*(.*)$",t, re.IGNORECASE)
    if m:
        return "/aporte", [m.group(1)] + ([m.group(2)] if m.group(2) else [])
    return cmd, parts[1:]

def muta_estado(text) -> bool:
    return _interpretar(text)[0] in ("/aporte", "/desfazer")


def progresso():
    ativos = [r for r in store.rows() if r.get("status") == "ativo"]
    total = sum(float(r["amount"]) for r in ativos)
    por = {}
    for r in ativos:
        por[r["person"]] = por.get(r["person"], 0.0) + float(r["amount"])
    pct = min(total / META, 1.0) if META else 0
    n = round(pct * 10)
    linhas = [f"Meta: {brl[META]}",
              f"Arrecadado: {brl(total)} ({pct:.0%})",
              " " * n + " " * (10 - n)]
    linhas += [f"- {p}: {brl(v)}" for p, v in sorted(por.items())]
    linhas.append(f"Falta: {brl(max(META - total, 0))}")
    return "\n".join(linhas)

def _extrato(n=5):
    ativos = [r for r in store.rows() if r.get("status") == "ativo"][:n]
    if not ativos:
        return "Nenhum aporte ainda."
    return "Últimos aportes:\n" + "\n".join(
        f"{r['date']} - {r['person']} - {brl(float(r['amount']))}" for r in ativos
    )

def handle(text: str, user_id: int, message_id: int) -> str:
    person = USERS.get(str(user_id))
    if not person:
        return f"Bot privado. Seu ID: {user_id} - perça pro admin liberar."
    parts = text.strip().split()
    if not parts: return AJUDA
    cmd, args = parts[0].split("@")[0].lower(), parts[1:]

    if cmd in ("/start", "/ajuda"): return f"Olá, {person}!" + AJUDA
    if cmd == "/total": return progresso()
    if cmd == "/desfazer":
        r = store.cancel_last(person)
        if not r: return "Você não tem aporte ativo para cancelar"
        return f"Cancelado: {brl(float(r['amount']))} de {r['date']}.\n" + progresso()
    if cmd == "/aporte":
        if not args: return "Uso: /aporte [valor]"
        try: valor = to_float(args[0])
        except ValueError: return "Valor inválido. Ex.: /aporte 400 ou /aporte 200"
        if not (0 < valor <= META): return f"Valor deve ser maior que 0 e até {brl(META)}."
        if store.has_message(message_id):
            return "Esse aporte já tinha sido registrado."
        store.add({
            "id": f"bot-{message_id}", "date": date.today().isoformat(),
            "person": person, "amount": valor,
            "description": " ".join(args[1:]) or f"VIAGEM-{person.upper()}",
            "source": "bot", "status": "ativo", "tg_message_id": message_id,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="second"),
        })
        return f"{brl(valor)} registrado para {person}!\n" + progresso()
    return AJUDA