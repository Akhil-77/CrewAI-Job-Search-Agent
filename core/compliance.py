"""Platform limits and submission-timing guards. Advisory only - never submits or blocks applying elsewhere.
These are guidelines, verify each platform's current rules.
"""
from datetime import datetime, timedelta
import config
from core import application_log as log

def _parse(dt_str):
    try: return datetime.fromisoformat(dt_str)
    except Exception: return None

def check_before_submission(platform=None, now=None):
    now=now or datetime.now(); warnings=[]; notes=[]
    plat=(platform or "").lower(); plat=log.ALIASES.get(plat, plat)
    # spacing
    last=log.last_entry("application")
    if last:
        lt=_parse(last.get("logged_at",""))
        if lt:
            mins=(now-lt).total_seconds()/60
            if mins < config.MIN_MINUTES_BETWEEN_SUBMISSIONS: warnings.append(f"Last application was {int(mins)} minutes ago - less than {config.MIN_MINUTES_BETWEEN_SUBMISSIONS} minutes. Consider spacing submissions.")
            elif mins < config.RECOMMENDED_MINUTES_BETWEEN_SUBMISSIONS: notes.append(f"Last application was {int(mins)} minutes ago - recommended spacing is {config.RECOMMENDED_MINUTES_BETWEEN_SUBMISSIONS} minutes (soft note).")
    # weekly count
    week_ago=(now-timedelta(days=7)).isoformat()
    weekly=log.count_in_window("application", None, week_ago)
    if weekly>=config.MAX_WEEKLY_APPLICATIONS: warnings.append(f"You have logged {weekly} applications this week (guideline max {config.MAX_WEEKLY_APPLICATIONS}) - quality may suffer.")
    # platform limits
    if plat=="indeed":
        day_start=now.replace(hour=0,minute=0,second=0).isoformat(); n=log.count_in_window("application","indeed",day_start)
        lo,hi=config.PLATFORM_LIMITS["indeed"]["applications_per_day"]
        if n>=hi: warnings.append(f"Indeed: {n} applications today - at upper guideline bound {hi}. Strong warning.")
        elif n>=lo: warnings.append(f"Indeed: {n} applications today - over lower guideline bound {lo}.")
    if plat=="linkedin":
        n=log.count_in_window("connection_request","linkedin",week_ago)
        lo,hi=config.PLATFORM_LIMITS["linkedin"]["connection_requests_per_week"]
        if n>=hi: warnings.append(f"LinkedIn: {n} connection requests this week - at upper guideline bound {hi}. Strong warning.")
        elif n>=lo: warnings.append(f"LinkedIn: {n} connection requests this week - over lower guideline bound {lo}.")
    msg="These are guidelines, verify each platform's current rules."
    return {"warnings":warnings,"notes":notes,"guideline":msg}
