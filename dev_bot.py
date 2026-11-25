from config import USERS
from core.bot import handle

uid = int(next(iter(USERS)))
print(f"REPL local como {USERS[str(uid)]}. Ctrl+C sai.")
mid = 1
while True:
    try: txt = input("> ")
    except (EOFError, KeyboardInterrupt): break
    print(handle(txt, uid, mid)); mid += 1