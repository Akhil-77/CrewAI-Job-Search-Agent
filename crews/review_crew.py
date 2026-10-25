"""Review crew (Part 4): quality_reviewer + review_task."""
from _compat import Agent, Task, Crew, Process, set_meta
from core.model_router import get_llm
from user_profile import profile_as_text_full

quality_reviewer = Agent(role="Quality Control Specialist", goal="Ensure all job application materials are accurate, personalized, and professional",
    backstory="You are meticulous about details and have a keen eye for authenticity in job applications.", tools=[], verbose=True)

def make_review_task(cover_letter_task=None, draft_text=None):
    profile=profile_as_text_full()
    desc="Review the generated cover letter for accuracy, tone, and personalization. Flag any generic language or factual errors."
    desc+=f" Candidate profile:\n{profile}\nFlag any skill, experience, or achievement that does not appear in the candidate profile."
    if draft_text: desc+=f"\nDraft to review:\n{draft_text}"
    t=Task(description=desc, agent=quality_reviewer, expected_output="A list of flagged issues (generic language, factual errors, unsupported claims) with a suggested fix for each, and a short overall verdict", context=[cover_letter_task] if cover_letter_task else [])
    set_meta(t, "task_name", "review_task"); return t

# Standalone task variable for inspection
review_task = make_review_task()

def build_review_crew(draft_text=""):
    t=make_review_task(draft_text=draft_text)
    crew=Crew(agents=[quality_reviewer], tasks=[t], process=Process.sequential, verbose=True); set_meta(crew, "task_map", {"review_task":t}); return crew
build_crew = build_review_crew
