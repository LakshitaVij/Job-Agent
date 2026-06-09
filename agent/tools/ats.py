import re
import json
import os

# ─── Detection ───────────────────────────────────────────────────────────────

_ATS_PATTERNS = {
    "greenhouse": [r"boards\.greenhouse\.io", r"job-boards\.greenhouse\.io", r"greenhouse\.io"],
    "lever":      [r"jobs\.lever\.co", r"lever\.co"],
}

def detect_ats(portal_url: str) -> str | None:
    for ats, patterns in _ATS_PATTERNS.items():
        if any(re.search(p, portal_url, re.IGNORECASE) for p in patterns):
            return ats
    return None


# ─── Field maps ──────────────────────────────────────────────────────────────
# selector:   stable CSS selector (used when the element has a predictable ID)
# label_text: partial label text for Playwright get_by_label() — used for
#             Greenhouse custom questions whose IDs change per job posting
# transform:  "first" / "last" split name, "bool" converts True→"Yes"/False→"No"
# required:   True = application cannot be submitted without this field

GREENHOUSE_FIELDS = [
    # ── Structural fields (stable IDs across all Greenhouse postings) ─────────
    {"field": "first_name",      "selector": "input#first_name",    "type": "text",  "profile_key": "name",                "required": True,  "transform": "first"},
    {"field": "last_name",       "selector": "input#last_name",     "type": "text",  "profile_key": "name",                "required": True,  "transform": "last"},
    {"field": "email",           "selector": "input#email",         "type": "text",  "profile_key": "email",               "required": True},
    {"field": "phone",           "selector": "input#phone",         "type": "text",  "profile_key": "phone",               "required": True},
    {"field": "resume",          "selector": "input#resume",        "type": "file",  "profile_key": "resume_path",         "required": True},
    {"field": "cover_letter",    "selector": "input#cover_letter",  "type": "file",  "profile_key": None,                  "required": False, "note": "generated at runtime"},
    {"field": "country",         "selector": "input#country",       "type": "text",  "profile_key": "country",             "required": False},

    # ── Custom questions (label-matched — IDs are job-specific) ──────────────
    {"field": "linkedin",        "selector": None, "label_text": "LinkedIn",                          "type": "text",   "profile_key": "linkedin",            "required": False},
    {"field": "github",          "selector": None, "label_text": "GitHub",                            "type": "text",   "profile_key": "github",              "required": False},
    {"field": "website",         "selector": None, "label_text": "Website",                           "type": "text",   "profile_key": "website",             "required": False},
    {"field": "state",           "selector": None, "label_text": "state do you reside",               "type": "text",   "profile_key": "state",               "required": False},
    {"field": "pronouns",        "selector": None, "label_text": "pronouns",                          "type": "text",   "profile_key": "pronouns",            "required": False},
    {"field": "work_location",   "selector": None, "label_text": "work location",                     "type": "text",   "profile_key": "location",            "required": False},
    {"field": "timezone",        "selector": None, "label_text": "time zone",                         "type": "text",   "profile_key": "timezone",            "required": False},
    {"field": "work_authorized", "selector": None, "label_text": "authorized to work",                "type": "text",   "profile_key": "work_authorized",     "required": False, "transform": "bool"},
    {"field": "sponsorship",     "selector": None, "label_text": "sponsorship",                       "type": "text",   "profile_key": "requires_sponsorship","required": False, "transform": "bool"},
    {"field": "salary",          "selector": None, "label_text": "salary",                            "type": "text",   "profile_key": "salary_expectation",  "required": False},
    {"field": "compensation",    "selector": None, "label_text": "base compensation expectations",    "type": "text",   "profile_key": "salary_expectation",  "required": False},
    {"field": "willing_relocate","selector": None, "label_text": "willing to relocate",               "type": "text",   "profile_key": "willing_to_relocate", "required": False, "transform": "bool"},
    {"field": "referral_source", "selector": None, "label_text": "hear about",                        "type": "text",   "profile_key": "referral_source",     "required": False},
]

LEVER_FIELDS = [
    # ── Structural fields (stable names across all Lever postings) ────────────
    {"field": "full_name",       "selector": "input[name='name']",              "type": "text",     "profile_key": "name",                "required": True},
    {"field": "email",           "selector": "input[name='email']",             "type": "text",     "profile_key": "email",               "required": True},
    {"field": "phone",           "selector": "input[name='phone']",             "type": "text",     "profile_key": "phone",               "required": True},
    {"field": "resume",          "selector": "input[name='resume']",            "type": "file",     "profile_key": "resume_path",         "required": True},
    {"field": "cover_letter",    "selector": "textarea[name='comments']",       "type": "textarea", "profile_key": None,                  "required": False, "note": "generated at runtime"},
    {"field": "linkedin",        "selector": "input[name='urls[LinkedIn]']",    "type": "text",     "profile_key": "linkedin",            "required": False},
    {"field": "github",          "selector": "input[name='urls[GitHub]']",      "type": "text",     "profile_key": "github",              "required": False},
    {"field": "portfolio",       "selector": "input[name='urls[Portfolio]']",   "type": "text",     "profile_key": "website",             "required": False},
    {"field": "location",        "selector": "input[name='location']",          "type": "text",     "profile_key": "location",            "required": False},
    {"field": "work_authorized", "selector": None, "label_text": "authorized to work",              "type": "text",   "profile_key": "work_authorized",     "required": False, "transform": "bool"},
    {"field": "sponsorship",     "selector": None, "label_text": "require sponsorship",             "type": "text",   "profile_key": "requires_sponsorship","required": False, "transform": "bool"},
]

_FIELD_MAP = {"greenhouse": GREENHOUSE_FIELDS, "lever": LEVER_FIELDS}


