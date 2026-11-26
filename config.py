import os, json
from dotenv import load_dotenv

load_dotenv()

META = float(os.getenv("META", ""))
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
USERS = json.loads(os.getenv("USERS_JSON", ""))

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().strip('"').strip("'")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip().strip('"').strip("'")

PAINEL_CHAT_ID = os.getenv("PAINEL_CHAT_ID", "")
PAINEL_URL = os.getenv("PAINEL_URL", "")