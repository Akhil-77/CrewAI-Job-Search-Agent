# Job Search Crew — AI-Powered Job Search Assistant (CrewAI)

A crew of specialized AI agents that help recent Master's graduates research jobs, tailor applications, research companies, and prepare for interviews. AI prepares; the human reviews, personalizes, and submits. Nothing in this project submits applications automatically.

## Prerequisites
Python 3.10 or newer.

## Setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add OPENAI_API_KEY and SERPER_API_KEY
```
Get a Serper key at serper.dev (free tier available, usage limits apply — check serper.dev for current terms).

## Part 1 — Foundation
- `python test_setup.py` — verifies setup; success = 3 tips + "Test completed successfully!". With no key it prints a friendly setup message.
- `python job_research_agent.py` — single-agent market report for `FIELD` (edit the constant; examples: "digital marketing", "software engineering", "business analysis", "project management").

**Cost notes:** billed per token by OpenAI; roughly $2-5 total for this course, small projects roughly $5-15/month. Set a spending limit in your OpenAI account. See openai.com/pricing.
**Limitations:** agents rely on training-data knowledge (not real-time boards) plus search/scrape results; verify company details, requirements, deadlines independently. Agents are research assistants, not final authorities.

**Troubleshooting:** Module not found → activate venv, install in it, run from project dir. API key errors → check `.env` format (no quotes/spaces), same folder as scripts. Slow responses → normal (30-60s+). Rate limits → wait/retry, add delays. Permission errors → use venv or `pip install --user crewai`. Other install problems → `pip install --upgrade crewai`.

## Part 2 — Three-agent crew
Researcher (ScrapeWebsiteTool, SerperDevTool) → Writer (no tools) → Analyst (no tools; spreadsheet tools later), sequential.
```
python main.py [--role ... --location ... --num-jobs 5]
python test_single.py researcher|writer|analyst
```
Edit `user_profile.py` (`USER_PROFILE`) with your real info — the writer uses only this, and does not invent credentials.
Debugging: agent stuck → more specific tasks, right tools, split steps. Poor outputs → improve goal/backstory, add examples, specify format. Tasks don't connect → check formats, order, test individually. Start small, `verbose=True` while testing. Loop: small test → biggest problem → fix one thing → retest.
Planning questions: What tasks take you the most time? Which parts do you want to automate? How many applications per week? Start with three agents, add later.

## Part 3 — Four specialized crews
| Crew | Command | Agents/Tasks |
|---|---|---|
| Job Research & Matching | `run.py jobs` | 1 / 3 |
| Application Materials | `run.py apply` | 3 / 3 |
| Company Research | `run.py company` | 3 / 4 |
| Interview Prep | `run.py interview` | 4 / 5 |
```bash
python run.py jobs --dry-run
python run.py apply --job-title "ML Engineer" --company ExampleCo --posting posting.txt
python run.py company --company ExampleCo
python run.py interview --job-title "ML Engineer" --company ExampleCo
```
Outputs saved to `outputs/<command>_<timestamp>.md`. Tool mapping: course placeholder tools were mapped to Serper/Scrape or dropped (LLM does the work) or built custom (`keyword_analyzer`, `consistency_checker`) — see `tools/`. Web limits: LinkedIn/Indeed/Glassdoor often block scraping; crews rely on search results, label estimates, cite sources, and say when a platform couldn't be accessed. Cost warning: interview crew = 5 tasks; test with `--dry-run`, use a cheaper model via `config.py`. Edit `user_profile.py` (`MY_SKILLS`, `MY_PROFILE`), `templates.py`, `config.py`. Crews do not learn on their own — edit profile/weights/wording from feedback. Scheduling a daily/weekly run via cron/Task Scheduler is possible but not set up here.
Vague prompt: "Write a cover letter." Specific prompt: "Write a 3-paragraph cover letter. Highlight Python and SQL. Match their collaborative tone. Use these examples: ..."

## Part 4 — Quality, cost, ethics
Checkpoints: (1) after draft — red-flag report + HUMAN TODO + checklist offer; (2) before submission — `python manage.py pre-submit <file>` (scanners + 7-item checklist + Red Flag Check + guards, writes `.approved.json`, submits nothing); (3) weekly review (Part 5).
Every `apply` output starts with the HUMAN TODO block (5-10 min: 2-3 personal touches, style, verify claims, replace `[ADD YOUR EMAIL]`/`[ADD YOUR PHONE]`, fix flagged phrases).
Let AI handle: research, first drafts, structure, keyword matching. You handle: personal touches, verification, final wording, submitting.
80% draft example: AI produces a ~80% complete draft; you spend 5-10 minutes making it yours.
Cost: tiers in `config.py` (cheap=research/formatting, strong=writing), `data/cost_log.csv`, `manage.py cost report`, billing alerts $10/$15/$20 (set in OpenAI dashboard, check weekly), weekly budget $5, guard warns at 80% / stops at 100% unless `--force`, `--economy` = cheap everywhere. Prices are configured by you in `config.py` — verify on the pricing page.
Cache: `data/cache/` (14-day TTL), `manage.py cache list|clear`, `run.py company --refresh`. Library: `manage.py library add|list|show|delete`. Batch: `run.py company --batch companies.txt`, `run.py apply --batch jobs.csv` (pause 5s, warn >10). Suggested rhythm: batch research early week, generate/refine mid-week, review/submit late week, plan weekends (no API cost) — superseded in detail by Part 5 schedule.
Compliance: platform limits in `config.py` are course rule-of-thumb guidelines, not official limits — read each platform's current terms. No auto-submission. Records to keep: application log, saved postings (`data/postings/`), rate vs limits, platform warnings (in log notes). See `ETHICS.md`.
What not to put in prompts — Safe: degree/year, general project descriptions, public company info, posting requirements, career goals. Private: salary numbers/history, confidential projects, contact info, credentials, references' details, SSN, full address.
Agent tips: specific expertise, examples in backstories, clear boundaries, test with samples. Speed: shorter prompts, only needed context, one focused task per call.
New flags: `review --file`, `--with-review`, `--economy`, `--force`, `--no-prompt`, `--allow-sensitive`, `--refresh`, `--batch`, `--highlight/--tone/--examples/--use-structure/--use-achievements`.

## Part 5 — Metrics, variants, presets, complete workflow
See `WORKFLOW.md` for the full guide. Weekly cycle: Sunday `manage.py plan` → Mon networking → Tue-Thu `manage.py daily --target ID` → Fri `manage.py weekly-review`.
```bash
python manage.py log update 1 --response yes --interview pending --quality 8
python manage.py time add --hours-spent 6 --hours-saved 10
python manage.py metrics --period month --by industry
python manage.py dashboard
python run.py apply --variant personalizer --industry finance --level entry
python manage.py compare-variants
python manage.py targets add --company ExampleCo --role "ML Engineer" --platform indeed
```
Metrics (see `analytics/metrics.py` docstring): response/interview rates exclude very recent pending applications (14-day wait); cost per application from log estimates, falling back to the cost log (source labeled). Time-saved and quality scores are self-reported. Variants change exactly one element vs baseline; test one change with 5-10 applications, compare, keep or revert — with samples this small, differences are often noise. Reminder: nothing submits applications.

## Tests (offline, no API)
```bash
python test_tools.py; python test_quality.py; python test_core.py
python test_compliance.py; python test_analytics.py; python test_presets.py; python test_workflow.py
```
