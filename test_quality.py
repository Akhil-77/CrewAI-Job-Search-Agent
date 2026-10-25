import os; os.environ.setdefault("OPENAI_API_KEY","dummy")
from quality.red_flags import scan
from quality.privacy import scan_for_sensitive
from quality.checklist import run_checklist, load_checklist

def test_red_flags():
    f = scan("I am a team player and hard worker. [Company] TBD. No numbers here.", kind="cover_letter")
    cats = [x["category"] for x in f]
    assert "Generic phrases" in cats, f
    assert "Placeholder text" in cats, f
    # unsupported / developing-as-expertise: profile has Python only, text claims Spark expert
    f2 = scan("I am an expert in Spark with extensive experience and 5 years, 100% results.", kind="resume")
    assert any(x["category"]=="Unsupported skills/experience" for x in f2), f2
    # allowed markers are info only
    f3 = scan("Contact: [ADD YOUR EMAIL] [ADD YOUR PHONE] 123 results", kind="resume")
    marker = [x for x in f3 if x["evidence"] in ("[ADD YOUR EMAIL]","[ADD YOUR PHONE]")]
    assert marker and all(x["severity"]=="info" for x in marker), f3
    print("red_flags OK")
def test_privacy():
    f = scan_for_sensitive("SSN 123-45-6789 and key sk-abcdefghijklmnop1234")
    assert any(x["severity"]=="error" for x in f), f
    print("privacy OK")
def test_checklist():
    items = load_checklist("standard"); assert len(items)>=7, items
    res = run_checklist(items, interactive=False); assert res["overall"]=="unchecked", res
    print("checklist OK")
if __name__=="__main__":
    test_red_flags(); test_privacy(); test_checklist(); print("test_quality: all passed")
