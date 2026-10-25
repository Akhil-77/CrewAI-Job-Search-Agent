import os, tempfile; os.environ.setdefault("OPENAI_API_KEY","dummy")
tmp=tempfile.mkdtemp(); os.environ["JOBSEARCH_DATA_DIR"]=tmp
import config; config.DATA_DIR=tmp
from datetime import datetime, timedelta
from core import application_log as log
from core.compliance import check_before_submission
import config as cfg

def test_spacing():
    now=datetime.now()
    log.add_entry(company="A", role="R", platform="indeed", logged_at=(now-timedelta(minutes=10)).isoformat())
    g=check_before_submission("indeed", now=now); assert g["warnings"], g
    print("spacing 30 OK")
    g2=check_before_submission("indeed", now=now+timedelta(minutes=50))  # 60 min after entry: <120 soft note
    assert g2["notes"] or g2["warnings"], g2
    print("spacing 120 OK")
def test_platform_limits():
    now=datetime.now()
    for i in range(cfg.PLATFORM_LIMITS["indeed"]["applications_per_day"][1]):
        log.add_entry(company=f"C{i}", role="R", platform="indeed", logged_at=now.isoformat())
    g=check_before_submission("indeed", now=now); assert any("Indeed" in w for w in g["warnings"]), g
    for i in range(cfg.PLATFORM_LIMITS["linkedin"]["connection_requests_per_week"][1]):
        log.add_entry(company=f"L{i}", role="", platform="linkedin", activity_type="connection_request", logged_at=now.isoformat())
    g2=check_before_submission("linkedin", now=now); assert any("LinkedIn" in w for w in g2["warnings"]), g2
    print("platform limits OK")
def test_no_submit_tools():
    import os as _os
    os.environ.setdefault("OPENAI_API_KEY","dummy")
    from crews.application_crew import build_crew as b1; from crews.job_research_crew import build_crew as b2
    from crews.company_research_crew import build_crew as b3; from crews.interview_prep_crew import build_crew as b4
    for build in [b1,b2,b3,b4]:
        crew=build()
        for a in crew.agents:
            for t in (a.tools or []):
                name=str(getattr(t,"name",t)).lower()
                assert "submit" not in name and "apply_to" not in name and "auto_apply" not in name, name
    print("no-submit-tools OK")
if __name__=="__main__":
    test_spacing(); test_platform_limits(); test_no_submit_tools(); print("test_compliance: all passed")
