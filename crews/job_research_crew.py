"""Crew 1: Job Research and Matching - 1 agent, 3 tasks."""
from _compat import Agent, Task, Crew, Process, get_serper_tool, get_scrape_tool, set_meta
from core.model_router import get_llm, tier_for, max_iter_for
from user_profile import skills_as_text
import config

def build_crew(economy=False):
    job_researcher = Agent(role="Job Research Specialist", goal="Find and evaluate job opportunities that match specific skills and preferences",
        backstory="You are an expert at finding relevant job opportunities across multiple platforms. You understand how to match job requirements with candidate skills and can identify the most promising opportunities.",
        tools=[get_serper_tool(), get_scrape_tool()], verbose=True, llm=get_llm(tier_for("job_researcher",economy),economy), max_iter=max_iter_for("research",economy))
    search_jobs_task = Task(description="Search for {job_title} positions in {location} across LinkedIn, Indeed, and Glassdoor. Focus on roles requiring {key_skills}. Collect job title, company, location, salary range, and key requirements for each position. Also collect application deadline and link where available. Report any platform that could not be accessed. Do not invent listings. Use only publicly available information (company websites, job postings, press releases). Do not collect personal contact details, such as emails, phone numbers, or personal profiles, of individuals.",
        agent=job_researcher, expected_output="A structured list of job opportunities with complete details for evaluation")
    set_meta(search_jobs_task, "task_name", "search_jobs_task")
    match_jobs_task = Task(description="Analyze each job opportunity and calculate a match score based on required skills, experience level, and industry. Rate each job from 1-10 where 10 is a perfect match. Consider both technical requirements and soft skills. Candidate skills:\n"+skills_as_text(),
        agent=job_researcher, expected_output="Each job opportunity with a detailed match score and explanation of why it matches or doesn't match the candidate profile", context=[search_jobs_task])
    set_meta(match_jobs_task, "task_name", "match_jobs_task")
    filter_desc = f"Filter job opportunities with match scores below {config.MIN_MATCH_SCORE}/10. For remaining jobs, rank them by: 1) Match score ({config.RANK_WEIGHTS['match_score']}%), 2) Salary competitiveness ({config.RANK_WEIGHTS['salary']}%), 3) Company reputation ({config.RANK_WEIGHTS['reputation']}%), 4) Growth potential ({config.RANK_WEIGHTS['growth']}%). Present top {config.TOP_N_JOBS} opportunities with reasoning. Each entry must include: match score, key reasons it fits, potential concerns, and a clear label where salary/reputation/growth are estimates."
    filter_rank_task = Task(description=filter_desc, agent=job_researcher, expected_output="A ranked list of the top 10 job opportunities with detailed explanations for each ranking decision", context=[match_jobs_task])
    set_meta(filter_rank_task, "task_name", "filter_rank_task")
    crew = Crew(agents=[job_researcher], tasks=[search_jobs_task, match_jobs_task, filter_rank_task], process=Process.sequential, verbose=True)
    set_meta(crew, "agent_map", {"job_researcher": job_researcher}); set_meta(crew, "task_map", {"search_jobs_task":search_jobs_task,"match_jobs_task":match_jobs_task,"filter_rank_task":filter_rank_task})
    return crew
build_job_research_crew = build_crew
