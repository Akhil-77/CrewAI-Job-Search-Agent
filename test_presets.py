import os; os.environ.setdefault("OPENAI_API_KEY","dummy"); os.environ.setdefault("SERPER_API_KEY","dummy")
from crews.application_crew import build_crew
from presets.variants import VARIANTS, build_guidance
from presets.industry import INDUSTRY_GUIDANCE
from presets.level import LEVEL_GUIDANCE

def names(crew): return [getattr(t,"task_name","") for t in crew.tasks]
def test_order_baseline():
    c=build_crew(); assert names(c)==["customize_resume_task","write_cover_letter_task","review_application_task"], names(c); print("baseline order OK")
def test_order_full():
    c=build_crew(variant="deep_culture_research", level="technical", with_review=True)
    assert names(c)==["translate_projects_task","deep_research_task","customize_resume_task","write_cover_letter_task","review_task","review_application_task"], names(c)
    # context links: cover letter context includes resume task
    tm=c.task_map; assert tm["customize_resume_task"] in tm["write_cover_letter_task"].context
    print("full order OK")
def test_personalizer():
    c=build_crew(variant="personalizer"); assert "personalize_task" in names(c); assert names(c)[-1]=="review_application_task"; print("personalizer OK")
def test_guidance_verbatim():
    for v in INDUSTRY_GUIDANCE.values(): assert v
    assert "Focus on regulatory knowledge" in INDUSTRY_GUIDANCE["finance"]
    assert "Emphasize learning potential" in LEVEL_GUIDANCE["entry"]
    g=build_guidance("finance","entry",{"highlight":["Python"],"tone":"formal","examples":["ex1"]},["lib text"])
    assert "Python" in g["cover_letter_guidance"] and "lib text" in g["cover_letter_guidance"]; print("guidance OK")
def test_variants_one_change():
    for name,v in VARIANTS.items():
        if name=="baseline": continue
        assert v["changed_element"] in ("agent","prompt","tool","model"), v
    print("variants OK")
def test_lite():
    from crews.company_research_crew import build_crew as bc; c=bc(lite=True); assert len(c.tasks)==2, [t.task_name for t in c.tasks]
    from crews.interview_prep_crew import build_crew as bi; c2=bi(lite=True); assert len(c2.tasks)==2 and len(c2.agents)==2
    print("lite OK")
def test_no_submit():
    for build in [lambda: build_crew()]:
        crew=build()
        for a in crew.agents:
            for t in (a.tools or []):
                n=str(getattr(t,"name",t)).lower(); assert "submit" not in n and "auto_apply" not in n
    print("no submit OK")
if __name__=="__main__":
    test_order_baseline(); test_order_full(); test_personalizer(); test_guidance_verbatim(); test_variants_one_change(); test_lite(); test_no_submit(); print("test_presets: all passed")
