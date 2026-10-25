"""Custom tool: keyword_analyzer - deterministic, no LLM."""
import re
COMMON_SKILLS = ["python","sql","r","machine learning","tableau","communication","data analysis","excel","power bi","statistics","pandas","numpy","visualization","project management","problem solving"]
STOP = set("the and for with you will are our job work team role must have from this that including experience skills required requirements ability".split())

def _analyze(job_posting_text, candidate_skills):
    text = (job_posting_text or "").lower()
    found = [s for s in COMMON_SKILLS if s in text]
    # frequency of non-stop words as extra keywords
    words = re.findall(r"[a-z][a-z\-]{2,}", text)
    freq = {}
    for wd in words:
        if wd not in STOP: freq[wd] = freq.get(wd, 0) + 1
    cand = [c.strip().lower() for c in (candidate_skills or "").split(",") if c.strip()]
    matched = [f for f in found if any(f in c or c in f for c in cand)]
    gaps = [f for f in found if f not in matched]
    suggested = found[:]
    report = ["Keyword analysis:", f"Keywords found in posting: {', '.join(found) if found else '(none)'}",
              f"Matching candidate skills: {', '.join(matched) if matched else '(none)'}",
              f"Gaps (in posting, not in candidate skills): {', '.join(gaps) if gaps else '(none)'}",
              f"Suggested keywords to include: {', '.join(suggested) if suggested else '(none)'}"]
    return "\n".join(report)

try:
    from crewai.tools import tool
    @tool("keyword_analyzer")
    def keyword_analyzer(job_posting_text: str, candidate_skills: str) -> str:
        """Use to analyze a job posting for keywords and compare with candidate skills. Input posting text and comma-separated candidate skills."""
        return _analyze(job_posting_text, candidate_skills)
except Exception:
    def keyword_analyzer(job_posting_text: str, candidate_skills: str) -> str:
        """Use to analyze a job posting for keywords and compare with candidate skills."""
        return _analyze(job_posting_text, candidate_skills)

def call_keyword_analyzer(job_posting_text, candidate_skills):
    fn = getattr(keyword_analyzer, "func", keyword_analyzer)
    return fn(job_posting_text, candidate_skills)
