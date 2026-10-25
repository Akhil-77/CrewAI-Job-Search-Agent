"""Management CLI - no LLM calls. Commands: pre-submit, cost, cache, library, log, ethics-check,
checklist, metrics, insights, dashboard, variants, compare-variants, targets, plan, daily, weekly-review, cadence, time
"""
import argparse, csv, json, os, sys
from datetime import datetime
import config

def cmd_pre_submit(args):
    path=args.file
    if not os.path.exists(path): print(f"File not found: {path}"); return
    with open(path,encoding="utf-8") as f: text=f.read()
    from quality.red_flags import scan, format_report; print(format_report(scan(text)))
    from quality.privacy import scan_for_sensitive
    for f in scan_for_sensitive(text): print(f"  [privacy {f['severity']}] {f['category']}: {f['evidence']}")
    from quality.checklist import load_checklist, run_checklist, run_red_flag_questions, RED_FLAG_QUESTIONS
    kind="five_minute" if args.checklist=="five_minute" else "standard"
    items=load_checklist(kind); print(f"Checklist ({kind}): {len(items)} items")
    res=run_checklist(items, interactive=not args.no_prompt)
    print(f"Checklist result: {res}")
    rf=run_red_flag_questions(interactive=not args.no_prompt); print(f"Red Flag Check: {rf}")
    from core.compliance import check_before_submission; g=check_before_submission(args.platform)
    for w_ in g["warnings"]: print(f"  [guard warn] {w_}")
    for n in g["notes"]: print(f"  [guard note] {n}")
    print(g["guideline"])
    approved={"timestamp":datetime.now().isoformat(),"checklist":str(res),"file":path}
    with open(path+".approved.json","w",encoding="utf-8") as f: json.dump(approved,f,indent=2)
    print(f"Approved marker written: {path}.approved.json (nothing was submitted)")

def cmd_cost(args):
    from core import cost_tracker
    if args.cost_command=="report":
        r=cost_tracker.report(); print(f"Week: ${r['week']}  Month: ${r['month']}  Runs: {r['n_runs']}"); print(f"By task type: {r['by_task_type']}"); print(f"Budget: {r['budget']}")
    elif args.cost_command=="log":
        cost_tracker.append_row(datetime.now().date().isoformat(), args.task_type, args.model or config.DEFAULT_MODEL, "", "", float(args.amount) if args.amount else None, args.notes or "")
        print("Manual cost entry added.")

def cmd_cache(args):
    from core import cache
    if args.cache_command=="list": print(cache.list_cache())
    elif args.cache_command=="clear": cache.clear_cache(args.company); print("Cache cleared.")

def cmd_library(args):
    from core import library
    if args.library_command=="add":
        text=args.text or ""
        if args.file:
            with open(args.file,encoding="utf-8") as f: text=f.read()
        item=library.add_item(args.category, args.title, text, [t.strip() for t in args.tags.split(",")] if args.tags else [])
        print(item)
    elif args.library_command=="list": print(library.list_items(args.category))
    elif args.library_command=="show": print(library.get_item(args.category, args.id))
    elif args.library_command=="delete": print("deleted" if library.delete_item(args.category, args.id) else "not found")

