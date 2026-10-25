"""Automated red-flag scanner. Heuristic - cannot replace human review."""
import re
import config
from user_profile import DEVELOPING_SKILLS
KNOWN_SKILLS=["python","sql","r","machine learning","tableau","spark","kubernetes","java","scala","aws","excel","pandas","tensorflow","pytorch"]

def scan(text, profile=None, kind="cover_letter", industry=None):
    t=text or ""; low=t.lower(); findings=[]
    def add(cat,sev,ev,fix): findings.append({"category":cat,"severity":sev,"evidence":ev,"suggested_fix":fix})
    for phrase in config.GENERIC_PHRASES:
        if phrase.lower() in low: add("Generic phrases","warn",phrase,"Replace generic enthusiasm with specific reasons you're interested")
    for ph in ["[Company]","[Your Name]","[Job Title]","TBD","Lorem","XXX"]:
        if ph.lower() in low: add("Placeholder text","error",ph,"Fill in or remove.")
    for m in re.findall(r"<[^>]+>", t): add("Placeholder text","error",m,"Fill in or remove.")
    for marker in config.CONTACT_MARKERS:
        if marker in t: add("Placeholder text","info",marker,"replace before submitting")
    # unsupported skills
    prof_skills=set()
    if profile:
        try:
            from user_profile import all_skills; prof_skills=all_skills()
        except Exception: pass
    for s in KNOWN_SKILLS:
        if s in low and s not in prof_skills and prof_skills:
            add("Unsupported skills/experience","warn",s,"Remove it, or describe it as 'developing' if you are learning it")
    for s in DEVELOPING_SKILLS:
        if s.lower() in low and any(w in low for w in ["expert","advanced","mastered","extensive experience"]):
            add("Unsupported skills/experience","warn",s,"Remove it, or describe it as 'developing' if you are learning it")
    if not re.search(r"\d", t): add("Missing metrics/examples","warn","(no digits found)","Add concrete numbers and results to vague claims")
    thresh=config.FORMAL_THRESHOLD_BY_INDUSTRY.get(industry or "default", config.FORMAL_THRESHOLD)
    formal=sum(1 for p in config.FORMAL_PHRASES if p.lower() in low)
    if formal>=thresh: add("Overly formal language","warn",f"{formal} formal phrases","Inject your personality through word choice and examples")
    add("Unverified company claims","info","(always)","Verify all factual claims about companies and roles")
    return findings

def format_report(findings):
    lines=["Red-flag report (heuristic, not a guarantee):"]
    for f in findings: lines.append(f"  [{f['severity'].upper()}] {f['category']}: {f['evidence']} -> {f['suggested_fix']}")
    return "\n".join(lines)
