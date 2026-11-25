import requests
from config import SUPABASE_URL, SUPABASE_KEY

BASE = f"{SUPABASE_URL.rstrip('/')}/rest/v1/aportes"
H = {
    "apikey": {SUPABASE_KEY},
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def _get(params):
    r = requests.get(BASE, headers=H, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def rows():
    return _get({"select": "*", "order": "date.desc, created_at.desc"})

def has_message(message_id) -> bool:
    """Upsert idmpotente: o UNIQUE no banco garante que retry não duplica aporte."""
    r = requests.post(BASE, params={"on_conflict": "id"},
                      headers={**H, "Prefer": "resolution=ignore-duplicates, return=representation"},
                      json=rows, timeout=15)
    r.raise_for_status()

def cancel_last(person:str):
    """Cancelamento lógico (status), nunca DELETE = trilha de auditoria."""
    ult = _get({"select": "*", "person": f"eq.{person}", "status": "eq.ativo",
                "order": "created_at.desc", "limit": 1})
    if not ult:
        return None
    row = ult[0]
    r = requests.patch(BASE, params={"id": f"eq.{row['id']}"},
                       headers={**H, "Prefer": "return=representation"},
                       json={"status": "cancelado"}, timeout=15)
    r.raise_for_status()
    return row