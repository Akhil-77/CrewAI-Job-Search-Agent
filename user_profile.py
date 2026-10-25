"""Candidate profile - EDIT THIS FILE with your real information.
Do NOT add phone, email, street address, SSN, salary history, login credentials,
or references' contact details to this file. Resumes use [ADD YOUR EMAIL] / [ADD YOUR PHONE]
markers that the human fills in before submitting.
"""
# Part 2 profile (kept unchanged in later parts)
USER_PROFILE = {
    "name": "Akhil Jethwa",
    "degree": "MS in Computer Science",
    "target_roles": ["Machine Learning Engineer", "AI Engineer", "Data Scientist"],
    "skills": ["Python", "SQL", "Machine Learning", "PyTorch", "LLM Inference", "vLLM", "ONNX", "FastAPI", "Kafka", "Docker", "AWS"],
    "location_preference": "United States (open to relocation)",
    "experience_summary": "MS CS at Arizona State University (2024-2026, GPA 3.63); ML Engineer at LST Capital (2023-2024) building Kafka/PySpark/FastAPI pipelines serving 5M+ residents; Graduate Student Assistant at ASU processing 3,000+ records weekly with OCR/NLP; IEEE publication on CNN malaria diagnosis (27,000+ images).",
}

# Part 3 additions - Akhil's real profile (replaces course placeholders, verified from his resume)
MY_SKILLS = {
    "technical": ["Python", "SQL", "Machine Learning", "PyTorch", "Data Analysis"],
    "soft": ["Project Management", "Communication", "Problem Solving"],
    "experience_level": "Entry to Mid-level",
    "preferred_industries": ["Technology", "Healthcare", "Finance"],
}
# Also expose flat keys used by some course snippets
MY_SKILLS_FLAT = MY_SKILLS

MY_PROFILE = {
    "education": {"degree": "Master of Science in Computer Science", "university": "Arizona State University",
                  "graduation_year": "2026", "relevant_coursework": ["Machine Learning", "Statistical Analysis", "Database Systems"]},
    "experience": [
        {"title": "Machine Learning Engineer", "company": "LST Capital", "duration": "2023-2024",
         "achievements": ["Built Kafka/PySpark/FastAPI pipelines serving 5M+ residents", "Cut incident detection time by 40% with Prometheus/Grafana"],
         "skills_used": ["Python", "Kafka", "SQL", "Data Visualization"]},
        {"title": "Research Assistant", "company": "University Lab", "duration": "2023-2024",
         "achievements": ["Analyzed datasets with 100K+ records", "Built predictive models", "Published research paper"],
         "skills_used": ["Python", "R", "SQL", "Data Visualization"]},
    ],
    "skills": {"technical": ["Python", "R", "SQL", "Machine Learning", "Data Visualization"],
               "soft": ["Research", "Communication", "Project Management"]},
}
values = ["work-life balance", "continuous learning", "honesty and defensibility"]

# Part 4 additions
DEVELOPING_SKILLS = ["Spark"]
PROJECTS = [
    {"name": "LLM-Roofline", "facts": "Analytical roofline model for Qwen2.5-0.5B/TinyLlama on Colab T4; measured 23.32 TFLOPS effective, 239.26 GB/s; decode overhead-bound; int8/int4 at 12%/16% of ideal",
     "technologies": ["Python", "PyTorch", "bitsandbytes"], "outcomes": "Verified 18/18 pytest; MAPE 90.23% time-based", "your_role": "Sole builder"},
    {"name": "DocFlow", "facts": "AI document intake with n8n + PostgreSQL, deterministic validation and guarded resolver agent",
     "technologies": ["n8n", "PostgreSQL", "Python"], "outcomes": "135/135 tests after node audit", "your_role": "Sole builder"},
]

def profile_as_text():
    p = USER_PROFILE
    lines = [f"Name: {p['name']}", f"Degree: {p['degree']}", f"Target roles: {', '.join(p['target_roles'])}",
             f"Skills: {', '.join(p['skills'])}", f"Location preference: {p['location_preference']}",
             f"Experience: {p['experience_summary']}"]
    return "\n".join(lines)

def skills_as_text():
    s = MY_SKILLS
    return "\n".join([f"Technical skills: {', '.join(s['technical'])}", f"Soft skills: {', '.join(s['soft'])}",
                       f"Experience level: {s['experience_level']}", f"Preferred industries: {', '.join(s['preferred_industries'])}",
                       f"Developing skills (developing, not expertise): {', '.join(DEVELOPING_SKILLS)}",
                       f"Values: {', '.join(values)}"])

def profile_as_text_full():
    parts = [profile_as_text(), skills_as_text()]
    edu = MY_PROFILE["education"]
    parts.append(f"Education: {edu['degree']}, {edu['university']}, {edu['graduation_year']}; coursework: {', '.join(edu['relevant_coursework'])}")
    for e in MY_PROFILE["experience"]:
        parts.append(f"Experience: {e['title']} at {e['company']} ({e['duration']}): {'; '.join(e['achievements'])}; skills: {', '.join(e['skills_used'])}")
    for pr in PROJECTS:
        parts.append(f"Project: {pr['name']} - {pr['facts']}; technologies: {', '.join(pr['technologies'])}; outcomes: {pr['outcomes']}; role: {pr['your_role']}")
    parts.append(f"Developing skills (developing, not expertise): {', '.join(DEVELOPING_SKILLS)}")
    return "\n".join(parts)

def all_skills():
    out = set()
    for src in [USER_PROFILE.get("skills", []), MY_SKILLS.get("technical", []), MY_SKILLS.get("soft", []),
                MY_PROFILE["skills"]["technical"], MY_PROFILE["skills"]["soft"]]:
        out.update(x.lower() for x in src)
    return out
