"""Weekly time log: data/time_log.csv"""
import csv, os
from datetime import date, timedelta
import config
COLUMNS=["week_start","hours_spent","hours_saved","notes"]
def _path(): os.makedirs(config.DATA_DIR, exist_ok=True); return os.path.join(config.DATA_DIR,"time_log.csv")
def _rows():
    p=_path()
    if not os.path.exists(p): return []
    with open(p,newline="",encoding="utf-8") as f: return list(csv.DictReader(f))
def _write(rows):
    with open(_path(),"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=COLUMNS); w.writeheader(); w.writerows(rows)
def monday_of(d=None):
    d=d or date.today(); return (d-timedelta(days=d.weekday())).isoformat()
def add_week(hours_spent, hours_saved, week_start=None, notes=""):
    ws=week_start or monday_of(); rows=[r for r in _rows() if r["week_start"]!=ws]
    rows.append({"week_start":ws,"hours_spent":str(hours_spent),"hours_saved":str(hours_saved),"notes":notes}); rows.sort(key=lambda r:r["week_start"]); _write(rows); return ws
def list_weeks(): return _rows()
def average_hours(weeks=4):
    rows=_rows()[-weeks:]
    if not rows: return {"avg_spent":None,"avg_saved":None}
    return {"avg_spent": round(sum(float(r["hours_spent"]) for r in rows)/len(rows),2), "avg_saved": round(sum(float(r["hours_saved"]) for r in rows)/len(rows),2)}
