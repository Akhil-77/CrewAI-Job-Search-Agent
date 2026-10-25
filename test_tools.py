"""No-API tests for custom tools."""
import os; os.environ.setdefault("OPENAI_API_KEY","dummy")
from tools.keyword_analyzer import call_keyword_analyzer
from tools.consistency_checker import call_consistency_checker

def test_keyword():
    out = call_keyword_analyzer("We need Python and SQL and Machine Learning experience. Python Python SQL.", "Python, SQL")
    assert "python" in out.lower(), out
    assert "machine learning" in out.lower(), out
    print("keyword_analyzer OK:", out.splitlines()[1])
def test_consistency_pass():
    profile = "Name: Akhil Jethwa\nDegree 2026 Arizona State University Python SQL"
    resume = "Akhil Jethwa 2026 Python SQL"
    cover = "Akhil Jethwa 2026 Python"
    out = call_consistency_checker(resume, cover, profile)
    assert "PASS" in out, out
    print("consistency pass OK")
def test_consistency_warn():
    profile = "Name: Akhil Jethwa\n2026 Python"
    resume = "Akhil Jethwa 2019 Kubernetes expert at FakeCorp"
    cover = "Akhil Jethwa 2019"
    out = call_consistency_checker(resume, cover, profile)
    assert "WARN" in out, out
    print("consistency warn OK")
if __name__=="__main__":
    test_keyword(); test_consistency_pass(); test_consistency_warn(); print("test_tools: all passed")
