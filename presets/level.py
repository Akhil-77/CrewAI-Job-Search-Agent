"""Role-level presets - guidance verbatim from course."""
LEVEL_GUIDANCE = {
 "entry": "Emphasize learning potential and academic projects. Focus on enthusiasm and cultural fit. Highlight internships, coursework, and personal projects. Use more conversational, eager tone",
 "mid": "Bridge academic experience with professional requirements. Emphasize transferable skills from projects and internships. Show progression and growth mindset. Balance confidence with humility",
 "technical": "Translate academic projects into industry-relevant technical experience",
 "cross_functional": "Highlight diverse skill sets and adaptability. Show examples of working across different domains. Emphasize communication and collaboration skills. Focus on systems thinking and problem-solving",
}
def get_level_guidance(level):
    return LEVEL_GUIDANCE.get((level or "").lower(), "")
