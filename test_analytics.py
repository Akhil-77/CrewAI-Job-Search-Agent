import os, tempfile; os.environ.setdefault("OPENAI_API_KEY","dummy")
tmp=tempfile.mkdtemp(); os.environ["JOBSEARCH_DATA_DIR"]=tmp
import config; config.DATA_DIR=tmp
from datetime import datetime, timedelta, date
from core import application_log as log
from core import cost_tracker

def _old(days): return (datetime.now()-timedelta(days=days)).isoformat()
def seed():
    # 12 eligible old applications: 1 response yes (8.3% -> red flag range), rest no
    for i in range(12):
        log.add_entry(company=f"C{i}", role="R", platform="indeed", industry="tech", response="Yes" if i==0 else "No", interview="No", logged_at=_old(30), cost_estimate="0.5", quality_score="5")
def test_rates_exclude_recent():
    seed()
    log.add_entry(company="Recent", role="R", platform="indeed", response="Pending", logged_at=datetime.now().isoformat())
    from analytics.metrics import compute_metrics
    m=compute_metrics("all"); assert m["n_eligible"]==12, m; assert abs(m["response_rate"]-1/12)<0.01, m
    print("rates OK", m)
def test_cost_fallback_and_labels():
    from analytics.metrics import compute_metrics, breakdown
    b=breakdown("industry","all"); assert b["tech"]["label"]=="", b  # n=13 >=5 so no label? recent adds 13
    # small group
    log.add_entry(company="Solo", role="R", platform="other", industry="rare", response="No", logged_at=_old(30))
    b2=breakdown("industry","all"); assert b2["rare"]["label"]=="too few to conclude", b2
    print("breakdown labels OK")
def test_insights_and_compare():
    from analytics.insights import get_insights
    ins=get_insights("all"); assert any(f["name"]=="Low response rate" for f in ins["red_flags"]), ins
    from analytics.metrics import response_rate_status
    assert response_rate_status(0.05)=="red_flag"; assert response_rate_status(0.12)=="below_target"; assert response_rate_status(0.20)=="on_target"; assert response_rate_status(0.30)=="above_range"
    from analytics.experiments import compare_variants
    # baseline only -> inconclusive for others not present; add variant entries
    for i in range(6): log.add_entry(company=f"V{i}", role="R", platform="indeed", response="Yes", interview="Yes", config_variant="personalizer", logged_at=_old(30), quality_score="9")
    out=compare_variants(); assert out["personalizer"]["verdict"] in ("keep","inconclusive"), out
    print("insights/compare OK")
def test_dashboard_na():
    from analytics.insights import dashboard_text; t=dashboard_text("all"); assert "Applications Sent" in t; print("dashboard OK")
if __name__=="__main__":
    test_rates_exclude_recent(); test_cost_fallback_and_labels(); test_insights_and_compare(); test_dashboard_na(); print("test_analytics: all passed")
