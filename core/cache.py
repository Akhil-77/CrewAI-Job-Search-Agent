"""File-based company research cache in data/cache/ with TTL."""
import json, os, re
from datetime import datetime, timedelta
import config
def _dir(): d=os.path.join(config.DATA_DIR,"cache"); os.makedirs(d, exist_ok=True); return d
def slugify(name): return re.sub(r"[^a-z0-9]+","_", (name or "").lower()).strip("_")
def _file(company): return os.path.join(_dir(), f"company_{slugify(company)}.json")
def save_company_research(company_name, research_data):
    data=dict(research_data or {}); data.setdefault("created_at", datetime.now().isoformat()); data.setdefault("ttl_days", config.CACHE_TTL_DAYS)
    with open(_file(company_name),"w",encoding="utf-8") as f: json.dump(data,f,indent=2)
    return _file(company_name)
def load_company_research(company_name):
    p=_file(company_name)
    if not os.path.exists(p): return None
    with open(p,encoding="utf-8") as f: data=json.load(f)
    if is_stale(data): return None
    return data
def is_stale(data):
    try:
        created=datetime.fromisoformat(data.get("created_at","")); ttl=int(data.get("ttl_days", config.CACHE_TTL_DAYS))
        return datetime.now()-created>timedelta(days=ttl)
    except Exception: return True
def list_cache():
    out=[]
    for fn in os.listdir(_dir()):
        if fn.endswith(".json"): out.append(fn)
    return out
def clear_cache(company=None):
    if company:
        p=_file(company)
        if os.path.exists(p): os.remove(p)
    else:
        for fn in list_cache(): os.remove(os.path.join(_dir(),fn))