# ─── Profile resolution ───────────────────────────────────────────────────────

def _resolve(profile: dict, key: str, transform: str | None = None) -> str | None:
    value = profile.get(key)
    if value is None:
        return None
    if transform == "first":
        return str(value).split()[0]
    if transform == "last":
        parts = str(value).split()
        return parts[-1] if parts else None
    if transform == "bool":
        return "Yes" if value else "No"
    return str(value)


# ─── Dry-run ─────────────────────────────────────────────────────────────────

def dry_run_fill(portal_url: str, profile: dict) -> dict:
    """
    Resolves all ATS fields against profile.json without opening a browser.
    Returns a report of what can be filled, what's missing, and what's runtime.
    """
    ats = detect_ats(portal_url)
    if ats is None:
        return {
            "status": "error",
            "message": "Could not detect ATS. Supported: greenhouse, lever.",
            "url": portal_url,
        }

    filled, missing_required, missing_optional, skipped = [], [], [], []

    for f in _FIELD_MAP[ats]:
        key = f["profile_key"]
        if key is None:
            skipped.append({"field": f["field"], "note": f.get("note", "runtime-generated")})
            continue

        value = _resolve(profile, key, f.get("transform"))
        locator = f.get("selector") or f"label~'{f.get('label_text')}'"
        entry = {"field": f["field"], "profile_key": key, "locator": locator}

        if value:
            filled.append({**entry, "value": value})
        elif f["required"]:
            missing_required.append(entry)
        else:
            missing_optional.append(entry)

    return {
        "status": "dry_run",
        "ats": ats,
        "filled": filled,
        "missing_required": missing_required,
        "missing_optional": missing_optional,
        "skipped_runtime": skipped,
    }


# ─── React Select helper ─────────────────────────────────────────────────────

def _react_select_pick(page, el, value: str) -> bool:
    """
    Click a React Select combobox and select the first option whose text
    contains `value` (case-insensitive). Returns True on success.
    """
    el.click()
    page.wait_for_timeout(500)
    opts = page.locator(".select__option").filter(
        has_text=re.compile(re.escape(value), re.IGNORECASE)
    )
    if opts.count() > 0:
        opts.first.click()
        return True
    page.keyboard.press("Escape")
    page.wait_for_timeout(200)
    return False


def _set_phone_country(page, country_code: str = "us") -> None:
    """Set the intl-tel-input country flag to the given ISO country code."""
    btn = page.locator(".iti__selected-country").first
    if btn.count() == 0:
        return
    btn.click()
    page.wait_for_timeout(400)
    page.locator(f"li[data-country-code='{country_code}']").first.click()
    page.wait_for_timeout(200)


# ─── Playwright fill ─────────────────────────────────────────────────────────

def fill_with_playwright(page, ats: str, profile: dict) -> dict:
    """
    Fills an open Playwright page (sync API) with profile data for the detected ATS.
    - File inputs: set_input_files()
    - Phone: fill() then set country code via iti picker
    - Everything else: try React Select click+pick first, fall back to plain fill()
    """
    results = {"filled": [], "skipped": [], "errors": []}

    for f in _FIELD_MAP[ats]:
        key = f["profile_key"]
        if key is None:
            results["skipped"].append(f["field"])
            continue

        value = _resolve(profile, key, f.get("transform"))
        if not value:
            results["skipped"].append(f["field"])
            continue

        # Locate: CSS selector first, label text fallback
        el = None
        used_locator = None
        if f.get("selector"):
            candidate = page.locator(f["selector"]).first
            if candidate.count() > 0:
                el = candidate
                used_locator = f["selector"]

        if el is None and f.get("label_text"):
            candidate = page.get_by_label(f["label_text"], exact=False).first
            if candidate.count() > 0:
                el = candidate
                used_locator = f"label~'{f['label_text']}'"

        if el is None:
            results["skipped"].append(f["field"])
            continue

        try:
            if f["type"] == "file":
                el.set_input_files(value)
            elif f["field"] == "phone":
                el.fill(value)
                _set_phone_country(page, country_code="us")
            else:
                # Try React Select first; fall back to plain fill for text inputs
                if not _react_select_pick(page, el, value):
                    el.fill(value)
            results["filled"].append({"field": f["field"], "locator": used_locator})
        except Exception as e:
            results["errors"].append({"field": f["field"], "locator": used_locator, "error": str(e)})

    return results


# ─── CLI dry-run ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    profile_path = os.path.join(os.path.dirname(__file__), "..", "profile.json")
    with open(profile_path) as fh:
        profile = json.load(fh)

    url = sys.argv[1] if len(sys.argv) > 1 else "https://boards.greenhouse.io/example/jobs/123"
    report = dry_run_fill(url, profile)

    print(f"\nATS detected: {report.get('ats', 'none').upper()}")
    print(f"URL: {url}\n")

    print(f"✅  FILLED ({len(report.get('filled', []))}):")
    for f in report.get("filled", []):
        print(f"    {f['field']:<22} = {f['value']}")

    print(f"\n❌  MISSING — REQUIRED ({len(report.get('missing_required', []))}):")
    for f in report.get("missing_required", []):
        print(f"    {f['field']:<22}  (add '{f['profile_key']}' to profile.json)")

    print(f"\n⚠️   MISSING — OPTIONAL ({len(report.get('missing_optional', []))}):")
    for f in report.get("missing_optional", []):
        print(f"    {f['field']:<22}  (add '{f['profile_key']}' to profile.json)")

    print(f"\n⏭️   RUNTIME-GENERATED ({len(report.get('skipped_runtime', []))}):")
    for f in report.get("skipped_runtime", []):
        print(f"    {f['field']:<22}  ({f['note']})")
