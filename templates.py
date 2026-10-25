RESUME_TEMPLATES = {
    "technical_focus": {"sections": ["Contact", "Technical Skills", "Experience", "Projects", "Education"], "emphasis": "technical_skills_and_projects"},
    "research_focus": {"sections": ["Contact", "Education", "Research Experience", "Publications", "Technical Skills"], "emphasis": "academic_and_research_background"},
    "business_focus": {"sections": ["Contact", "Experience", "Skills", "Education", "Achievements"], "emphasis": "business_impact_and_leadership"},
}
def templates_as_text():
    lines = []
    for name, t in RESUME_TEMPLATES.items():
        lines.append(f"Template {name}: sections - {', '.join(t['sections'])}; emphasis - {t['emphasis']}")
    return "\n".join(lines)
