"""Red flags, success indicators, optimization triggers, dashboard."""
import config
from analytics.metrics import compute_metrics, response_rate_status
from core import application_log as log, cost_tracker

def get_insights(period="month"):
    m=compute_metrics(period); rows=log.list_entries()
    flags=[]; successes=[]; triggers=[]
    elig=m["n_eligible"]
    if elig>=config.MIN_ELIGIBLE_FOR_RATES and m["response_rate"] is not None and m["response_rate"]<config.RED_FLAG_RESPONSE_RATE:
        flags.append({"name":"Low response rate","message":"May indicate generic applications"})
    apps=[r for r in rows if r.get("activity_type")=="application"]
    if len(apps)>=config.NO_INTERVIEW_AFTER_N and not any(r.get("interview")=="Yes" for r in apps):
        flags.append({"name":"No interviews","message":"Need to adjust strategy"})
    fit=sum(1 for r in apps if any(p in (r.get("notes") or "").lower() for p in config.NOT_A_FIT_PHRASES))
    if fit>=config.NOT_A_FIT_REPEAT_COUNT: flags.append({"name":"Consistent not a good fit","message":"May be targeting the wrong roles"})
    if m["cost_per_application"] and m["cost_per_application"]>config.HIGH_COST_PER_APPLICATION_USD and m["response_rate"] is not None and m["response_rate"]<0.15:
        flags.append({"name":"High cost, low results","message":"Inefficient AI usage"})
    # successes
    if m["response_rate"] is not None and 0.15 <= m["response_rate"] <= 0.25: successes.append("Response rate 15%-25%")
    quality_apps=[r for r in apps if r.get("quality_score") not in ("",None) and float(r["quality_score"])>=config.QUALITY_APPLICATION_MIN_SCORE]
    if quality_apps and sum(1 for r in quality_apps if r.get("interview")=="Yes")*10>=len(quality_apps)*config.TARGET_INTERVIEWS_PER_10_QUALITY: successes.append("At least one interview per 10 quality applications")
    pos=sum(1 for r in apps if "positive feedback" in (r.get("notes") or "").lower())
    if pos: successes.append(f"Positive feedback: {pos}")
    if m["time_saved_per_week"] is not None and m["time_saved_per_week"]>=config.TARGET_HOURS_SAVED_PER_WEEK: successes.append("Average hours saved per week >= 10")
    # triggers
    if m["response_rate"] is not None and m["response_rate"]<config.TRIGGER_RESPONSE_RATE:
        triggers.append({"trigger":"Response rate < 15%: improve personalization","action":"Try run.py apply --variant personalizer and --variant deep_culture_research; use --tone and --examples"})
    ct=cost_tracker.totals()
    if ct["month"]>config.TRIGGER_MONTHLY_COST_USD: triggers.append({"trigger":"Monthly cost > $25: optimize AI usage","action":"Use --economy, rely on the cache, batch research, reuse library items"})
    from core.time_log import average_hours; avg=average_hours()
    if avg.get("avg_spent") is not None and avg["avg_spent"]>config.TRIGGER_HOURS_SPENT_PER_WEEK: triggers.append({"trigger":"Weekly time spent > 8 hours: increase automation","action":"Use batch mode, the library, and the guided daily routine"})
    if m["quality_score"] is not None and m["quality_score"]<config.TRIGGER_QUALITY_SCORE: triggers.append({"trigger":"Average quality score < 7: enhance review process","action":"Use --with-review, run the checklists, run the weekly review"})
    if elig<config.MIN_ELIGIBLE_FOR_RATES:
        return {"metrics":m,"red_flags":[],"success_indicators":successes,"triggers":triggers,"note":"not enough data yet"}
    return {"metrics":m,"red_flags":flags,"success_indicators":successes,"triggers":triggers}

def dashboard_text(period="month"):
    ins=get_insights(period); m=ins["metrics"]; ct=cost_tracker.totals()
    def fmt(v, suffix=""): return "n/a" if v is None else f"{v}{suffix}"
    lines=[f"Applications Sent: {fmt(m['n_applications'])}",
           f"Response Rate: {fmt(round(m['response_rate']*100,1) if m['response_rate'] is not None else None, '%')}",
           f"Interview Rate: {fmt(round(m['interview_rate']*100,1) if m['interview_rate'] is not None else None, '%')}",
           f"Time Saved per Week: {fmt(m['time_saved_per_week'])} hours",
           f"Cost per Application: ${fmt(m['cost_per_application'])}",
           f"Quality Score (1-10): {fmt(m['quality_score'])}",
           f"Month-to-date spend: ${ct['month']} (target $15-20)"]
    lines.append("\nRed flags:"); lines+= [f"  - {f['name']}: {f['message']}" for f in ins["red_flags"]] or ["  - none"]
    lines.append("Success indicators:"); lines+= [f"  - {s}" for s in ins["success_indicators"]] or ["  - none"]
    lines.append("Optimization triggers:"); lines+= [f"  - {t['trigger']} -> {t['action']}" for t in ins["triggers"]] or ["  - none"]
    return "\n".join(lines)
