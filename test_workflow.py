import os, tempfile; os.environ.setdefault("OPENAI_API_KEY","dummy")
tmp=tempfile.mkdtemp(); os.environ["JOBSEARCH_DATA_DIR"]=tmp
import config; config.DATA_DIR=tmp
from datetime import datetime, timedelta
from workflow.timing import check_submission_window
from workflow.targets import add_target, list_targets, remove_target, set_status
from workflow.planner import build_plan
from workflow.last_run import write_last_run
from core import application_log as log

def test_timing():
    tue=datetime(2026,10,27,11,0)  # Tuesday
    assert tue.strftime("%A")=="Tuesday", tue.strftime("%A")
    msgs=check_submission_window(now=tue); assert any("within the recommended window" in m for m in msgs), msgs
    mon=datetime(2026,10,26,9,0); assert mon.strftime("%A")=="Monday"
    msgs2=check_submission_window(now=mon); assert any("avoid" in m or "outside" in m for m in msgs2), msgs2
    fri=datetime(2026,10,30,15,0); assert fri.strftime("%A")=="Friday"
    msgs3=check_submission_window(now=fri); assert any("avoid" in m or "outside" in m for m in msgs3), msgs3
    msgs4=check_submission_window(now=tue, last_submission=tue-timedelta(minutes=10)); assert any("30 minutes" in m for m in msgs4), msgs4
    msgs5=check_submission_window(now=tue, last_submission=tue-timedelta(minutes=60)); assert any("120" in m or "spacing" in m for m in msgs5), msgs5
    print("timing OK")
def test_targets_and_plan():
    for i in range(3): add_target(f"C{i}","R","indeed")
    assert len(list_targets())==3
    txt=build_plan(); assert "Tuesday" in txt
    # warn above 5: add 4 more =7 targets, plan assigns at most 5 slots
    for i in range(4): add_target(f"D{i}","R","indeed")
    txt2=build_plan(); assert "Warning" in txt2 or "exceeds" in txt2, txt2
    tid=list_targets()[0]["id"]; assert set_status(tid,"drafted"); assert remove_target(tid)
    print("targets/plan OK")
def test_last_run_and_unreviewed():
    write_last_run({"command":"apply","company":"X","role":"Y","variant":"baseline","industry":"tech","level":"entry","cost_estimate":"0.4","output_file": os.path.join(tmp,"out.md"),"finished_at":datetime.now().isoformat()})
    open(os.path.join(tmp,"out.md"),"w",encoding="utf-8").write("draft")
    # log add --from-last-run logic is in manage.py; here verify prefill data exists and approved check
    from workflow.last_run import read_last_run; lr=read_last_run(); assert lr["company"]=="X"
    assert not os.path.exists(lr["output_file"]+".approved.json")
    print("last_run OK")
def test_custom_checklist_and_cadence():
    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(os.path.join(config.DATA_DIR,"custom_checklist_items.txt"),"w",encoding="utf-8") as f: f.write("□ My custom item\n")
    from quality.checklist import load_checklist; items=load_checklist("standard"); assert any("custom" in i for i in items), items
    from workflow.weekly_review import cadence_status; st=cadence_status(); assert "weekly" in st
    print("checklist/cadence OK")
if __name__=="__main__":
    test_timing(); test_targets_and_plan(); test_last_run_and_unreviewed(); test_custom_checklist_and_cadence(); print("test_workflow: all passed")
