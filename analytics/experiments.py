"""Variant comparison."""
import config
from core import application_log as log
from analytics.metrics import _eligible
def compare_variants(baseline="baseline", min_n=5):
    rows=[r for r in log.list_entries() if r.get("activity_type")=="application"]
    groups={}
    for r in rows: groups.setdefault(r.get("config_variant") or "baseline",[]).append(r)
    def stats(rs):
        elig=_eligible(rs); ne=len(elig)
        rated=[float(x["quality_score"]) for x in rs if x.get("quality_score") not in ("",None)]
        costs=[float(x["cost_estimate"]) for x in rs if x.get("cost_estimate") not in ("",None)]
        return {"n":len(rs),"response_rate": round(sum(1 for x in elig if x.get("response")=="Yes")/ne,4) if ne else None,
                "interview_rate": round(sum(1 for x in elig if x.get("interview")=="Yes")/ne,4) if ne else None,
                "avg_quality": round(sum(rated)/len(rated),2) if rated else None, "avg_cost": round(sum(costs)/len(costs),4) if costs else None}
    base=stats(groups.get(baseline,[])); out={}
    for name,rs in groups.items():
        s=stats(rs)
        if name==baseline: verdict="baseline"
        elif s["n"]<min_n or base["n"]<min_n: verdict="inconclusive"
        elif (s["response_rate"] or 0)<(base["response_rate"] or 0) and (s["interview_rate"] or 0)<(base["interview_rate"] or 0): verdict="revert"
        elif ((s["response_rate"] or 0)>(base["response_rate"] or 0) or (s["interview_rate"] or 0)>(base["interview_rate"] or 0)) and (s["avg_quality"] is None or base["avg_quality"] is None or s["avg_quality"]>=base["avg_quality"]): verdict="keep"
        else: verdict="inconclusive"
        s["verdict"]=verdict; s["delta_response"]= round((s["response_rate"] or 0)-(base["response_rate"] or 0),4) if s["response_rate"] is not None and base["response_rate"] is not None else None
        out[name]=s
    return out
def format_comparison(baseline="baseline", min_n=5):
    out=compare_variants(baseline, min_n); lines=[]
    for name,s in out.items(): lines.append(f"{name}: n={s['n']} response={s['response_rate']} interview={s['interview_rate']} quality={s['avg_quality']} cost={s['avg_cost']} delta_vs_baseline={s['delta_response']} verdict={s['verdict']}" + (" (too few to conclude)" if s['n']<min_n else ""))
    lines.append("With samples this small, differences are often noise. Treat verdicts as hints, and keep testing.")
    lines.append("Testing process: change one element at a time; test with 5-10 applications; compare to baseline; keep what improves metrics and revert what doesn't.")
    return "\n".join(lines)
