"""Crew 2: Application Materials + Part 5 variants/presets ordering.
Order: 1 translate_projects 2 deep_research 3 customize_resume 4 write_cover_letter 5 personalize 6 review 7 review_application
"""
from _compat import Agent, Task, Crew, Process, get_serper_tool, set_meta
from core.model_router import get_llm, tier_for, max_iter_for
from user_profile import profile_as_text_full
from templates import templates_as_text
from tools.keyword_analyzer import keyword_analyzer
from tools.consistency_checker import consistency_checker

GUARD_SEARCH = "Use only publicly available information (company websites, job postings, press releases). Do not collect personal contact details, such as emails, phone numbers, or personal profiles, of individuals."
GUARD_WRITE = "Skills listed as developing must be described as developing, never as expertise. Describe projects using only the facts provided; do not exaggerate scope or the candidate's role. Use the placeholders [ADD YOUR EMAIL] and [ADD YOUR PHONE] for contact details."

def _agent(role, goal, backstory, tools, key, economy=False, kind="writing"):
    return Agent(role=role, goal=goal, backstory=backstory, tools=tools, verbose=True, llm=get_llm(tier_for(key,economy),economy), max_iter=max_iter_for(kind,economy))

def build_crew(job_title="Data Analyst", company_name="Google", job_posting="", variant="baseline", industry=None, level=None,
               resume_guidance="None.", cover_letter_guidance="None.", company_research_cache="No cached research available; research the company yourself.", with_review=False, economy=False):
    profile = profile_as_text_full(); templates = templates_as_text()
    agents=[]; tasks=[]
    def add_agent(a): 
        if a not in agents: agents.append(a); return a
    # agents created lazily per task need
    resume_writer = _agent("Resume Customization Specialist","Create tailored resumes that highlight the most relevant experience and skills for each specific job opportunity","You are an expert at crafting compelling resumes that get past ATS systems and catch hiring managers' attention. You know how to emphasize different aspects of a candidate's background for different roles.",[keyword_analyzer],"resume_writer",economy)  # document_formatter dropped
    cover_letter_writer = _agent("Cover Letter Specialist","Write compelling, personalized cover letters that demonstrate genuine interest in the role and company while highlighting relevant qualifications","You are skilled at crafting engaging cover letters that tell a candidate's story in a way that resonates with hiring managers. You research companies thoroughly and connect candidate experience to business needs.",[get_serper_tool()],"cover_letter_writer",economy)  # writing_assistant dropped
    quality_controller = _agent("Application Quality Assurance","Ensure all application materials maintain consistent personal branding, accurate information, and professional standards","You have a keen eye for detail and ensure that all application materials present a cohesive professional image while being appropriately customized for each opportunity.",[consistency_checker],"quality_controller",economy)  # document_reviewer dropped

    task_by_name={}
    # 1 translate_projects (level technical)
    translate_task=None
    if level=="technical":
        technical_writer = _agent("Technical Application Specialist","Translate academic projects into industry-relevant technical experience","You excel at showing how academic work applies to real-world technical challenges",[],"technical_writer",economy)
        add_agent(technical_writer)
        translate_task = Task(description=f"Translate the candidate's academic projects into industry-relevant technical experience for the {job_title} role at {company_name}, using only the project facts in the candidate profile. Do not exaggerate scope or the candidate's role. Profile:\n{profile}", agent=technical_writer, expected_output="A set of project descriptions reframed in industry-relevant technical terms, grounded strictly in the profile facts")
        set_meta(translate_task, "task_name", "translate_projects_task"); tasks.append(translate_task); task_by_name["translate_projects_task"]=translate_task
    # 2 deep_research (variant)
    deep_task=None
    if variant=="deep_culture_research":
        research_agent = _agent("Company Culture Analyst","Find specific details about company values, recent news, and team culture to enable highly personalized applications","You excel at finding the human elements that make each company unique",[get_serper_tool()],"research_agent",economy,kind="research")
        add_agent(research_agent)
        deep_task = Task(description=f"Find specific details about {company_name}'s values, recent news, and team culture that can be referenced in a personalized application for the {job_title} role. Cite sources and mark anything unverified. {GUARD_SEARCH}", agent=research_agent, expected_output="A short list of specific, sourced details about the company that can be used to personalize an application")
        set_meta(deep_task, "task_name", "deep_research_task"); tasks.append(deep_task); task_by_name["deep_research_task"]=deep_task
    # 3 customize resume
    add_agent(resume_writer)
    ctx=[t for t in [translate_task, deep_task] if t]
    customize_resume_task = Task(description=f"Analyze the job posting for {job_title} at {company_name}. Identify key requirements and preferred qualifications. Select the most appropriate resume template and customize it to highlight relevant experience, skills, and achievements. Ensure ATS compatibility by including relevant keywords naturally. Job posting:\n{job_posting}\nCandidate profile:\n{profile}\nTemplates:\n{templates}\nUse only facts from the profile; never invent employers, dates, degrees, metrics, or skills. State which template was chosen and why. {GUARD_WRITE} Guidance: {resume_guidance}", agent=resume_writer, expected_output="A customized resume in professional format that emphasizes the most relevant qualifications for this specific role", context=ctx)
    set_meta(customize_resume_task, "task_name", "customize_resume_task"); tasks.append(customize_resume_task); task_by_name["customize_resume_task"]=customize_resume_task
    # 4 cover letter
    add_agent(cover_letter_writer)
    ctx2=[customize_resume_task]+([deep_task] if deep_task else [])
    write_cover_letter_task = Task(description=f"Research {company_name} including their mission, recent news, and company culture. Write a compelling cover letter for the {job_title} position that: 1) Shows knowledge of the company, 2) Explains why you're interested in this specific role, 3) Highlights 2-3 most relevant qualifications, 4) Demonstrates enthusiasm and cultural fit. Keep it concise and professional. Use only facts from the candidate profile; do not state company facts that were not found in research. {GUARD_SEARCH} {GUARD_WRITE} Guidance: {cover_letter_guidance} Cached research: {company_research_cache}", agent=cover_letter_writer, expected_output="A personalized cover letter that feels authentic and demonstrates genuine interest in the specific role and company", context=ctx2)
    set_meta(write_cover_letter_task, "task_name", "write_cover_letter_task"); tasks.append(write_cover_letter_task); task_by_name["write_cover_letter_task"]=write_cover_letter_task
    # 5 personalize
    personalize_task=None
    if variant=="personalizer":
        personalization_agent = _agent("Application Personalizer","Transform generic content into highly specific, company-tailored applications","You have a talent for connecting individual experiences to specific company needs",[],"personalization_agent",economy)
        add_agent(personalization_agent)
        personalize_task = Task(description=f"Rewrite any generic language in the draft resume and cover letter into specific, company-tailored statements for {company_name}, using only facts from the candidate profile and the company research. Do not add skills, experiences, or achievements that are not in the profile.", agent=personalization_agent, expected_output="Revised resume and cover letter with generic language replaced by specific, factual, company-tailored statements", context=[customize_resume_task, write_cover_letter_task])
        set_meta(personalize_task, "task_name", "personalize_task"); tasks.append(personalize_task); task_by_name["personalize_task"]=personalize_task
    # 6 review (Part 4, optional)
    review_task_obj=None
    if with_review:
        from crews.review_crew import quality_reviewer, make_review_task
        add_agent(quality_reviewer)
        review_task_obj = make_review_task(write_cover_letter_task)
        tasks.append(review_task_obj); task_by_name["review_task"]=review_task_obj
    # 7 quality review_application always last
    add_agent(quality_controller)
    ctx3=[customize_resume_task, write_cover_letter_task]+([personalize_task] if personalize_task else [])+([review_task_obj] if review_task_obj else [])
    review_application_task = Task(description="Review the customized resume and cover letter for consistency, accuracy, and professional presentation. Check that: 1) All dates and facts are accurate, 2) Writing style is consistent, 3) Formatting is professional, 4) Customization is appropriate for the role, 5) No spelling or grammar errors exist. Verify facts against the candidate profile using the consistency_checker tool.", agent=quality_controller, expected_output="A final application package with any necessary corrections and a quality assurance report", context=ctx3)
    set_meta(review_application_task, "task_name", "review_application_task"); tasks.append(review_application_task); task_by_name["review_application_task"]=review_application_task
    crew = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=True)
    set_meta(crew, "task_map", task_by_name); set_meta(crew, "agent_map", {a.role:a for a in agents})
    # expose named agents for tests/inspection
    set_meta(crew, "resume_writer", resume_writer); set_meta(crew, "cover_letter_writer", cover_letter_writer); set_meta(crew, "quality_controller", quality_controller)
    return crew
build_application_crew = build_crew
