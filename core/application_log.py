"""Application/activity log: data/application_log.csv. Schema defined in Part 4, used by Part 5."""
import csv, os
from datetime import datetime, timedelta, date
import config
COLUMNS=["id","logged_at","activity_type","company","role","platform","industry","role_level","ai_generated","edit_level","config_variant","response","response_days","interview","quality_score","cost_estimate","notes"]
ALIASES={"angellist":"wellfound"}
def _path(): d=config.DATA_DIR; os.makedirs(d, exist_ok=True); return os.path.join(d,"application_log.csv")
def _ensure():
    p=_path()
    if not os.path.exists(p):
        with open(p,"w",newline="",encoding="utf-8") as f: csv.writer(f).writerow(COLUMNS)
    return p
def _rows():
    p=_ensure()
    with open(p,newline="",encoding="utf-8") as f: return list(csv.DictReader(f))
def _write(rows):
    p=_path()
    with open(p,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=COLUMNS); w.writeheader(); w.writerows(rows)
def add_entry(**fields):
    rows=_rows(); nid=max([int(r["id"]) for r in rows if r.get("id")], default=0)+1
    row={c:"" for c in COLUMNS}; row["id"]=str(nid); row["logged_at"]=fields.pop("logged_at", datetime.now().isoformat(timespec="seconds"))
    plat=fields.get("platform","")
    if plat: fields["platform"]=ALIASES.get(str(plat).lower(), plat)
    for k,v in fields.items():
        if k in COLUMNS: row[k]=str(v) if v is not None else ""
    if not row["activity_type"]: row["activity_type"]="application"
    if not row["config_variant"]: row["config_variant"]="baseline"
    rows.append(row); _write(rows); return nid
def list_entries(filters=None):
    rows=_rows()
    if filters:
        for k,v in filters.items():
            rows=[r for r in rows if str(r.get(k,""))==str(v)]
    return rows
def get_entry(entry_id):
    for r in _rows():
        if str(r["id"])==str(entry_id): return r
    return None
def count_in_window(activity_type=None, platform=None, since=None):
    rows=_rows(); n=0
    for r in rows:
        if activity_type and r.get("activity_type")!=activity_type: continue
        if platform and r.get("platform") not in (platform, ALIASES.get(platform,platform)): continue
        if since and r.get("logged_at","")<since: continue
        n+=1
    return n
def last_entry(activity_type=None):
    rows=[r for r in _rows() if not activity_type or r.get("activity_type")==activity_type]
    return rows[-1] if rows else None
def update_entry(entry_id, **fields):
    allowed={"response","response_days","interview","quality_score","edit_level","notes","industry","role_level","config_variant","ai_generated","cost_estimate"}
    for k in fields:
        if k not in allowed: raise ValueError(f"Unknown column {k}")
    rows=_rows()
    for r in rows:
        if str(r["id"])==str(entry_id):
            for k,v in fields.items(): r[k]=str(v) if v is not None else ""
            _write(rows); return r
    return None
def entries_between(start, end):
    return [r for r in _rows() if start <= r.get("logged_at","")[:10] <= end]
