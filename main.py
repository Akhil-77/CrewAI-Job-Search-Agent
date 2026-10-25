"""Part 2 full crew: research -> writing -> tracking (sequential)."""
import os, argparse
from dotenv import load_dotenv

def main():
    load_dotenv()
    missing = [k for k in ("OPENAI_API_KEY", "SERPER_API_KEY") if not os.getenv(k)]
    if missing:
        print(f"Missing {', '.join(missing)}. Copy .env.example to .env and add your keys (see README for Serper).")
        return
    parser = argparse.ArgumentParser(); parser.add_argument("--role", default="entry-level data analyst positions in major tech companies. Focus on roles requiring Python and SQL skills")
    parser.add_argument("--location", default=""); parser.add_argument("--num-jobs", type=int, default=5)
    args = parser.parse_args()
    from _compat import Crew, Process
    from agents import researcher, writer, analyst
    from tasks import create_research_task, create_writing_task, create_tracking_task
    from validation import run_all_checks
    research_task = create_research_task(researcher, args.role, args.location, args.num_jobs)
    writing_task = create_writing_task(writer, [research_task])
    tracking_task = create_tracking_task(analyst, [writing_task])
    job_search_crew = Crew(agents=[researcher, writer, analyst], tasks=[research_task, writing_task, tracking_task], process=Process.sequential, verbose=True)
    print("Starting job search crew...")
    result = job_search_crew.kickoff()
    print(result)
    run_all_checks(str(result))
    print("\nReminder: verify job details, links and deadlines manually. A human reviews and submits every application.")

if __name__ == "__main__":
    main()
