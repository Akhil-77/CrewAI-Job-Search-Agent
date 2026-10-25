"""Metrics from application log. Definitions:
Applications sent = activity_type=application in period.
Eligible = resolved response OR logged > RESPONSE_WAIT_DAYS ago.
Response rate = eligible with response=Yes / eligible. Interview rate similarly.
Time saved/week = average hours_saved from time log. Quality = mean quality_score.
Cost per application = sum cost_estimate / apps; fallback cost-log total / apps, labeled by source.
"""
import csv, os
from datetime import datetime, timedelta, date
import config
from core import application_log as log
from core import time_log

def _in_period(rows, period):
    if period=="all" or not period: return rows
    today=date.today()
    if period=="week": start=today-timedelta(days=today.weekday())
    elif period=="month": start=today.replace(day=1)
    else: return rows
    return [r for r in rows if r.get("logged_at","")[:10]>=start.isoformat()]

def _eligible(rows):
    out=[]; cutoff=date.today()-timedelta(days=config.RESPONSE_WAIT_DAYS)
    for r in rows:
        if r.get("response") in ("Yes","No"): out.append(r); continue
        try:
            d=date.fromisoformat(r.get("logged_at","")[:10])
            if d<=cutoff: out.append(r)
        except Exception: pass
    return out

def compute_metrics(period="month", filters=None):
    rows=[r for r in log.list_entries(filters) if r.get("activity_type")=="application"]
    rows=_in_period(rows, period)
    elig=_eligible(rows)
    n=len(rows); ne=len(elig)
    resp=sum(1 for r in elig if r.get("response")=="Yes"); intr=sum(1 for r in elig if r.get("interview")=="Yes")
    rated=[float(r["quality_score"]) for r in rows if r.get("quality_score") not in ("",None)]
    # cost
    costs=[float(r["cost_estimate"]) for r in rows if r.get("cost_estimate") not in ("",None)]
    cost_source="log_estimates"
    if costs and n: cpa=round(sum(costs)/n,4)
    else:
        # fallback to cost log
        from core import cost_tracker; tot=cost_tracker.totals()
        total=tot["month"] if period=="month" else tot["week"] if period=="week" else sum(cost_tracker._cost_of(r) for r in tot["rows"])
        cpa=round(total/n,4) if n and total else None; cost_source="cost_log_fallback" if n and total else "n/a"
    avg=time_log.average_hours()
    return {"n_applications":n,"n_eligible":ne,"n_rated":len(rated),
            "response_rate": round(resp/ne,4) if ne else None, "interview_rate": round(intr/ne,4) if ne else None,
            "time_saved_per_week": avg.get("avg_saved"), "quality_score": round(sum(rated)/len(rated),2) if rated else None,
            "cost_per_application": cpa, "cost_source": cost_source,
            "small_sample": ne < config.MIN_ELIGIBLE_FOR_RATES}

def breakdown(by, period="month"):
    rows=[r for r in log.list_entries() if r.get("activity_type")=="application"]; rows=_in_period(rows, period)
    groups={}
    for r in rows:
        if by=="weekday":
            try: key=date.fromisoformat(r["logged_at"][:10]).strftime("%A")
            except Exception: key="unknown"
        elif by=="hour_bucket":
            try:
                h=int(r["logged_at"][11:13]); key="morning" if h<12 else "midday" if h<14 else "afternoon" if h<17 else "evening"
            except Exception: key="unknown"
        else: key=r.get(by,"") or "(blank)"
        groups.setdefault(key,[]).append(r)
    out={}
    for k,rs in groups.items():
        elig=_eligible(rs); ne=len(elig)
        out[k]={"n":len(rs),"response_rate": round(sum(1 for x in elig if x.get("response")=="Yes")/ne,4) if ne else None,
                "interview_rate": round(sum(1 for x in elig if x.get("interview")=="Yes")/ne,4) if ne else None,
                "label": "too few to conclude" if len(rs)<5 else ""}
    return out

def response_rate_status(rate):
    if rate is None: return "n/a"
    if rate < config.RED_FLAG_RESPONSE_RATE: return "red_flag"
    if rate < config.TRIGGER_RESPONSE_RATE: return "below_target"
    if rate <= config.TARGET_RESPONSE_RATE_RANGE[1]: return "on_target"
    return "above_range"
