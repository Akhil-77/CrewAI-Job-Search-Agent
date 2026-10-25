# Complete Workflow Guide

## 1. Complete workflow overview
Weekly planning (`manage.py plan`) -> daily execution (`manage.py daily --target ID`) -> quality control (`manage.py pre-submit`) -> tracking (`manage.py log add`) and follow-up -> continuous improvement (`manage.py dashboard`, `compare-variants`).

## 2. Weekly planning, daily routine, timing
Sunday planning (1 hour): target selection 20 min, company research batch 30 min (`run.py company --from-targets --lite`), week planning 10 min.
Daily routine (45 min/application): Phase 1 AI generation 15 min, Phase 2 human review 20 min, Phase 3 final preparation 10 min.
Timing strategy: submit Tue-Thu 10am-2pm, avoid Monday mornings and Friday afternoons, space at least 2 hours apart (recommended), vary timing within the window. These are course recommendations, not proven rules.

Weekly schedule:
```
Sunday:    Planning and company research (1 hour)
Monday:    Networking and LinkedIn engagement (30 minutes)
Tuesday:   2 applications with AI assistance (1.5 hours)
Wednesday: 2 applications with AI assistance (1.5 hours)
Thursday:  1 application + interview prep (1 hour)
Friday:    Follow-ups and weekly review (45 minutes)
Saturday:  Rest or optional skill development
```
Note: the Part 4 cost lesson's "Monday research / Friday submit" pattern is superseded by this schedule.

## 3. Quality control integration
5-minute check (`quality_check_5min.txt`, `manage.py checklist --five-minute`), weekly quality review (`manage.py weekly-review`), red-flag prevention: never submit without human review; verify company details; check examples match actual experience; ensure writing sounds like you.

## 4. Sustainable routine
Energy management: do creative work when fresh; use AI for routine tasks when energy is lower; batch similar activities; take breaks; set realistic goals (3-5 quality applications); focus on fit over volume; celebrate small wins; keep activities outside job searching. Avoid burnout with the tips in `manage.py plan`.

## 5. Measuring what matters
Five metrics: response rate, interview rate, time saved per week, cost per application, quality score. Definitions in `analytics/metrics.py` and README. Weekly review questions: which industries respond? do edited vs AI letters differ? what time works? which variants work? Time-saved and quality are self-reported.

## 6. Iterating
If response rates are low -> `--variant personalizer` / `deep_culture_research`, `--tone`, `--examples`. If applications feel generic -> personalizer. If costs too high -> `--economy`, cache, library. Configuration testing: one change at a time, 5-10 applications, compare to baseline, keep or revert. Small-sample caution: differences are often noise.

## 7. Adapting for industries and role levels
Presets: `--industry tech|finance|healthcare|consulting`, `--level entry|mid|technical|cross_functional`. See README examples.

## 8. Scaling
Template library approach: save successful agent configurations per industry (`agent_configs`), effective prompts (`prompts`), research templates (`research_templates`), standard workflows (`workflows`). Standard workflows: (1) new application, (2) batch week, (3) interview invitation (cached research then `run.py interview`), (4) low-response troubleshooting.
Automation boundaries: automate research and initial drafts; keep final review and submission manual; keep networking and follow-ups personal; use AI for preparation, not replacement of judgment. Continuous improvement cadence: weekly tactics, monthly patterns/configs, quarterly strategy.

## 9. Cost and performance
Monthly budget $15-20, daily usage tracking (`manage.py cost report`), cheap model for research / strong for writing, caching, dashboard, four optimization triggers (see `analytics/insights.py`).

## 10. Next steps and career growth (documentation only)
Short-term (3 months): master the workflow, build a network, develop interview skills, land the first role.
Medium-term (6-12 months): adapt for internal promotions, performance review prep, goal setting, thought leadership through AI-assisted content, mentor others.
Long-term (1-2 years): develop AI skills as a differentiator, systems for ongoing development, personal brand around AI/automation, consider entrepreneurial opportunities.
Continuous learning: stay updated on CrewAI/AI tools, join communities, experiment, share experiences.
Closing reminder: this system is a starting point; keep adapting while maintaining authenticity and ethical practice.
