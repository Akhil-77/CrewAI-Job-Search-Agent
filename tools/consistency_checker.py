"""Custom tool: consistency_checker - deterministic heuristics, cannot replace human review."""
import re

def _check(resume_text, cover_letter_text, profile_text):
    findings = []
    profile = profile_text or ""
    combined = ((resume_text or "") + "\n" + (cover_letter_text or ""))
    # name consistency: first line / name from profile "Name: X"
    m = re.search(r"Name:\s*(.+)", profile)
    name = m.group(1).strip() if m else ""
    if name:
        if name in (resume_text or "") and name in (cover_letter_text or ""):
            findings.append("PASS: name appears consistently in both documents")
        else:
            findings.append(f"WARN: candidate name '{name}' not found in both documents")
    # years in docs not in profile
    prof_years = set(re.findall(r"\b(19|20)\d{2}\b", profile))
    # capture full years properly
    prof_years = set(re.findall(r"\b(?:19|20)\d{2}\b", profile))
    doc_years = set(re.findall(r"\b(?:19|20)\d{2}\b", combined))
    extra_years = doc_years - prof_years
    if extra_years:
        findings.append(f"WARN: years in documents not in profile: {', '.join(sorted(extra_years))}")
    else:
        findings.append("PASS: all years in documents appear in profile")
    # degree/university check: flag graduation year mismatch handled via years above
    # skills: simple vocab
    vocab = ["python","sql","spark","tableau","kubernetes","java","aws","gcp","azure","machine learning"]
    prof_low = profile.lower()
    flagged = [s for s in vocab if s in combined.lower() and s not in prof_low]
    if flagged:
        findings.append(f"WARN: skills in documents but not in profile: {', '.join(flagged)}")
    else:
        findings.append("PASS: no unprofiled skills detected from checklist vocab")
    # organizations: capitalized multiword? heuristic - years check is primary for tests
    return "\n".join(findings)

try:
    from crewai.tools import tool
    @tool("consistency_checker")
    def consistency_checker(resume_text: str, cover_letter_text: str, profile_text: str) -> str:
        """Use to verify resume and cover letter are consistent with the candidate profile (name, years, skills)."""
        return _check(resume_text, cover_letter_text, profile_text)
except Exception:
    def consistency_checker(resume_text: str, cover_letter_text: str, profile_text: str) -> str:
        """Use to verify resume and cover letter are consistent with the candidate profile."""
        return _check(resume_text, cover_letter_text, profile_text)

def call_consistency_checker(r, c, p):
    fn = getattr(consistency_checker, "func", consistency_checker)
    return fn(r, c, p)
