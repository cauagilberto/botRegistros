import requests
from config import SUPABASE_URL, SUPABASE_KEY

BASE = f"{SUPABASE_URL.rstrip('/')}/rest/v1/aportes"
H = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}


def _check():
    if not isinstance(SUPABASE_URL, str) or not SUPABASE_URL.startswith("https://"):
        raise RuntimeError("SUPABASE_URL inválida: confira o .env, sem {} nem aspas.")
    if not isinstance(SUPABASE_KEY, str) or not SUPABASE_KEY:
        raise RuntimeError("SUPABASE_KEY inválida: confira o .env, sem {} nem aspas.")


def _get(params):
    _check()
    r = requests.get(BASE, headers=H, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def rows():
    return _get({"select": "*", "order": "date.desc,created_at.desc"})


def has_message(message_id) -> bool:
    return bool(_get({
        "select": "id",
        "tg_message_id": f"eq.{message_id}",
        "limit": 1,
    }))


def add(row: dict):
    _check()
    r = requests.post(
        BASE,
        params={"on_conflict": "id"},
        headers={**H, "Prefer": "resolution=ignore-duplicates,return=representation"},
        json=row,
        timeout=15,
    )
    r.raise_for_status()


def cancel_last(person: str):
    ult = _get({
        "select": "*",
        "person": f"eq.{person}",
        "status": "eq.ativo",
        "order": "created_at.desc",
        "limit": 1,
    })
    if not ult:
        return None

    row = ult[0]
    r = requests.patch(
        BASE,
        params={"id": f"eq.{row['id']}"},
        headers={**H, "Prefer": "return=representation"},
        json={"status": "cancelado"},
        timeout=15,
    )
    r.raise_for_status()
    return row