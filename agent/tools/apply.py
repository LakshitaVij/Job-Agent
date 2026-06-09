import json
import os
import re
from datetime import date
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from agent.tools.ats import detect_ats, fill_with_playwright, _react_select_pick
from agent.tools.evaluate import _evaluate

PROFILE_PATH = os.path.join(os.path.dirname(__file__), "..", "profile.json")

# Shared browser session — persists across tool calls within a single agent run
_session = {"pw": None, "browser": None, "page": None, "ats": None}


def _profile() -> dict:
    with open(PROFILE_PATH) as f:
        return json.load(f)


def _close_session():
    try:
        if _session["browser"]:
            _session["browser"].close()
        if _session["pw"]:
            _session["pw"].stop()
    except Exception:
        pass
    _session.update({"pw": None, "browser": None, "page": None, "ats": None})


# ─── Portal login / navigation ───────────────────────────────────────────────

def login_to_portal(portal_url, portal_type=None):
    _close_session()

    ats = detect_ats(portal_url)
    if ats is None:
        return {
            "status": "error",
            "message": f"Unsupported portal — could not detect Greenhouse or Lever at {portal_url}",
        }

    # Lever listing pages need /apply to reach the form; Greenhouse is direct
    navigate_url = portal_url
    if ats == "lever" and not portal_url.rstrip("/").endswith("/apply"):
        navigate_url = portal_url.rstrip("/") + "/apply"

    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=False, slow_mo=80)
    page = browser.new_page()

    if ats == "lever":
        # Lever has persistent background requests — networkidle never resolves
        page.goto(navigate_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
    else:
        page.goto(navigate_url, wait_until="networkidle", timeout=30000)

    _session.update({"pw": pw, "browser": browser, "page": page, "ats": ats})
    return {"status": "ready", "ats": ats, "url": navigate_url}


# ─── Field filling ───────────────────────────────────────────────────────────

def fill_basic_fields(resume, portal_type=None):
    page, ats = _session["page"], _session["ats"]
    if page is None:
        return {"status": "error", "message": "No active browser session — call login_to_portal first."}

    profile = _profile()
    result = fill_with_playwright(page, ats, profile)
    return {"status": "filled", **result}


def attach_portfolio(role, available_links=None):
    """
    LinkedIn, GitHub, and website are already filled by fill_basic_fields via
    the ATS field map. This handles any extra links passed explicitly (e.g.
    a project-specific URL the agent decides to attach for a particular role).
    """
    page = _session["page"]
    if page is None or not available_links:
        return {"status": "skipped", "message": "No active session or no links provided."}

    filled, skipped = [], []
    label_hints = {"github": "GitHub", "linkedin": "LinkedIn", "lever": "Portfolio"}

    for link in available_links:
        label = next((v for k, v in label_hints.items() if k in link.lower()), "Portfolio")
        try:
            el = page.get_by_label(label, exact=False).first
            if el.count() > 0:
                el.fill(link)
                filled.append({"label": label, "value": link})
            else:
                skipped.append(link)
        except Exception:
            skipped.append(link)

    return {"status": "done", "filled": filled, "skipped": skipped}


def fill_skill_checkboxes(page=None):
    """
    Finds all checkbox inputs on the page and checks those whose labels
    match skills in profile.json. Skips meta-options (Some/None/All of the above).
    """
    if page is None:
        page = _session["page"]
    if page is None:
        return {"status": "error", "message": "No active browser session."}

    profile = _profile()
    skills_obj = profile.get("skills", {})
    raw_skills = []
    if isinstance(skills_obj, dict):
        for v in skills_obj.values():
            raw_skills.extend(v)
    else:
        raw_skills = skills_obj

    skill_set = {s.lower().strip() for s in raw_skills}
    ALIASES = {
        "js": "javascript", "ts": "typescript",
        "node": "node.js", "postgres": "postgresql",
        "postgresql": "sql", "pg": "sql",
        "k8s": "kubernetes", "react native": "react",
    }
    SKIP = re.compile(r"some of|none of|all of|prefer not|not applicable|n/a", re.IGNORECASE)

    checked, skipped = [], []
    for cb in page.locator("input[type='checkbox']").all():
        try:
            cb_id = cb.get_attribute("id") or ""
            label_el = page.locator(f"label[for='{cb_id}']") if cb_id else None
            label = label_el.first.inner_text().strip() if (label_el and label_el.count() > 0) else ""
            if not label or SKIP.search(label):
                continue
            norm = label.lower().strip()
            resolved = ALIASES.get(norm, norm)
            if resolved in skill_set or norm in skill_set:
                if not cb.is_checked():
                    cb.click()
                checked.append(label)
            else:
                skipped.append(label)
        except Exception:
            continue

    return {"status": "done", "checked": checked, "skipped": skipped}


def fill_company_questions(page=None):
    """
    Scans every label on the page and applies general rules for questions
    that can't be pre-mapped (company name changes per application):
      - Previously employed at this company → No
      - Spouse / household / family at this company → No
      - Under 18 → No
    Relocate is handled by the standard field map (willing_to_relocate in profile).
    """
    if page is None:
        page = _session["page"]
    if page is None:
        return {"status": "error", "message": "No active browser session."}

    RULES = [
        # Currently / previously / formerly worked at or contracted with this company
        (re.compile(r"(current(ly)?|previous(ly)?|former(ly)?)\s+(an?\s+)?(employ|work|contractor)", re.IGNORECASE), "No"),
        # Customer of this company (past or present)
        (re.compile(r"customer\s+of|was.*customer|past.*customer", re.IGNORECASE), "No"),
        # Spouse / household / family member at this company
        (re.compile(r"spouse|domestic\s+partner|household|family\s+member|parent\s+or\s+child", re.IGNORECASE), "No"),
        # Under 18
        (re.compile(r"under\s*18|less\s+than\s+18", re.IGNORECASE), "No"),
    ]

    filled, skipped = [], []

    for label in page.locator("label").all():
        try:
            label_text = label.inner_text().strip()
            if len(label_text) < 5:
                continue

            answer = next((val for pat, val in RULES if pat.search(label_text)), None)
            if not answer:
                continue

            input_id = label.get_attribute("for")
            if not input_id:
                skipped.append(label_text[:70])
                continue

            el = page.locator(f"#{input_id}").first
            if el.count() == 0:
                skipped.append(label_text[:70])
                continue

            if not _react_select_pick(page, el, answer):
                el.fill(answer)
            filled.append({"question": label_text[:70], "answer": answer})
        except Exception:
            continue

    return {"status": "done", "filled": filled, "skipped": skipped}


def fill_demographic_fields(demographic_preferences=None):
    page = _session["page"]
    if page is None:
        return {"status": "error", "message": "No active browser session."}

    demo = _profile().get("demographics", {})
    if not demo:
        return {"status": "skipped", "message": "No demographics key in profile.json."}

    # (label_hint, profile sub-key) — label hints match partial label text on the form
    fields = [
        ("gender",        "gender"),
        ("racial",        "race_ethnicity"),
        ("sexual",        "sexual_orientation"),
        ("transgender",   "transgender"),
        ("disability",    "disability"),
        ("veteran",       "veteran"),
    ]

    filled, skipped, errors = [], [], []

    for label_hint, key in fields:
        value = demo.get(key)
        if not value:
            skipped.append(key)
            continue

        try:
            el = page.get_by_label(label_hint, exact=False).first
            if el.count() == 0:
                skipped.append(key)
                continue
            if not _react_select_pick(page, el, value):
                el.fill(value)
            filled.append({"field": key, "value": value})
        except Exception as e:
            errors.append({"field": key, "error": str(e)})

    return {"status": "done", "filled": filled, "skipped": skipped, "errors": errors}


def fill_lever_eeo():
    """Fill Lever EEO section: gender/veteran/disability selects, race radio, disability signature."""
    page = _session["page"]
    if page is None:
        return {"status": "error", "message": "No active browser session."}

    demo = _profile().get("demographics", {})
    profile = _profile()
    filled, skipped, errors = [], [], []

    GENDER_MAP = {
        "woman": "Female", "female": "Female",
        "man": "Male", "male": "Male",
    }
    RACE_MAP = {
        "south asian": "Asian (Not Hispanic or Latino)",
        "east asian": "Asian (Not Hispanic or Latino)",
        "asian": "Asian (Not Hispanic or Latino)",
        "hispanic": "Hispanic or Latino",
        "latino": "Hispanic or Latino",
        "black": "Black or African American (Not Hispanic or Latino)",
        "african american": "Black or African American (Not Hispanic or Latino)",
        "white": "White (Not Hispanic or Latino)",
        "two or more": "Two or More Races (Not Hispanic or Latino)",
        "multiracial": "Two or More Races (Not Hispanic or Latino)",
        "native hawaiian": "Native Hawaiian or Other Pacific Islander (Not Hispanic or Latino)",
        "pacific islander": "Native Hawaiian or Other Pacific Islander (Not Hispanic or Latino)",
        "american indian": "American Indian or Alaska Native (Not Hispanic or Latino)",
        "alaska native": "American Indian or Alaska Native (Not Hispanic or Latino)",
    }
    VETERAN_MAP = {
        "no": "I am not a Protected Veteran",
        "yes": "I am a Protected Veteran",
    }
    DISABILITY_MAP = {
        "no": "No, I do not have a disability and have not had one in the past",
        "yes": "Yes, I have a disability, or have had one in the past",
    }

    def _select(sel_name, raw, mapping):
        val = next((v for k, v in mapping.items() if k in raw.lower()), None)
        sel = page.locator(f"select[name='{sel_name}']")
        if sel.count() == 0:
            skipped.append(sel_name)
            return
        if not val:
            skipped.append(sel_name)
            return
        try:
            sel.select_option(val)
            filled.append({"field": sel_name, "value": val})
        except Exception as e:
            errors.append({"field": sel_name, "error": str(e)})

    _select("eeo[gender]",    demo.get("gender", ""),    GENDER_MAP)
    _select("eeo[veteran]",   demo.get("veteran", ""),   VETERAN_MAP)
    _select("eeo[disability]",demo.get("disability", ""),DISABILITY_MAP)

    race_raw = demo.get("race_ethnicity", "").lower()
    race_val = next((v for k, v in RACE_MAP.items() if k in race_raw), None)
    if race_val:
        radio = page.locator(f"input[name='eeo[race]'][value='{race_val}']")
        if radio.count() > 0:
            try:
                radio.first.click()
                filled.append({"field": "eeo[race]", "value": race_val})
            except Exception as e:
                errors.append({"field": "eeo[race]", "error": str(e)})
        else:
            skipped.append("eeo[race]")
    else:
        skipped.append("eeo[race]")

    # Disability signature: required by law regardless of answer
    sig = page.locator("input[name='eeo[disabilitySignature]']")
    if sig.count() > 0:
        try:
            sig.fill(profile.get("name", ""))
            filled.append({"field": "eeo[disabilitySignature]", "value": profile.get("name", "")})
        except Exception as e:
            errors.append({"field": "eeo[disabilitySignature]", "error": str(e)})

    sig_date = page.locator("input[name='eeo[disabilitySignatureDate]']")
    if sig_date.count() > 0:
        today = date.today().strftime("%m/%d/%Y")
        try:
            sig_date.fill(today)
            filled.append({"field": "eeo[disabilitySignatureDate]", "value": today})
        except Exception as e:
            errors.append({"field": "eeo[disabilitySignatureDate]", "error": str(e)})

    return {"status": "done", "filled": filled, "skipped": skipped, "errors": errors}


def fill_lever_cards():
    """
    Parse Lever's hidden baseTemplate JSON to find each custom question's text and type,
    then fill radio/text/textarea/multiple-select inputs by index.
    """
    page = _session["page"]
    if page is None:
        return {"status": "error", "message": "No active browser session."}

    profile = _profile()
    yoe = profile.get("years_of_experience", {})
    filled, skipped, errors = [], [], []

    # multiple-choice rules: pattern → exact or partial radio value
    MC_RULES = [
        (re.compile(r"hereby affirm|information.*true|complete.*to.*best", re.IGNORECASE), "Yes"),
        (re.compile(r"background.*check|credit.*history|contingent.*completion|contingent.*successful", re.IGNORECASE), "acknowledge and agree"),
        (re.compile(r"commitment|non.?compete|restrict.*employment|agreements.*employer", re.IGNORECASE), "No"),
        (re.compile(r"applied.*within.*past|have you applied.*recently|previously applied.*role|past six months", re.IGNORECASE), "No"),
        (re.compile(r"previously worked at|former.*employ", re.IGNORECASE), "No"),
        (re.compile(r"(current(ly)?|previous(ly)?|former(ly)?)\s+(an?\s+)?(employ|work)", re.IGNORECASE), "No"),
        (re.compile(r"security clearance", re.IGNORECASE), "No"),
        (re.compile(r"legally eligible to work in canada", re.IGNORECASE), "No"),
    ]

    # multiple-choice rules backed by profile values (dotted key path)
    MC_PROFILE_RULES = [
        (re.compile(r"how many years.*production experience|years.*experience.*total", re.IGNORECASE), "years_of_experience.total"),
        (re.compile(r"how many years.*react", re.IGNORECASE), "years_of_experience.react"),
        (re.compile(r"how many years.*node", re.IGNORECASE), "years_of_experience.nodejs"),
        (re.compile(r"front.?end.*back.?end|backend.*frontend|stronger.*expertise|lean.*frontend|full.?stack.*prefer", re.IGNORECASE), "fullstack_preference"),
    ]

    # text/textarea rules: pattern → value
    TEXT_RULES = [
        (re.compile(r"start date|available.*start|when.*start", re.IGNORECASE), profile.get("availability", "")),
        (re.compile(r"salary|compensation|pay expectation|total comp", re.IGNORECASE), profile.get("salary_expectation", "")),
        (re.compile(r"referred.*employee|referral.*employee|current.*employee.*refer", re.IGNORECASE), "No"),
    ]

    def _resolve_dotted(key: str):
        val = profile
        for k in key.split("."):
            val = val.get(k) if isinstance(val, dict) else None
        return str(val) if val else None

    def _click_radio(f_name: str, answer: str) -> bool:
        # Try exact match first, then contains match for long option texts
        for sel in [
            f"input[name='{f_name}'][value='{answer}']",
            f"input[name='{f_name}'][value*='{answer}']",
        ]:
            r = page.locator(sel)
            if r.count() > 0:
                r.first.click()
                page.wait_for_timeout(200)
                return True
        return False

    def _normalize_skill(s: str) -> str:
        return re.sub(r'[\.\s]', '', s.lower()).replace('js', '')

    templates = page.locator("input[name*='baseTemplate']").all()
    if not templates:
        return {"status": "skipped", "message": "No Lever card templates found on this form."}

    for tmpl in templates:
        try:
            raw = tmpl.get_attribute("value") or ""
            if not raw:
                continue
            card_data = json.loads(raw)
            card_id = card_data.get("id", "")
            fields = card_data.get("fields", [])

            for idx, field in enumerate(fields):
                q_text = field.get("text", "")
                f_type = field.get("type", "text")
                f_name = f"cards[{card_id}][field{idx}]"

                if f_type == "multiple-choice":
                    answer = next((val for pat, val in MC_RULES if pat.search(q_text)), None)
                    if answer is None:
                        for pat, prof_key in MC_PROFILE_RULES:
                            if pat.search(q_text):
                                answer = _resolve_dotted(prof_key)
                                break
                    if answer:
                        if _click_radio(f_name, answer):
                            filled.append({"question": q_text[:70], "answer": answer})
                        else:
                            skipped.append(f"{q_text[:60]} (radio '{answer}' not found)")
                    else:
                        skipped.append(f"{q_text[:60]} (no rule)")

                elif f_type == "multiple-select":
                    # Collect all profile skills, normalised
                    all_skills = []
                    skills_obj = profile.get("skills", {})
                    for v in (skills_obj.values() if isinstance(skills_obj, dict) else [skills_obj]):
                        all_skills.extend(v)
                    skill_norms = {_normalize_skill(s) for s in all_skills}
                    for opt in field.get("options", []):
                        opt_text = opt.get("text", "")
                        opt_norm = _normalize_skill(opt_text)
                        if opt_norm in skill_norms or any(opt_norm in n or n in opt_norm for n in skill_norms):
                            cb = page.locator(f"input[name='{f_name}'][value='{opt_text}']")
                            if cb.count() > 0:
                                cb.first.click()
                                page.wait_for_timeout(150)
                                filled.append({"question": q_text[:60], "answer": f"checked:{opt_text}"})

                elif f_type in ("text", "textarea"):
                    value = next((val for pat, val in TEXT_RULES if pat.search(q_text) and val), None)
                    if value:
                        el = page.locator(f"[name='{f_name}']").first
                        if el.count() > 0:
                            el.fill(str(value))
                            filled.append({"question": q_text[:70], "answer": str(value)})
                        else:
                            skipped.append(f"{q_text[:60]} (input not found)")
                    else:
                        skipped.append(f"{q_text[:60]} (no profile value)")

        except Exception as e:
            errors.append({"error": str(e)})

    return {"status": "done", "filled": filled, "skipped": skipped, "errors": errors}


def fill_salary_expectation(negotiation_position=None, salary_data=None):
    page = _session["page"]
    if page is None:
        return {"status": "error", "message": "No active browser session."}

    # Prefer the agent's negotiation output; fall back to profile
    value = None
    if isinstance(negotiation_position, dict):
        value = negotiation_position.get("suggested_range")
    if not value:
        value = _profile().get("salary_expectation")
    if not value:
        return {"status": "skipped", "message": "No salary value in negotiation_position or profile.json."}

    try:
        el = page.get_by_label("salary", exact=False).first
        if el.count() == 0:
            return {"status": "skipped", "message": "Salary field not found on this form."}
        el.fill(str(value))
        return {"status": "filled", "value": value}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def fill_availability(start_date, availability_notes=None):
    page = _session["page"]
    if page is None:
        return {"status": "error", "message": "No active browser session."}

    for label_hint in ["start date", "available", "earliest"]:
        try:
            el = page.get_by_label(label_hint, exact=False).first
            if el.count() > 0:
                el.fill(start_date)
                return {"status": "filled", "field": label_hint, "value": start_date}
        except Exception:
            continue

    return {"status": "skipped", "message": "No start date / availability field found on this form."}


# ─── Submit ──────────────────────────────────────────────────────────────────

def submit_application(portal_type, application_data):
    page = _session["page"]
    if page is None:
        return {"status": "error", "message": "No active browser session."}

    submit = None
    for candidate in [
        page.get_by_role("button", name="Submit", exact=False),
        page.locator("input[type='submit']"),
        page.locator("button[type='submit']"),
    ]:
        if candidate.count() > 0:
            submit = candidate.first
            break

    if submit is None:
        return {"status": "error", "message": "Submit button not found on page."}

    submit.click()
    page.wait_for_load_state("load", timeout=30000)

    html = page.content()
    _close_session()

    return {"status": "submitted", "confirmation_html": html}


# ─── Confirmation parsing ────────────────────────────────────────────────────

def parse_confirmation(confirmation_page):
    soup = BeautifulSoup(confirmation_page, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    match = re.search(
        r'(?:confirmation|application|reference|tracking)[^\w]*(?:number|#|id|no\.?)[^\w]*([A-Z0-9][A-Z0-9\-]{3,})',
        text, re.IGNORECASE
    )
    if not match:
        match = re.search(r'#([A-Z0-9\-]{5,})', text)
    confirmation = match.group(1) if match else None

    next_steps = []
    keywords = ("next step", "what happen", "expect", "will contact", "will reach", "within", "review your")
    for tag in soup.find_all(["li", "p"]):
        tag_text = tag.get_text(strip=True)
        if tag_text and any(kw in tag_text.lower() for kw in keywords):
            next_steps.append(tag_text)

    return {
        "status": "parsed",
        "confirmation": confirmation or "not found",
        "next_steps": next_steps,
    }


# ─── LLM-powered tools ───────────────────────────────────────────────────────

def generate_cover_letter(job_description, relevant_experiences, build_opportunities=None, company_name=None):
    prompt = f"""You are an expert cover letter writer. Write a compelling, personalized cover letter for this job application.

Company: {company_name or "the company"}
Job Description: {job_description}
Candidate's Relevant Experiences: {relevant_experiences}
Build Opportunities / Why This Role: {build_opportunities or "Not specified"}

Write a 3-4 paragraph cover letter that:
- Opens with a strong hook specific to {company_name or "the company"} and the role
- Connects the candidate's most relevant experiences to the specific job requirements
- Explains genuine motivation for this role (use build opportunities if provided)
- Closes with a confident call to action

Return only the cover letter text, no subject line or metadata."""
    return _evaluate(prompt)


def answer_short_questions(questions, resume, company_context=None):
    prompt = f"""You are an expert job applicant helping answer short application questions authentically and concisely.

Questions: {questions}
Candidate Background (Resume): {resume}
Company Context: {company_context or "Not provided"}

For each question, write a concise, specific answer (1-3 sentences unless the question clearly requires more) that:
- Draws directly from the candidate's actual background
- Is tailored to the company and role context when provided
- Sounds natural, not generic or templated

Return a JSON with:
- answers: list of objects, each with "question" and "answer" fields, in the same order as the input questions"""
    return _evaluate(prompt)
