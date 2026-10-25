"""Friday weekly review + cadence."""
import json, os
import config
from core.time_log import monday_of
def cadence_path(): os.makedirs(config.DATA_DIR, exist_ok=True); return os.path.join(config.DATA_DIR,"cadence.json")
def read_cadence():
    p=cadence_path()
    if not os.path.exists(p): return {}
    with open(p,encoding="utf-8") as f: return json.load(f)
def mark_cadence(kind, when=None):
    from datetime import date; c=read_cadence(); c[kind]=(when or date.today()).isoformat()
    with open(cadence_path(),"w",encoding="utf-8") as f: json.dump(c,f,indent=2); return c
def cadence_status(now=None):
    from datetime import date; now=now or date.today(); c=read_cadence(); out={}
    for kind,days in config.CADENCE_DAYS.items():
        last=c.get(kind)
        if not last: out[kind]="due (never recorded)"
        else:
            delta=(now-date.fromisoformat(last)).days; out[kind]=f"due ({delta} days since last, every {days})" if delta>=days else f"ok ({delta}/{days} days)"
    return out
