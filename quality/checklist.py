"""5-point validation + checklist runner + checkpoints."""
import os
FIVE_POINTS=[
    ("Accuracy","Are all company names, job titles, and requirements correct?"),
    ("Personalization","Does this sound like you wrote it?"),
    ("Relevance","Do the examples match the job requirements?"),
    ("Tone","Is the writing style appropriate for the company culture?"),
    ("Completeness","Are all required elements included?"),
]
RED_FLAG_QUESTIONS=[
    "Could I confidently discuss every claim in an interview?",
    "Are all the facts verifiable if an employer checks?",
    "Does this sound like something I would actually say?",
    "Am I comfortable with this representing me professionally?",
]
PREVENTION_REMINDERS=["never submit without human review","always verify company-specific details","check that examples match your actual experience","ensure the writing sounds like you"]
def _read_lines(path):
    with open(path,encoding="utf-8") as f: return [l.rstrip("\n") for l in f if l.strip()]
def load_checklist(kind="standard"):
    base="validation_checklist.txt" if kind=="standard" else "quality_check_5min.txt"
    items=_read_lines(base)
    # custom items appended, committed files never edited
    import config; custom=os.path.join(config.DATA_DIR,"custom_checklist_items.txt")
    if os.path.exists(custom):
        with open(custom,encoding="utf-8") as f: items+= [l.rstrip() for l in f if l.strip()]
    return items
def run_checklist(items, interactive=False, input_fn=input):
    if not interactive:
        return {"passed":[],"failed":[],"unchecked":list(items),"overall":"unchecked"}
    passed,failed=[],[]
    for it in items:
        ans=input_fn(f"{it} (y/n) ").strip().lower()
        (passed if ans.startswith("y") else failed).append(it)
    print("\nRed-flag prevention reminders:")
    for r in PREVENTION_REMINDERS: print(f"  - {r}")
    return {"passed":passed,"failed":failed,"unchecked":[],"overall":"pass" if not failed else "fail"}
def run_red_flag_questions(interactive=False, input_fn=input):
    if not interactive: return {"answers":{},"overall":"unchecked"}
    ans={}
    for q in RED_FLAG_QUESTIONS: ans[q]=input_fn(f"{q} (y/n) ").strip().lower().startswith("y")
    return {"answers":ans,"overall":"pass" if all(ans.values()) else "fail"}