def cmd_log(args):
    from core import application_log as log; from core.compliance import check_before_submission
    if args.log_command=="add":
        fields={}
        # from last run prefill
        if args.from_last_run:
            from workflow.last_run import read_last_run; lr=read_last_run() or {}
            fields={"company":lr.get("company",""),"role":lr.get("role",""),"config_variant":lr.get("variant","baseline"),"industry":lr.get("industry") or "","role_level":lr.get("level") or "","cost_estimate":lr.get("cost_estimate") or "","ai_generated":"Yes"}
            of=lr.get("output_file","")
            if of and not os.path.exists(of+".approved.json") and not args.confirm_unreviewed:
                print(f"Refusing: output {of} has no .approved.json from pre-submit. Run manage.py pre-submit first, or pass --confirm-unreviewed."); return
        if args.output_file and not os.path.exists(args.output_file+".approved.json") and not args.confirm_unreviewed:
            print("Refusing: output has no .approved.json from pre-submit. Run pre-submit first, or pass --confirm-unreviewed."); return
        for k in ["company","role","platform","industry","role_level","ai_generated","edit_level","config_variant","response","interview","notes","activity_type"]:
            v=getattr(args,k,None)
            if v: fields[k]=v
        g=check_before_submission(fields.get("platform"))
        for w_ in g["warnings"]: print(f"  [guard warn] {w_}")
        print(g["guideline"])
        if not args.yes:
            try:
                if input("Write this log entry? (y/n) ").strip().lower() not in ("y","yes"): print("Cancelled."); return
            except EOFError: pass
        nid=log.add_entry(**fields); print(f"Logged entry {nid}")
    elif args.log_command=="list":
        rows=log.list_entries(); 
        if args.since: rows=[r for r in rows if r["logged_at"][:10]>=args.since]
        for r in rows: print(r)
    elif args.log_command=="update":
        fields={}
        mapping={"response":args.response,"response_days":args.response_days,"interview":args.interview,"quality_score":args.quality,"edit_level":args.edit_level,"notes":args.notes}
        for k,v in mapping.items():
            if v is not None: fields[k]= {"yes":"Yes","no":"No","pending":"Pending"}.get(str(v).lower(), v)
        print(log.update_entry(args.id, **fields))

def cmd_ethics(args):
    from core import application_log as log
    from datetime import timedelta; since=(datetime.now()-timedelta(days=7)).isoformat()
    rows=[r for r in log.list_entries() if r["logged_at"]>=since]
    print(f"Ethics check - past 7 days: {len(rows)} entries")
    by={}
    for r in rows: by[r.get("platform","")]=by.get(r.get("platform",""),0)+1
    print(f"By platform: {by}")
    warns=[r for r in rows if "warning" in (r.get("notes") or "").lower()]; print(f"Entries with warnings in notes: {len(warns)}")
    risky=[r for r in rows if r.get("ai_generated")=="Yes" and r.get("edit_level")=="none"]; print(f"AI-generated with no edits (review authenticity): {len(risky)}")
    qs=["Did I review my applications for accuracy and authenticity?","Did I stay within platform limits?","Does my AI usage align with my values?","Does anything feel off that I should adjust?"]
    answers={}
    interactive = not args.no_prompt
    for q in qs:
        answers[q]= input(f"{q} (y/n) ") if interactive else "unchecked"
        print(f"  {q} -> {answers[q]}")
    os.makedirs(config.DATA_DIR, exist_ok=True); p=os.path.join(config.DATA_DIR,"ethics_checks.csv")
    exists=os.path.exists(p)
    with open(p,"a",newline="",encoding="utf-8") as f:
        wtr=csv.writer(f)
        if not exists: wtr.writerow(["date"]+qs)
        wtr.writerow([datetime.now().isoformat()]+[answers[q] for q in qs])
    print(f"Saved to {p}")

