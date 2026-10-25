"""Industry presets - guidance verbatim from course."""
INDUSTRY_GUIDANCE = {
 "tech": "Reference the company's tech stack and engineering culture where research supports it",
 "finance": "Focus on regulatory knowledge and attention to detail. Emphasize quantitative achievements and risk management. Research company's recent financial performance and market position. Use more formal, conservative language in applications",
 "healthcare": "Highlight relevant coursework and research experience. Focus on patient impact and regulatory compliance. Research company's pipeline and recent clinical trials. Emphasize collaboration and attention to detail",
 "consulting": "Emphasize problem-solving frameworks and case study experience. Research client industries and recent case studies. Focus on leadership potential and analytical skills. Use structured, results-oriented language",
}
def get_industry_guidance(industry):
    return INDUSTRY_GUIDANCE.get((industry or "").lower(), "")
