"""Submission timing advice. Course recommendations, not proven rules."""
from datetime import datetime
import config
from core.compliance import check_before_submission
def check_submission_window(now=None, last_submission=None):
    now=now or datetime.now(); msgs=[]
    day=now.strftime("%A"); hour=now.hour
    in_avoid=any(d==day and h1<=hour<h2 for d,h1,h2 in config.AVOID_WINDOWS)
    if day in config.PREFERRED_SUBMISSION_DAYS and config.PREFERRED_SUBMISSION_HOURS[0]<=hour<config.PREFERRED_SUBMISSION_HOURS[1]:
        msgs.append("within the recommended window")
    elif in_avoid: msgs.append("inside an avoid window (Monday mornings / Friday afternoons) - gentle caution")
    else: msgs.append("outside the recommended window; consider scheduling for Tue-Thu, 10am-2pm")
    if last_submission is not None:
        mins=(now-last_submission).total_seconds()/60
        if mins<30: msgs.append("less than 30 minutes since last submission - strong spacing warning")
        elif mins<120: msgs.append("less than 120 minutes since last submission - suggest spacing")
    msgs.append("These are the course's recommendations, not rules. Vary your timing within the window. Keep detailed timing records (the application log does this).")
    return msgs
