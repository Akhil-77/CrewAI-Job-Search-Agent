"""First real agent: Senior Career Research Specialist (Part 1).
Note: output is based on the model's training data, not live job postings - verify against current sources.
"""
import os
from dotenv import load_dotenv
load_dotenv()
# Configurable field - examples: "digital marketing", "software engineering", "business analysis", "project management"
FIELD = "data science"

from _compat import Agent, Task, Crew

job_researcher = Agent(
    role="Senior Career Research Specialist",
    goal="Help recent Masters graduates identify promising career opportunities and develop effective job search strategies",
    backstory="You are an experienced career counselor with 15 years of experience helping recent graduates transition into their careers. You understand the current job market, know what employers are looking for, and can provide practical, actionable advice. You're encouraging but realistic about the challenges new graduates face.",
    verbose=True, allow_delegation=False)

career_research_task = Task(
    description=f"""Analyze the current job market for recent Masters graduates in {FIELD} and provide a comprehensive report including:
1. Top 5 in-demand skills employers are seeking
2. 3 types of entry-level positions to target
3. Salary expectations for new graduates
4. 5 specific strategies for standing out as a candidate
5. Common mistakes to avoid during the job search
Focus on actionable advice that a recent graduate can implement immediately.""",
    agent=job_researcher, expected_output="A detailed report with specific recommendations and actionable steps")

research_crew = Crew(agents=[job_researcher], tasks=[career_research_task], verbose=True)

# Optional extras (commented out):
# company_research_task = Task(description="Research Google's company culture, recent initiatives, and what they look for in new graduates. Provide interview preparation tips.", agent=job_researcher, expected_output="Company research summary")
# resume_strategy_task = Task(description="Provide 5 specific tips for optimizing a resume for data science positions, including keywords and formatting advice.", agent=job_researcher, expected_output="Resume tips")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("No OPENAI_API_KEY found. Copy .env.example to .env and add your key.")
    else:
        print("Starting job market research...")
        print("This may take 30-60 seconds...\n")
        result = research_crew.kickoff()
        print("="*50); print("RESEARCH COMPLETE"); print("="*50); print(result)
        print("\nNote: based on training data, not live postings - verify against current sources.")
