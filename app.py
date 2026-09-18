"""Minimal web UI for the candidate sourcing pipeline (browser preview only -- main.py is the
real CLI entry point; this just wraps the same pipeline for visual demoing in a browser).

Run: .venv/bin/python app.py
"""
from __future__ import annotations

from pathlib import Path

from flask import Flask, render_template_string, request

from src.adapters.registry import all_names, get, register_linkedin_adapter
from src.intake.confirmation_flow import confirm_and_save, pending_block_a_fields
from src.matching.search import run_search
from src.nlp.jd_extractor import extract_draft_requirement_set
from src.shortlist.render import render_shortlist
from src.storage.audit_store import AuditStore
from src.storage.requirement_store import RequirementStore

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
requirement_store = RequirementStore(DATA_DIR / "requirements.jsonl")
audit_store = AuditStore(DATA_DIR / "audit.jsonl")

try:
    register_linkedin_adapter()
except Exception:
    pass  # no credentials configured yet -- "mock" is still available in the dropdown

app = Flask(__name__)

PAGE = """
<!doctype html>
<html>
<head>
  <title>Candidate Sourcing Tool</title>
  <style>
    body { font-family: -apple-system, sans-serif; max-width: 760px; margin: 40px auto; color: #1a1a1a; }
    h1 { font-size: 1.4rem; }
    textarea { width: 100%; height: 220px; font-family: monospace; font-size: 0.9rem; }
    label { display: block; margin-top: 12px; font-weight: 600; }
    select, button { margin-top: 6px; padding: 6px 10px; font-size: 0.95rem; }
    button { cursor: pointer; }
    .step { background: #f6f6f6; border-radius: 8px; padding: 16px; margin-top: 20px; }
    .disclaimer { color: #a15c00; font-weight: 600; }
    .candidate { border-left: 3px solid #444; padding-left: 12px; margin: 14px 0; }
    .reason { color: #444; font-size: 0.9rem; margin: 2px 0 2px 12px; }
    .pending { color: #b00020; }
  </style>
</head>
<body>
  <h1>Candidate Sourcing Tool</h1>
  <p>Paste a job description, pick a source, and run the pipeline (JD extraction &rarr;
  auto-filled recruiter confirmation &rarr; boolean filter &rarr; ranking &rarr; non-ranked
  shortlist with reasons). This demo auto-answers any still-missing Block A field so it can run
  without a real interactive terminal.</p>

  <form method="post">
    <label for="jd_text">Job description</label>
    <textarea name="jd_text" id="jd_text">{{ jd_text }}</textarea>

    <label for="source">Source</label>
    <select name="source" id="source">
      {% for name in source_names %}
        <option value="{{ name }}" {% if name == selected_source %}selected{% endif %}>{{ name }}</option>
      {% endfor %}
    </select>

    <div><button type="submit">Run search</button></div>
  </form>

  {% if pending_fields %}
  <div class="step">
    <strong class="pending">Auto-filled {{ pending_fields|length }} Block A field(s) the JD didn't specify:</strong>
    <ul>{% for f in pending_fields %}<li>{{ f }}</li>{% endfor %}</ul>
  </div>
  {% endif %}

  {% if rendered %}
  <div class="step">
    <h2>Shortlist</h2>
    <pre style="white-space: pre-wrap; font-family: -apple-system, sans-serif;">{{ rendered }}</pre>
  </div>
  {% endif %}

  {% if error %}
  <div class="step" style="border: 1px solid #b00020; color: #b00020;">{{ error }}</div>
  {% endif %}
</body>
</html>
"""

_AUTO_DEMO_ANSWERS = {
    "work_authorization": "US citizen or authorized, no sponsorship",
    "credentials": "none",
    "location_policy": "remote",
    "worksite": "remote",
    "geo_scope": "United States",
    "comp_band": "not specified",
    "excluded_employers": "none",
}

_SAMPLE_JD = (Path("tests/fixtures/sample_jds/technical_role.txt")).read_text()


@app.route("/", methods=["GET", "POST"])
def index():
    jd_text = _SAMPLE_JD
    source = "mock"
    rendered = None
    pending_fields = []
    error = None

    if request.method == "POST":
        jd_text = request.form.get("jd_text", "")
        source = request.form.get("source", "mock")
        try:
            draft = extract_draft_requirement_set(jd_text)
            pending_fields = pending_block_a_fields(draft)
            answers = {f: _AUTO_DEMO_ANSWERS.get(f, "not specified") for f in pending_fields}
            confirmed = confirm_and_save(draft, answers, requirement_store)

            adapter = get(source)
            query = " ".join(r.text for r in confirmed.requirements) or "candidate"
            candidates = adapter.fetch_candidates(query)

            result = run_search(confirmed, candidates, audit_store, user_id="owner")
            rendered = render_shortlist(result)
        except Exception as exc:  # demo UI -- surface the error plainly instead of a 500 page
            error = f"{type(exc).__name__}: {exc}"

    return render_template_string(
        PAGE,
        jd_text=jd_text,
        selected_source=source,
        source_names=all_names(),
        rendered=rendered,
        pending_fields=pending_fields,
        error=error,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5055, debug=True)
