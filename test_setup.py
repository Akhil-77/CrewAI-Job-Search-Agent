"""Verify CrewAI + API key with the smallest job-search crew (Part 1)."""
import os, sys
from dotenv import load_dotenv

def main():
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("No OPENAI_API_KEY found.")
        print("Create a .env file in this folder (copy .env.example to .env) and add your key:")
        print("  cp .env.example .env   # then edit .env and replace the placeholder")
        return
    from _compat import Agent, Task, Crew
    agent = Agent(role="Job Search Assistant", goal="Help recent graduates find relevant job opportunities",
                  backstory="You are a career counselor who specializes in helping new graduates navigate the job market.", verbose=True)
    task = Task(description="Provide 3 tips for recent Masters graduates starting their job search",
                agent=agent, expected_output="A list of 3 practical tips")
    crew = Crew(agents=[agent], tasks=[task], verbose=True)
    print("Testing CrewAI setup...")
    result = crew.kickoff()
    print("Test completed successfully!")
    print("Result:")
    print(result)

if __name__ == "__main__":
    main()
