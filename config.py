"""Central configuration. All thresholds, model names, prices and limits live here only."""
import os

DATA_DIR = os.getenv("JOBSEARCH_DATA_DIR", "data")

# Part 3 ranking
MIN_MATCH_SCORE = 6
RANK_WEIGHTS = {"match_score": 40, "salary": 30, "reputation": 20, "growth": 10}
TOP_N_JOBS = 10

# Part 4 model tiers - check OpenAI pricing/models at implementation time and edit here.
# Defaults use current small/large naming pattern; override via env vars.
CHEAP_MODEL = os.getenv("CHEAP_MODEL", "gpt-4o-mini")
STRONG_MODEL = os.getenv("STRONG_MODEL", "gpt-4o")
MODEL_TIERS = {"cheap": CHEAP_MODEL, "strong": STRONG_MODEL}
DEFAULT_MODEL = CHEAP_MODEL
# price per 1K tokens (prompt, completion) USD - editable, illustrative; verify on openai.com/pricing
MODEL_PRICES_PER_1K = {
    CHEAP_MODEL: (0.00015, 0.0006),
    STRONG_MODEL: (0.0025, 0.01),
    "gpt-4o-mini": (0.00015, 0.0006),
    "gpt-4o": (0.0025, 0.01),
}
AGENT_TIER = {
    "job_researcher": "cheap", "company_researcher": "cheap", "culture_analyst": "cheap",
    "question_generator": "cheap", "mock_interview_designer": "cheap", "interview_simulator": "cheap",
    "talking_points_generator": "cheap", "quality_controller": "cheap", "quality_reviewer": "cheap",
    "research_agent": "cheap", "tech_research_agent": "cheap",
    "resume_writer": "strong", "cover_letter_writer": "strong", "answer_coach": "strong",
    "personalization_agent": "strong", "technical_writer": "strong",
}
MAX_ITER = {"writing": 4, "research": 8}

WEEKLY_BUDGET_USD = 5.0
MONTHLY_TARGET_RANGE_USD = (15, 20)
BILLING_ALERT_LEVELS_USD = (10, 15, 20)
BUDGET_WARN_FRACTION = 0.8

CACHE_TTL_DAYS = 14
LIBRARY_CATEGORIES = ["cover_letter_structures", "achievements", "interview_answers",
                      "agent_configs", "prompts", "research_templates", "workflows"]

GENERIC_PHRASES = ["I am excited to contribute to your team", "team player", "hard worker",
                   "passionate about", "fast learner", "results-driven", "I believe I would be a great fit"]
FORMAL_PHRASES = ["I am writing to express", "esteemed", "hereby", "utilize", "pursuant"]
FORMAL_THRESHOLD = 3

PLATFORM_LIMITS = {
    "linkedin": {"connection_requests_per_week": (20, 30)},
    "indeed": {"applications_per_day": (10, 15)},
    "glassdoor": {"company_research_queries_per_day": 10},
    "angellist": {"note": "Be selective with startup applications: quality over quantity."},
    "wellfound": {"note": "Be selective with startup applications: quality over quantity."},
}
MAX_WEEKLY_APPLICATIONS = 5
MIN_MINUTES_BETWEEN_SUBMISSIONS = 30
RECOMMENDED_MINUTES_BETWEEN_SUBMISSIONS = 120
CONTACT_MARKERS = ["[ADD YOUR EMAIL]", "[ADD YOUR PHONE]"]

# Part 5
RESPONSE_WAIT_DAYS = 14
MIN_ELIGIBLE_FOR_RATES = 10
RED_FLAG_RESPONSE_RATE = 0.10
TRIGGER_RESPONSE_RATE = 0.15
TARGET_RESPONSE_RATE_RANGE = (0.15, 0.25)
NO_INTERVIEW_AFTER_N = 20
TARGET_INTERVIEWS_PER_10_QUALITY = 1
QUALITY_APPLICATION_MIN_SCORE = 7
TARGET_HOURS_SAVED_PER_WEEK = 10
TRIGGER_MONTHLY_COST_USD = 25
TRIGGER_HOURS_SPENT_PER_WEEK = 8
TRIGGER_QUALITY_SCORE = 7
HIGH_COST_PER_APPLICATION_USD = 1.0
MIN_N_FOR_VARIANT_COMPARISON = 5
NOT_A_FIT_PHRASES = ["not a good fit", "not a fit", "overqualified", "underqualified"]
NOT_A_FIT_REPEAT_COUNT = 3
WEEKLY_GOAL_APPLICATIONS = 5
APPLICATION_SLOTS = {"Tuesday": 2, "Wednesday": 2, "Thursday": 1}
PREFERRED_SUBMISSION_DAYS = ("Tuesday", "Wednesday", "Thursday")
PREFERRED_SUBMISSION_HOURS = (10, 14)
AVOID_WINDOWS = [("Monday", 0, 12), ("Friday", 12, 24)]
CADENCE_DAYS = {"weekly": 7, "monthly": 30, "quarterly": 90}
FORMAL_THRESHOLD_BY_INDUSTRY = {"default": FORMAL_THRESHOLD, "finance": FORMAL_THRESHOLD + 2}
