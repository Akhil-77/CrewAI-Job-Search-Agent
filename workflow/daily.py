"""Guided 3-phase daily routine - never submits anything."""
def daily_steps(target):
    return [("Phase 1. AI generation (15 min)", ["Load saved company research from cache; if missing, offer company --lite","Run application crew with target company/role/posting and variant/industry/level options","Run first-pass interview prep: run.py interview --lite"]),
            ("Phase 2. Human review and enhancement (20 min)", ["Show red-flag report; run standard checklist","Add 2-3 personal touches and specific examples","Adjust tone to company culture; verify all factual claims"]),
            ("Phase 3. Final preparation (10 min)", ["Run pre-submit with five-minute check, privacy scan, timing/compliance guards","Format documents; copy approved files to outputs/ready_to_submit/","Create log entry via log add --from-last-run; set target status","You submit manually on the platform - this routine never submits anything"])]
