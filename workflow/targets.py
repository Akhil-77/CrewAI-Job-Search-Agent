"""Weekly targets: data/weekly_targets.csv"""
import csv, os
import config
COLUMNS=["id","company","role","platform","posting","priority","status","notes"]
def _path(): os.makedirs(config.DATA_DIR, exist_ok=True); return os.path.join(config.DATA_DIR,"weekly_targets.csv")
def _rows():
    p=_path()
    if not os.path.exists(p): return []
    with open(p,newline="",encoding="utf-8") as f: return list(csv.DictReader(f))
def _write(rows):
    with open(_path(),"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=COLUMNS); w.writeheader(); w.writerows(rows)
def add_target(company, role, platform, posting="", priority="", notes=""):
    rows=_rows(); nid=max([int(r["id"]) for r in rows if r.get("id")],default=0)+1
    rows.append({"id":str(nid),"company":company,"role":role,"platform":platform,"posting":posting,"priority":str(priority),"status":"new","notes":notes}); _write(rows); return nid
def list_targets(): return _rows()
def remove_target(tid):
    rows=_rows(); new=[r for r in rows if str(r["id"])!=str(tid)]; _write(new); return len(new)!=len(rows)
def set_status(tid, status):
    rows=_rows()
    for r in rows:
        if str(r["id"])==str(tid): r["status"]=status; _write(rows); return True
    return False
def get_target(tid):
    for r in _rows():
        if str(r["id"])==str(tid): return r
    return None
