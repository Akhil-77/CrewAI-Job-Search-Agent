"""Simple output checks (Part 2). Heuristics, not guarantees."""
def run_all_checks(result_text, tasks=None, expectations=None):
    text = str(result_text or "")
    checks = []
    # Completeness
    ok = bool(text.strip())
    checks.append(("Completeness", ok, "Output is non-empty" if ok else "Empty output - review the task/agent that produced it (researcher/writer/analyst)"))
    # Relevance
    keywords = (expectations or {}).get("keywords", ["data", "python"])
    found = [k for k in keywords if k.lower() in text.lower()]
    ok2 = bool(found)
    checks.append(("Relevance", ok2, f"Found keywords {found}" if ok2 else "No target keywords found - review researcher/writer task"))
    # Format
    has_fields = all(w in text.lower() for w in ["company"]) or "|" in text
    checks.append(("Format", has_fields, "Expected fields/table present" if has_fields else "Missing company field or markdown table - review format in task"))
    # Quality - human judgment
    print("Quality check: Would you be comfortable submitting these materials? Review manually: accuracy, tone, personalization.")
    checks.append(("Quality", True, "Human review required - see question above"))
    print("\nValidation report:")
    for name, passed, msg in checks:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}: {msg}")
    return checks
