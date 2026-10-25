import os, tempfile; os.environ.setdefault("OPENAI_API_KEY","dummy")
# Use temp data dir BEFORE importing config-dependent modules
tmp = tempfile.mkdtemp(); os.environ["JOBSEARCH_DATA_DIR"]=tmp
import importlib, config; importlib.reload(config); config.DATA_DIR=tmp
from core import cost_tracker, cache, library
from core import application_log as log

def test_cost():
    c = cost_tracker.estimate_cost(config.CHEAP_MODEL, 1000, 1000)
    assert c is not None and c>0, c
    assert cost_tracker.estimate_cost("unknown-model-xyz", 1000, 1000) is None
    cost_tracker.append_row("2026-10-23","job_search",config.CHEAP_MODEL,1000,1000,c,"test")
    st = cost_tracker.budget_status(); assert "week_spend" in st
    print("cost OK", c)
def test_cache():
    cache.save_company_research("Test Co", {"research":"abc","culture":"def"})
    got = cache.load_company_research("Test Co"); assert got and got["research"]=="abc", got
    import json
    # expiry: backdate
    p = cache._file("Test Co"); d=json.load(open(p,encoding="utf-8")); d["created_at"]="2020-01-01T00:00:00"; json.dump(d, open(p,"w",encoding="utf-8"))
    assert cache.load_company_research("Test Co") is None
    print("cache OK")
def test_library():
    item = library.add_item("achievements","T1","Did X with 100 results",["a"]); assert library.get_item("achievements", item["id"])
    assert library.delete_item("achievements", item["id"])
    print("library OK")
def test_log():
    nid = log.add_entry(company="A", role="R", platform="indeed", activity_type="application")
    assert log.get_entry(nid)
    assert log.count_in_window("application","indeed", "2000-01-01")>=1
    print("log OK")
if __name__=="__main__":
    test_cost(); test_cache(); test_library(); test_log(); print("test_core: all passed")
