"""CLI runner (Parts 3-5). Commands: jobs | apply | company | interview | review
AI prepares; human reviews, personalizes, and clicks submit. Nothing here submits applications.
"""
import argparse, os, sys, time
from datetime import datetime
from dotenv import load_dotenv

HUMAN_TODO = """HUMAN TODO (target: 5-10 minutes)
[ ] Add 2-3 personal touches (specific project details, genuine enthusiasm)
[ ] Adjust 1-2 sentences to match your natural writing style
[ ] Verify every company-specific claim and every fact about you
[ ] Replace contact markers: [ADD YOUR EMAIL], [ADD YOUR PHONE]
[ ] Remove or rewrite any generic phrases flagged below
"""

def _save_output(command, content, inputs_desc=""):
    os.makedirs("outputs", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join("outputs", f"{command}_{ts}.md")
    with open(path, "w", encoding="utf-8") as f: f.write(content)
    return path

def _dry_print(command, crew, inputs):
    print(f"[dry-run] command={command}")
    print(f"[dry-run] inputs={inputs}")
    print("[dry-run] agents:")
    for a in crew.agents: print(f"  - {getattr(a,'role','?')}")
    print("[dry-run] tasks:")
    for t in crew.tasks: print(f"  - {getattr(t,'task_name', getattr(t,'description','')[:60])}")
    print("[dry-run] No API calls made, no cost-log rows written.")

def _check_keys(need_serper, dry_run):
    if dry_run: return True
    missing=[]
    if not os.getenv("OPENAI_API_KEY"): missing.append("OPENAI_API_KEY")
    if need_serper and not os.getenv("SERPER_API_KEY"): missing.append("SERPER_API_KEY")
    if missing:
        print(f"Missing {', '.join(missing)}. Copy .env.example to .env and add your keys."); return False
    return True

def _budget_guard(force, economy):
    from core.cost_tracker import budget_status
    st = budget_status(); print(f"Budget: week ${st['week_spend']} / ${st['weekly_budget']}, month ${st['month_spend']}")
    for a in st["alerts_crossed"]: print(f"Notice: month-to-date crossed billing alert level ${a}")
    if st["warn"] and not st["over_budget"]: print("Warning: at/above 80% of weekly budget.")
    if st["over_budget"]:
        if not force: print("Weekly budget exhausted (100%). Re-run with --force to continue, or use --economy."); return False
        print("Over budget but --force given. Consider --economy: cheap tier everywhere, capped iterations; prefer editing drafts, shorter prompts, templates.")
    return True

def _privacy_gate(texts, allow_sensitive):
    from quality.privacy import scan_for_sensitive
    findings=[]
    for t in texts: findings += scan_for_sensitive(t or "")
    for f in findings: print(f"  [privacy {f['severity']}] {f['category']}: {f['evidence']}")
    if any(f["severity"]=="error" for f in findings) and not allow_sensitive:
        print("Privacy scan found error-level sensitive data. Fix it or pass --allow-sensitive."); return False
    return True

def main(argv=None):
    load_dotenv()
    parser = argparse.ArgumentParser(prog="run.py")
    sub = parser.add_subparsers(dest="command", required=True)
    def common(p):
        p.add_argument("--dry-run", action="store_true"); p.add_argument("--economy", action="store_true")
        p.add_argument("--force", action="store_true"); p.add_argument("--no-prompt", action="store_true")
        p.add_argument("--allow-sensitive", action="store_true"); p.add_argument("--model", default=None)
    p_jobs = sub.add_parser("jobs"); common(p_jobs); p_jobs.add_argument("--job-title", default="Data Analyst"); p_jobs.add_argument("--location", default="Austin, Texas"); p_jobs.add_argument("--key-skills", default="Python, SQL")
    p_apply = sub.add_parser("apply"); common(p_apply)
    p_apply.add_argument("--job-title", default="Data Analyst"); p_apply.add_argument("--company", default="Google"); p_apply.add_argument("--posting", default="")
    p_apply.add_argument("--with-review", action="store_true"); p_apply.add_argument("--highlight", action="append", default=[]); p_apply.add_argument("--tone", default="")
    p_apply.add_argument("--examples", action="append", default=[]); p_apply.add_argument("--use-structure", default=""); p_apply.add_argument("--use-achievements", default="")
    p_apply.add_argument("--variant", default="baseline"); p_apply.add_argument("--industry", default=None); p_apply.add_argument("--level", default=None)
    p_apply.add_argument("--batch", default=""); p_apply.add_argument("--pause-seconds", type=int, default=5)
    p_co = sub.add_parser("company"); common(p_co); p_co.add_argument("--company", default="Google"); p_co.add_argument("--refresh", action="store_true")
    p_co.add_argument("--batch", default=""); p_co.add_argument("--pause-seconds", type=int, default=5); p_co.add_argument("--industry", default=None); p_co.add_argument("--lite", action="store_true"); p_co.add_argument("--from-targets", action="store_true")
    p_int = sub.add_parser("interview"); common(p_int); p_int.add_argument("--job-title", default="Data Analyst"); p_int.add_argument("--company", default="Google"); p_int.add_argument("--lite", action="store_true")
    p_rev = sub.add_parser("review"); common(p_rev); p_rev.add_argument("--file", required=False, default="")
    args = parser.parse_args(argv)
    cmd = args.command; dry = getattr(args, "dry_run", False); economy = getattr(args, "economy", False) or getattr(args, "variant", "")=="economy"
    need_serper = cmd in ("jobs","apply","company") or (cmd=="interview")
    if cmd=="interview": need_serper=False  # optional search tool
    if cmd=="review": need_serper=False

    # Batch handling (company / apply) - sequential, cache-aware, budget-aware
    if getattr(args, "batch", "") and not dry:
        print(f"Batch mode from {args.batch} (pause {args.pause_seconds}s). Batch implies --no-prompt.")
    if getattr(args, "from_targets", False) and cmd=="company":
        from workflow.targets import list_targets; companies=[t["company"] for t in list_targets()]
        print(f"From targets: {companies}")

    # Build crew + inputs
    inputs={}; crew=None; task_type=cmd
    if cmd=="jobs":
        from crews.job_research_crew import build_crew; crew=build_crew(economy=economy)
        inputs={"job_title":args.job_title,"location":args.location,"key_skills":args.key_skills}; task_type="job_search"
    elif cmd=="apply":
        posting_text=""
        if args.posting:
            if os.path.exists(args.posting):
                with open(args.posting,encoding="utf-8") as f: posting_text=f.read()
                # save posting copy (Part 4 documentation strategy)
                import re, config as _c; os.makedirs(os.path.join(_c.DATA_DIR,"postings"), exist_ok=True)
                slug=re.sub(r"[^a-z0-9]+","_", f"{args.company}_{args.job_title}".lower()).strip("_")
                with open(os.path.join(_c.DATA_DIR,"postings", f"{datetime.now().strftime('%Y%m%d')}_{slug}.txt"),"w",encoding="utf-8") as f: f.write(posting_text)
            else: posting_text=args.posting
        from presets.variants import build_guidance
        from core.library import get_item
        lib_texts=[]
        if args.use_structure:
            it=get_item("cover_letter_structures", args.use_structure); lib_texts.append(f"Reuse this structure: {it['text']}" if it else "")
        if args.use_achievements:
            for aid in args.use_achievements.split(","):
                it=get_item("achievements", aid.strip()); lib_texts.append(f"Reuse this achievement: {it['text']}" if it else "")
        guidance=build_guidance(args.industry, args.level, {"highlight":args.highlight,"tone":args.tone,"examples":args.examples}, lib_texts)
        # cached company research
        from core.cache import load_company_research
        cached=load_company_research(args.company); cache_text="Use this saved research; only search for gaps.\n"+str(cached) if cached else "No cached research available; research the company yourself."
        from crews.application_crew import build_crew
        crew=build_crew(job_title=args.job_title, company_name=args.company, job_posting=posting_text, variant=args.variant, industry=args.industry, level=args.level, resume_guidance=guidance["resume_guidance"], cover_letter_guidance=guidance["cover_letter_guidance"], company_research_cache=cache_text, with_review=args.with_review, economy=economy)
        inputs={"job_title":args.job_title,"company_name":args.company,"job_posting":posting_text}
        task_type="application"
        args._posting_text=posting_text
    elif cmd=="company":
        from core.cache import load_company_research, save_company_research
        if not dry and not getattr(args,"refresh",False):
            cached=load_company_research(args.company)
            if cached and not getattr(args,"from_targets",False):
                print(f"Using cached research for {args.company}:"); print(cached); return
        from crews.company_research_crew import build_crew; crew=build_crew(company_name=args.company, lite=args.lite, industry=args.industry, economy=economy)
        inputs={"company_name":args.company}; task_type="company_research"
    elif cmd=="interview":
        from crews.interview_prep_crew import build_crew; crew=build_crew(lite=args.lite, economy=economy)
        inputs={"job_title":args.job_title,"company_name":args.company}; task_type="interview_prep"
    elif cmd=="review":
        draft=""
        if args.file and os.path.exists(args.file):
            with open(args.file,encoding="utf-8") as f: draft=f.read()
        from crews.review_crew import build_review_crew; crew=build_review_crew(draft_text=draft)
        inputs={"draft_text":draft}; task_type="review"

    if dry:
        _dry_print(cmd, crew, inputs); return
    if not _check_keys(need_serper, dry): return
    if not _budget_guard(args.force, economy): return
    # privacy scan on inputs
    from user_profile import profile_as_text_full
    texts=[profile_as_text_full(), str(inputs)]
    if not _privacy_gate(texts, args.allow_sensitive): return

    print(f"Running {cmd} crew...")
    result = crew.kickoff(inputs=inputs)
    result_text=str(result)
    # post-run scans for apply
    extra=""
    if cmd=="apply":
        from quality.red_flags import scan, format_report; from quality.privacy import scan_output_for_third_party_contacts
        findings=scan(result_text, kind="cover_letter", industry=args.industry)
        extra="\n\n"+format_report(findings)
        for f in scan_output_for_third_party_contacts(result_text): extra+=f"\n  [privacy warn] {f['category']}: {f['evidence']}"
        content=HUMAN_TODO+extra+"\n\n"+result_text
        path=_save_output(cmd, content)
        from workflow.last_run import write_last_run
        write_last_run({"command":cmd,"company":args.company,"role":args.job_title,"variant":args.variant,"industry":args.industry,"level":args.level,"cost_estimate":"","output_file":path,"finished_at":datetime.now().isoformat()})
        print(f"Saved to {path}")
        if not args.no_prompt:
            print("Checkpoint 1: review the draft, run the checklist (manage.py checklist), add personal touches.")
    elif cmd=="company":
        from core.cache import save_company_research
        # cache first two task outputs if available, else full result
        save_company_research(args.company, {"research":result_text,"culture":"","company":args.company})
        path=_save_output(cmd, result_text); print(f"Saved to {path} and cached.")
    else:
        path=_save_output(cmd, result_text); print(f"Saved to {path}")
    print(result_text)
    from core.cost_tracker import record_run; record_run(task_type, crew=crew)
    print("\nReminder: outputs are AI-generated, partly based on model knowledge - verify company facts, salaries, deadlines, and review as a human before use.")

if __name__=="__main__":
    main()
