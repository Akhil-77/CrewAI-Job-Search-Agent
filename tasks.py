"""Part 2 task builders - parameterized, explicit context handoffs."""
from _compat import Task
from user_profile import profile_as_text

def create_research_task(agent, role_query="entry-level data analyst positions in major tech companies. Focus on roles requiring Python and SQL skills", location_hint="", num_jobs=5):
    description = f"Search for {role_query}"
    if location_hint: description += f" in {location_hint}"
    description += ". Include application links."
    return Task(description=description, agent=agent,
                expected_output=f"A list of {num_jobs} job opportunities with company name, job title, location, and key requirements.")

def create_writing_task(agent, context_tasks=None):
    desc = ("Create a tailored resume and cover letter for each job found. "
            f"Candidate profile:\n{profile_as_text()}\nUse the real job details from the research task and do not invent employers, projects, or credentials.")
    return Task(description=desc, agent=agent, expected_output="Customized application materials for each position",
                context=context_tasks or [])

def create_tracking_task(agent, context_tasks=None):
    desc = ("Record application details and set follow-up reminders. Build a tracking table with company, role, "
            "date prepared, status, follow-up date, and a short suggestion on improving the search. Output as a markdown table.")
    return Task(description=desc, agent=agent, expected_output="Updated application tracking spreadsheet",
                context=context_tasks or [], output_file="application_tracker.md")

def create_parallel_company_research_tasks(agent):
    # Parallel tasks must not depend on each other; async tasks are gathered by a later sync task / test_single.
    t1 = Task(description="Research Google's company culture and recent news", agent=agent, expected_output="Company profile with culture insights", async_execution=True)
    t2 = Task(description="Research Microsoft's company culture and recent news", agent=agent, expected_output="Company profile with culture insights", async_execution=True)
    return [t1, t2]
