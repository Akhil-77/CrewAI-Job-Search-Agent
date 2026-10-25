"""Sunday planning (1 hour)."""
import os
import config
from workflow.targets import list_targets
from core.time_log import monday_of
from datetime import date
SCHEDULE_TEMPLATE="""Sunday:    Planning and company research (1 hour)
Monday:    Networking and LinkedIn engagement (30 minutes)
Tuesday:   2 applications with AI assistance (1.5 hours)
Wednesday: 2 applications with AI assistance (1.5 hours)
Thursday:  1 application + interview prep (1 hour)
Friday:    Follow-ups and weekly review (45 minutes)
Saturday:  Rest or optional skill development"""
ENERGY_TIPS=["Do creative work (writing, customization) when fresh","Use AI for routine tasks when energy is lower","Batch similar activities","Take breaks between applications","Set realistic weekly goals (3-5 quality applications)","Focus on fit over volume","Celebrate small wins (responses, interviews, good feedback)","Keep activities outside job searching"]
def build_plan():
    targets=list_targets(); slots=[]; idx=0
    for day,count in config.APPLICATION_SLOTS.items():
        for _ in range(count):
            if idx<len(targets): slots.append(f"{day}: {targets[idx]['company']} - {targets[idx]['role']}"); idx+=1
    warn=""
    if len(targets)>config.WEEKLY_GOAL_APPLICATIONS: warn=f"Warning: {len(targets)} targets exceeds weekly goal {config.WEEKLY_GOAL_APPLICATIONS} - quality beats volume."
    lines=["# Weekly plan",f"Week starting: {monday_of()}", "", "## Targets (5-7 high-quality opportunities guidance)", *[f"- {t['company']} - {t['role']} ({t['platform']})" for t in targets], warn, "", "## Slots", *slots, "", "## Weekly schedule", SCHEDULE_TEMPLATE, "", "Networking and follow-ups are human-only. The plan only reserves time.", "", "## Energy and burnout tips", *[f"- {t}" for t in ENERGY_TIPS]]
    return "\n".join(lines)
def save_plan():
    text=build_plan(); d=os.path.join(config.DATA_DIR,"weekly_plans"); os.makedirs(d,exist_ok=True)
    p=os.path.join(d, f"{monday_of()}.md")
    with open(p,"w",encoding="utf-8") as f: f.write(text)
    return p, text
