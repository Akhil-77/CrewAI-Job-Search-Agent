"""Privacy scanner. Heuristic."""
import re
def scan_for_sensitive(text):
    t=text or ""; findings=[]
    def add(cat,sev,ev): findings.append({"category":cat,"severity":sev,"evidence":ev})
    if re.search(r"\b\d{3}-\d{2}-\d{4}\b", t): add("SSN","error","SSN-like pattern ###-##-####")
    if re.search(r"sk-[A-Za-z0-9_\-]{10,}", t): add("API key","error","sk-... token")
    if re.search(r"(password|passwd)\s*[:=]\s*\S+", t, re.I): add("Credential","error","password with value")
    for m in re.findall(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", t): add("Email","warn",m)
    for m in re.findall(r"\b\d{3}[-. ]\d{3}[-. ]\d{4}\b", t): add("Phone","warn",m)
    if re.search(r"\b\d+\s+\w+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln)\b", t): add("Street address","warn","address-like line")
    for phrase in ["current salary","salary history","confidential"]:
        if phrase in t.lower(): add("Sensitive phrase","warn",phrase)
    return findings
def scan_output_for_third_party_contacts(text):
    t=text or ""; out=[]
    for m in re.findall(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", t): out.append({"category":"Third-party email","severity":"warn","evidence":m})
    for m in re.findall(r"\b\d{3}[-. ]\d{3}[-. ]\d{4}\b", t): out.append({"category":"Third-party phone","severity":"warn","evidence":m})
    return out