def main(argv=None):
    parser=argparse.ArgumentParser(prog="manage.py"); sub=parser.add_subparsers(dest="command", required=True)
    p=sub.add_parser("pre-submit"); p.add_argument("file"); p.add_argument("--platform",default=""); p.add_argument("--checklist",default="standard",choices=["standard","five_minute"]); p.add_argument("--no-prompt",action="store_true")
    p=sub.add_parser("cost"); sc=p.add_subparsers(dest="cost_command",required=True); r=sc.add_parser("report"); l=sc.add_parser("log"); l.add_argument("--task-type",default="manual"); l.add_argument("--amount",default=""); l.add_argument("--notes",default=""); l.add_argument("--model",default="")
    p=sub.add_parser("cache"); sc=p.add_subparsers(dest="cache_command",required=True); sc.add_parser("list"); c=sc.add_parser("clear"); c.add_argument("--company",default=None)
    p=sub.add_parser("library"); sc=p.add_subparsers(dest="library_command",required=True)
    a=sc.add_parser("add"); a.add_argument("category"); a.add_argument("--title",required=True); a.add_argument("--text",default=""); a.add_argument("--file",default=""); a.add_argument("--tags",default="")
    li=sc.add_parser("list"); li.add_argument("category",nargs="?")
    sh=sc.add_parser("show"); sh.add_argument("category"); sh.add_argument("id")
    de=sc.add_parser("delete"); de.add_argument("category"); de.add_argument("id")
    p=sub.add_parser("log"); sc=p.add_subparsers(dest="log_command",required=True)
    ad=sc.add_parser("add"); ad.add_argument("--company",default=""); ad.add_argument("--role",default=""); ad.add_argument("--platform",default=""); ad.add_argument("--industry",default=""); ad.add_argument("--role-level",dest="role_level",default=""); ad.add_argument("--ai-generated",dest="ai_generated",default=""); ad.add_argument("--edit-level",dest="edit_level",default=""); ad.add_argument("--config-variant",dest="config_variant",default=""); ad.add_argument("--response",default=""); ad.add_argument("--interview",default=""); ad.add_argument("--notes",default=""); ad.add_argument("--activity-type",dest="activity_type",default="application"); ad.add_argument("--from-last-run",action="store_true"); ad.add_argument("--output-file",default=""); ad.add_argument("--confirm-unreviewed",action="store_true"); ad.add_argument("--yes",action="store_true")
    li2=sc.add_parser("list"); li2.add_argument("--since",default="")
    up=sc.add_parser("update"); up.add_argument("id"); up.add_argument("--response",default=None); up.add_argument("--response-days",dest="response_days",default=None); up.add_argument("--interview",default=None); up.add_argument("--quality",default=None); up.add_argument("--edit-level",dest="edit_level",default=None); up.add_argument("--notes",default=None)
    p=sub.add_parser("ethics-check"); p.add_argument("--no-prompt",action="store_true")
    p=sub.add_parser("checklist"); p.add_argument("--five-minute",action="store_true"); p.add_argument("--no-prompt",action="store_true")
    p=sub.add_parser("metrics"); p.add_argument("--period",default="month"); p.add_argument("--by",default="")
    p=sub.add_parser("insights")
    p=sub.add_parser("dashboard"); p.add_argument("--mark-reviewed",action="store_true")
    p=sub.add_parser("variants"); sc=p.add_subparsers(dest="variants_command",required=True); sc.add_parser("list")
    p=sub.add_parser("compare-variants"); p.add_argument("--baseline",default="baseline"); p.add_argument("--min-n",type=int,default=5)
    p=sub.add_parser("targets"); sc=p.add_subparsers(dest="targets_command",required=True)
    ta=sc.add_parser("add"); ta.add_argument("--company",required=True); ta.add_argument("--role",required=True); ta.add_argument("--platform",required=True); ta.add_argument("--posting",default=""); ta.add_argument("--priority",default=""); ta.add_argument("--notes",default="")
    sc.add_parser("list"); tr=sc.add_parser("remove"); tr.add_argument("id"); ts=sc.add_parser("status"); ts.add_argument("id"); ts.add_argument("status")
    p=sub.add_parser("plan"); p.add_argument("--research",action="store_true")
    p=sub.add_parser("daily"); p.add_argument("--target",required=True); p.add_argument("--dry-run",action="store_true"); p.add_argument("--variant",default="baseline"); p.add_argument("--industry",default=None); p.add_argument("--level",default=None)
    p=sub.add_parser("weekly-review"); p.add_argument("--no-prompt",action="store_true")
    p=sub.add_parser("cadence"); p.add_argument("--mark",default="")
    p=sub.add_parser("time"); sc=p.add_subparsers(dest="time_command",required=True)
    ta2=sc.add_parser("add"); ta2.add_argument("--hours-spent",required=True); ta2.add_argument("--hours-saved",required=True); ta2.add_argument("--week",default=None); ta2.add_argument("--notes",default="")
    sc.add_parser("list")
    args=parser.parse_args(argv)
    if args.command=="pre-submit": cmd_pre_submit(args)
    elif args.command=="cost": cmd_cost(args)
    elif args.command=="cache": cmd_cache(args)
    elif args.command=="library": cmd_library(args)
    elif args.command=="log": cmd_log(args)
    elif args.command=="ethics-check": cmd_ethics(args)
    elif args.command=="checklist":
        from quality.checklist import load_checklist, run_checklist
        items=load_checklist("five_minute" if args.five_minute else "standard"); print(run_checklist(items, interactive=not args.no_prompt))
    elif args.command=="metrics":
        from analytics.metrics import compute_metrics, breakdown
        if args.by: print(breakdown(args.by, args.period))
        else: print(compute_metrics(args.period))
    elif args.command=="insights":
        from analytics.insights import get_insights; print(get_insights())
    elif args.command=="dashboard":
        from analytics.insights import dashboard_text; print(dashboard_text())
        if args.mark_reviewed:
            from workflow.weekly_review import mark_cadence; mark_cadence("monthly"); print("Monthly review marked.")
    elif args.command=="variants":
        from presets.variants import list_variants; print(list_variants())
    elif args.command=="compare-variants":
        from analytics.experiments import format_comparison; print(format_comparison(args.baseline, args.min_n))
    elif args.command=="targets":
        from workflow.targets import add_target, list_targets, remove_target, set_status
        if args.targets_command=="add":
            nid=add_target(args.company,args.role,args.platform,args.posting,args.priority,args.notes); print(f"Target {nid} added.")
            if args.posting and os.path.exists(args.posting):
                import shutil; os.makedirs(os.path.join(config.DATA_DIR,"postings"),exist_ok=True); shutil.copy(args.posting, os.path.join(config.DATA_DIR,"postings", os.path.basename(args.posting)))
        elif args.targets_command=="list":
            rows=list_targets(); 
            for r in rows: print(r)
            print(f"Total: {len(rows)} (guidance: 5-7 high-quality opportunities per week)")
            if len(rows)<5 or len(rows)>7: print("Warning: outside 5-7 range.")
        elif args.targets_command=="remove": print(remove_target(args.id))
        elif args.targets_command=="status": print(set_status(args.id,args.status))
    elif args.command=="plan":
        from workflow.planner import save_plan; path,text=save_plan(); print(text); print(f"Saved to {path}")
        if args.research: print("Research step: run 'python run.py company --from-targets --lite' to batch research (respects budget/cache).")
    elif args.command=="daily":
        from workflow.targets import get_target; from workflow.daily import daily_steps
        t=get_target(args.target)
        if not t: print("Target not found"); return
        print(f"Daily routine for {t}")
        for title,steps in daily_steps(t):
            print(f"\n{title}")
            for s in steps: print(f"  - {s}")
            if not args.dry_run:
                try: input("Press Enter when done...")
                except EOFError: pass
        print("Reminder: you submit manually on the platform. This routine never submits anything.")
    elif args.command=="weekly-review":
        from analytics.metrics import breakdown, compute_metrics
        print("Weekly review"); print(compute_metrics("week"))
        for by in ["config_variant","edit_level","industry"]: print(by, breakdown(by,"month"))
        issues=""; improvements=""
        if not args.no_prompt:
            try: issues=input("Which quality issues slipped through? "); improvements=input("Improvements to plan for next week? ")
            except EOFError: pass
            extra=input("Add a custom checklist item (blank to skip): ")
            if extra.strip():
                os.makedirs(config.DATA_DIR,exist_ok=True)
                with open(os.path.join(config.DATA_DIR,"custom_checklist_items.txt"),"a",encoding="utf-8") as f: f.write("□ "+extra.strip()+"\n")
        from core.time_log import monday_of; d=os.path.join(config.DATA_DIR,"weekly_reviews"); os.makedirs(d,exist_ok=True)
        pth=os.path.join(d,f"{monday_of()}.md")
        with open(pth,"w",encoding="utf-8") as f: f.write(f"# Weekly review {monday_of()}\nIssues: {issues}\nImprovements: {improvements}\n")
        from workflow.weekly_review import mark_cadence; mark_cadence("weekly"); print(f"Saved to {pth}")
    elif args.command=="cadence":
        from workflow.weekly_review import cadence_status, mark_cadence
        if args.mark: mark_cadence(args.mark); print(f"Marked {args.mark}")
        print(cadence_status()); print("Weekly: review metrics and adjust tactics. Monthly: analyze patterns and update agent configurations (compare-variants, dashboard). Quarterly: reassess overall strategy and industry focus. Ongoing: stay updated on industry trends.")
    elif args.command=="time":
        from core import time_log
        if args.time_command=="add": print(time_log.add_week(float(args.hours_spent), float(args.hours_saved), args.week, args.notes))
        else: print(time_log.list_weeks())

if __name__=="__main__":
    main()
