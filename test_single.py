"""Test one agent/task at a time (Part 2). Usage: python test_single.py researcher|writer|analyst|parallel"""
import os, sys
from dotenv import load_dotenv
load_dotenv()
def main():
    choice = sys.argv[1] if len(sys.argv) > 1 else "writer"
    needs_serper = choice in ("researcher", "parallel")
    if not os.getenv("OPENAI_API_KEY"):
        print("Missing OPENAI_API_KEY. Copy .env.example to .env and add your key."); return
    if needs_serper and not os.getenv("SERPER_API_KEY"):
        print("Missing SERPER_API_KEY. Copy .env.example to .env and add your Serper key."); return
    from _compat import Crew, Task
    from agents import researcher, writer, analyst
    from tasks import create_research_task, create_writing_task, create_tracking_task, create_parallel_company_research_tasks
    from validation import run_all_checks
    if choice == "researcher":
        task = create_research_task(researcher); crew = Crew(agents=[researcher], tasks=[task], verbose=True)
    elif choice == "writer":
        sample = "Sample job: Data Analyst at ExampleCo, requires Python and SQL, Austin TX."
        task = Task(description=f"Create a tailored resume and cover letter for this job: {sample}. Use only the candidate profile, do not invent credentials.", agent=writer, expected_output="Customized application materials for each position")
        crew = Crew(agents=[writer], tasks=[task], verbose=True)
    elif choice == "analyst":
        sample = "Applications: ExampleCo Data Analyst 2026-10-01; SampleInc Analyst 2026-10-02"
        task = Task(description=f"Record application details and set follow-up reminders for: {sample}. Output a markdown table.", agent=analyst, expected_output="Updated application tracking spreadsheet")
        crew = Crew(agents=[analyst], tasks=[task], verbose=True)
    elif choice == "parallel":
        tasks = create_parallel_company_research_tasks(researcher); crew = Crew(agents=[researcher], tasks=tasks, verbose=True)
    else:
        print("Choose researcher, writer, analyst or parallel"); return
    result = crew.kickoff(); print(result); run_all_checks(str(result))

if __name__ == "__main__":
    main()
