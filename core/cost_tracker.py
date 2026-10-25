"""Cost tracker: data/cost_log.csv - Method 2 automatic logging.
Method 1 (manual, README): OpenAI dashboard Usage, billing alerts $10/$15/$20, check weekly.
"""
import csv, os
from datetime import datetime, date, timedelta
import config

def _path():
    d = os.path.join(config.DATA_DIR); os.makedirs(d, exist_ok=True)
    return os.path.join(d, "cost_log.csv")
COLUMNS = ["Date","Task Type","Model","Prompt Tokens","Completion Tokens","Estimated Cost","Notes"]
def _ensure():
    p=_path()
    if not os.path.exists(p):
        with open(p,"w",newline="",encoding="utf-8") as f: csv.writer(f).writerow(COLUMNS)
    return p
def estimate_cost(model, prompt_tokens, completion_tokens):
    price = config.MODEL_PRICES_PER_1K.get(model)
    if price is None: return None
    try: pt, ct = float(prompt_tokens or 0), float(completion_tokens or 0)
    except Exception: return None
    return round(pt/1000*price[0] + ct/1000*price[1], 6)
def append_row(date_str, task_type, model, prompt_tokens, completion_tokens, cost, notes=""):
    p=_ensure()
    cost_str = "n/a (price not configured)" if cost is None else f"{cost:.4f}" if isinstance(cost,(int,float)) else str(cost)
    with open(p,"a",newline="",encoding="utf-8") as f:
        csv.writer(f).writerow([date_str, task_type, model, prompt_tokens or "", completion_tokens or "", cost_str, notes])
def record_run(task_type, crew=None, notes="", model=None, prompt_tokens=None, completion_tokens=None):
    # Try to read usage from crew object if available
    if crew is not None:
        um = getattr(crew, "usage_metrics", None) or {}
        if isinstance(um, dict):
            prompt_tokens = prompt_tokens if prompt_tokens is not None else um.get("prompt_tokens","")
            completion_tokens = completion_tokens if completion_tokens is not None else um.get("completion_tokens","")
    model = model or config.DEFAULT_MODEL
    cost = estimate_cost(model, prompt_tokens, completion_tokens) if (prompt_tokens not in (None,"") or completion_tokens not in (None,"")) else None
    append_row(date.today().isoformat(), task_type, model, prompt_tokens, completion_tokens, cost, notes)
    return cost
def read_rows():
    p=_path()
    if not os.path.exists(p): return []
    with open(p, newline="", encoding="utf-8") as f: return list(csv.DictReader(f))
def _cost_of(row):
    try: return float(row.get("Estimated Cost",""))
    except Exception: return 0.0
def totals():
    rows=read_rows(); today=date.today()
    week_start=today-timedelta(days=today.weekday())
    w=sum(_cost_of(r) for r in rows if r.get("Date","")>=week_start.isoformat())
    m=sum(_cost_of(r) for r in rows if r.get("Date","")[:7]==today.isoformat()[:7])
    return {"week": round(w,4), "month": round(m,4), "rows": rows}
def budget_status():
    t=totals(); warn=t["week"]>=config.WEEKLY_BUDGET_USD*config.BUDGET_WARN_FRACTION; over=t["week"]>=config.WEEKLY_BUDGET_USD
    alerts=[a for a in config.BILLING_ALERT_LEVELS_USD if t["month"]>=a]
    return {"week_spend": t["week"], "month_spend": t["month"], "weekly_budget": config.WEEKLY_BUDGET_USD,
            "warn": warn, "over_budget": over, "alerts_crossed": alerts}
def report():
    t=totals(); rows=t["rows"]
    by={}
    for r in rows: by[r.get("Task Type","")]=by.get(r.get("Task Type",""),0)+_cost_of(r)
    return {"week": t["week"], "month": t["month"], "by_task_type": by, "n_runs": len(rows), "budget": budget_status()}
