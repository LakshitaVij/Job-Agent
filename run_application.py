"""
End-to-end application runner.
Usage:
  /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 run_application.py <job_url> [company_name] [role_title]

Example:
  python3 run_application.py https://job-boards.greenhouse.io/consumerreports/jobs/5143361007 "Consumer Reports" "Data Engineer"
"""

import json
import sys
import os
import tempfile
import urllib.request
import re

sys.path.insert(0, os.path.dirname(__file__))

from agent.tools.apply import (
    login_to_portal,
    fill_basic_fields,
    fill_skill_checkboxes,
    fill_demographic_fields,
    fill_company_questions,
    fill_availability,
    fill_lever_eeo,
    fill_lever_cards,
    generate_cover_letter,
    submit_application,
    parse_confirmation,
    _profile,
    _session,
)
from agent.tools.document import create_application_record


def step(n, label):
    print(f"\n{'─' * 60}")
    print(f"  Step {n} · {label}")
    print(f"{'─' * 60}")


def fetch_job_description(url: str) -> str:
    m = re.search(r'greenhouse\.io/([^/]+)/jobs/(\d+)', url)
    if m:
        company_slug, job_id = m.group(1), m.group(2)
        api = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs/{job_id}"
        try:
            with urllib.request.urlopen(api, timeout=10) as resp:
                data = json.loads(resp.read())
                content = data.get("content") or data.get("description") or ""
                from html import unescape
                from bs4 import BeautifulSoup
                return BeautifulSoup(unescape(content), "html.parser").get_text(separator=" ", strip=True)
        except Exception as e:
            print(f"  Warning: could not fetch JD from Greenhouse API ({e})")
    return f"Job posting at {url}"


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run_application.py <job_url> [company_name] [role_title]")
        sys.exit(1)

    job_url     = sys.argv[1]
    company     = sys.argv[2] if len(sys.argv) > 2 else input("  Company name: ").strip()
    role        = sys.argv[3] if len(sys.argv) > 3 else input("  Role title: ").strip()
    profile     = _profile()

    # ── 1. Fetch job description ─────────────────────────────────────────────
    step(1, "Fetching job description")
    jd = fetch_job_description(job_url)
    print(f"  {len(jd)} chars fetched")

    # ── 2. Open browser ──────────────────────────────────────────────────────
    step(2, "Opening browser · navigating to form")
    login_result = login_to_portal(job_url)
    if login_result["status"] == "error":
        print(f"  ERROR: {login_result['message']}")
        sys.exit(1)
    ats = login_result["ats"]
    print(f"  ATS detected: {ats.upper()}")

    # ── 3. Fill basic fields ─────────────────────────────────────────────────
    step(3, "Filling basic fields")
    result = fill_basic_fields(resume=profile)
    print(f"  Filled  : {[f['field'] for f in result.get('filled', [])]}")
    if result.get("skipped"):
        print(f"  Skipped : {result['skipped']}")
    if result.get("errors"):
        print(f"  Errors  : {result['errors']}")

    # ── 3.5. Check skill checkboxes ──────────────────────────────────────────
    step("3.5", "Checking skill boxes")
    result = fill_skill_checkboxes(page=_session["page"])
    print(f"  Checked : {result.get('checked', [])}")
    print(f"  Skipped : {result.get('skipped', [])}")

    if ats == "lever":
        # ── 4. Lever EEO section ─────────────────────────────────────────────
        step(4, "Filling Lever EEO fields")
        result = fill_lever_eeo()
        print(f"  Filled  : {[f['field'] for f in result.get('filled', [])]}")
        if result.get("skipped"):
            print(f"  Skipped : {result['skipped']}")
        if result.get("errors"):
            print(f"  Errors  : {result['errors']}")

        # ── 4.5. Lever custom card questions ─────────────────────────────────
        step("4.5", "Filling Lever card questions")
        result = fill_lever_cards()
        print(f"  Filled  : {[(f['question'][:50], f['answer']) for f in result.get('filled', [])]}")
        if result.get("skipped"):
            print(f"  Skipped : {result['skipped']}")
        if result.get("errors"):
            print(f"  Errors  : {result['errors']}")

    else:
        # ── 4. Greenhouse demographic fields ─────────────────────────────────
        step(4, "Filling demographic fields")
        result = fill_demographic_fields()
        print(f"  Filled  : {[f['field'] for f in result.get('filled', [])]}")
        if result.get("skipped"):
            print(f"  Skipped : {result['skipped']}")
        if result.get("errors"):
            print(f"  Errors  : {result['errors']}")

        # ── 4.5. Greenhouse company-specific questions ────────────────────────
        step("4.5", "Answering company-specific questions")
        result = fill_company_questions(page=_session["page"])
        print(f"  Filled  : {[(f['question'][:50], f['answer']) for f in result.get('filled', [])]}")
        if result.get("skipped"):
            print(f"  Skipped : {result['skipped']}")

        # ── 4.6. Greenhouse availability / start date ─────────────────────────
        step("4.6", "Filling availability")
        result = fill_availability(start_date=profile.get("availability", ""))
        print(f"  {result['status']}: {result.get('value') or result.get('message', '')}")

    # ── 5. Generate cover letter ─────────────────────────────────────────────
    step(5, "Generating cover letter")
    relevant_exp = "\n".join(
        f"- {e['role']} at {e['company']}: " + "; ".join(e["highlights"])
        for e in profile["experiences"]
    )
    cover_letter = generate_cover_letter(
        job_description=jd,
        relevant_experiences=relevant_exp,
        company_name=company,
    )
    cl_file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", prefix="cover_letter_", delete=False
    )
    cl_file.write(cover_letter)
    cl_file.close()
    print(f"  Saved to : {cl_file.name}")
    print(f"\n{cover_letter[:500]}\n  [...]\n")

    # Handle cover letter upload/insert based on ATS
    page = _session["page"]
    if ats == "lever":
        # Lever uses a textarea[name='comments'] — paste the text directly
        cl_textarea = page.locator("textarea[name='comments']")
        if cl_textarea.count() > 0:
            cl_textarea.fill(cover_letter)
            print("  Pasted into Lever cover letter textarea ✓")
        else:
            print("  No Lever cover letter textarea found — skipping")
    else:
        # Greenhouse uses input#cover_letter (file upload), only if required
        cl_input = page.locator("input#cover_letter")
        if cl_input.count() > 0:
            is_required = cl_input.get_attribute("required") is not None
            if not is_required:
                cl_label = page.locator("label[for='cover_letter']")
                if cl_label.count() > 0:
                    is_required = "*" in cl_label.inner_text()
            if is_required:
                cl_input.set_input_files(cl_file.name)
                print("  Uploaded to form (required) ✓")
            else:
                print("  Cover letter not required on this form — skipping")

    # ── Pause for manual review ──────────────────────────────────────────────
    print("=" * 60)
    print("  Browser is open. Review all fields and fix anything")
    print("  the agent missed. Upload cover letter manually if needed:")
    print(f"  {cl_file.name}")
    print("=" * 60)
    try:
        input("\n  Press Enter to SUBMIT, or Ctrl+C to abort.\n  > ")
    except KeyboardInterrupt:
        print("\n  Aborted — browser left open for manual inspection.")
        sys.exit(0)

    # ── 6. Submit ────────────────────────────────────────────────────────────
    step(6, "Submitting application")
    result = submit_application(portal_type=ats, application_data={})
    if result["status"] == "error":
        print(f"  ERROR: {result['message']}")
        sys.exit(1)

    confirmation = parse_confirmation(result["confirmation_html"])
    print(f"  Confirmation : {confirmation['confirmation']}")
    if confirmation["next_steps"]:
        print("  Next steps:")
        for s in confirmation["next_steps"]:
            print(f"    • {s}")

    # ── 7. Log to Notion ─────────────────────────────────────────────────────
    step(7, "Logging to Notion")
    notion_result = create_application_record(
        company_name=company,
        role=role,
        confirmation_data=confirmation,
    )
    page_id = notion_result.get("id", "unknown")
    page_url = notion_result.get("url", "")
    print(f"  Notion page : {page_url or page_id}")

    print("\n✅  Done.\n")


if __name__ == "__main__":
    main()
