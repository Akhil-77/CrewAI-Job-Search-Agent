"""Configuration variants registry. Rule: each variant changes exactly one element relative to baseline."""
from presets.industry import get_industry_guidance
from presets.level import get_level_guidance

VARIANTS = {
 "baseline": {"name":"baseline","description":"Part 3/4 application crew, unchanged","changed_element":None},
 "deep_culture_research": {"name":"deep_culture_research","description":"Adds a culture-research agent and task before writing","changed_element":"agent"},
 "personalizer": {"name":"personalizer","description":"Adds a personalization agent and task after drafting","changed_element":"agent"},
 "economy": {"name":"economy","description":"Alias for --economy (cheap tier, capped iterations)","changed_element":"model"},
}
def list_variants(): return list(VARIANTS.values())
def build_guidance(industry=None, level=None, user_flags=None, library_items=None):
    resume_parts=[]; cover_parts=[]
    ig=get_industry_guidance(industry); lg=get_level_guidance(level)
    if ig: resume_parts.append(ig); cover_parts.append(ig)
    if lg: resume_parts.append(lg); cover_parts.append(lg)
    if user_flags:
        for k in ("resume_guidance","cover_letter_guidance"):
            pass
        if user_flags.get("highlight"): cover_parts.append("Highlight: "+ ", ".join(user_flags["highlight"])); resume_parts.append("Highlight: "+ ", ".join(user_flags["highlight"]))
        if user_flags.get("tone"): cover_parts.append(f"Tone: {user_flags['tone']}")
        if user_flags.get("examples"): cover_parts.append("Use these specific examples: "+ "; ".join(user_flags["examples"]))
        if user_flags.get("extra_resume"): resume_parts.append(user_flags["extra_resume"])
        if user_flags.get("extra_cover"): cover_parts.append(user_flags["extra_cover"])
    if library_items:
        for it in library_items: resume_parts.append(str(it)); cover_parts.append(str(it))
    return {"resume_guidance": "\n".join(resume_parts) if resume_parts else "None.", "cover_letter_guidance": "\n".join(cover_parts) if cover_parts else "None."}
