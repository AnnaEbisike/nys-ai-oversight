"""
analysis.py
Claude-powered ethics audit and accountability gap analysis
for the NYS AI Systems Inventory.
"""

import json
from anthropic import Anthropic

MODEL = "claude-opus-4-7"

SYSTEM_PROMPT = """\
You are an expert in AI ethics, civil liberties, and government technology accountability.
You analyze government AI systems through the lens of public rights, democratic oversight,
and algorithmic accountability. Your analysis is rigorous, specific, and grounded in
concrete concerns — not vague platitudes.

You reference frameworks like the EU AI Act risk tiers, the NIST AI Risk Management
Framework, and ACLU AI principles where relevant.

Always respond with valid JSON only. No markdown fences, no commentary outside the JSON."""


def _parse_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def analyze_system(client: Anthropic, system: dict) -> dict:
    """
    Run a civil-liberties ethics audit on a single NYS AI system.
    Returns a structured dict with risk level, score, concerns, and questions.
    """
    prompt = f"""\
Analyze this New York State government AI system for civil liberties and public accountability concerns.

Agency: {system['agency']}
Vendor: {system['vendor']}
Product: {system['product']}
AI Capability Category: {system['capability']}
Stated Purpose: {system['purpose']}

Return ONLY a JSON object with exactly these fields:
{{
  "risk_level": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
  "risk_score": integer 0-100 (100 = most concerning),
  "affected_populations": [list of specific groups affected — be concrete, not generic],
  "privacy_concerns": [list of up to 5 specific privacy risks with this system],
  "civil_liberties_flags": [specific civil liberties concerns, empty list if minimal],
  "transparency_score": integer 0-10 (10 = very transparent description),
  "transparency_assessment": "1-2 sentence plain assessment of how forthcoming this description is",
  "accountability_gaps": [up to 4 missing oversight mechanisms or unanswered questions],
  "key_questions": [3-5 specific questions a journalist, legislator, or citizen should ask this agency],
  "summary": "2-3 sentence plain-language assessment of this system's overall risk profile and public interest significance"
}}"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse_json(response.content[0].text)


def analyze_gaps(client: Anthropic, systems: list) -> dict:
    """
    Analyze what is missing from the NYS AI inventory.
    Returns a structured dict with missing agencies, categories, and legislative questions.
    """
    agencies_summary = "\n".join(
        f"- {s['agency']}: {s['product']} ({s['capability']})" for s in systems
    )

    prompt = f"""\
You are analyzing New York State's first-ever public AI inventory, published September 2025.
It was mandated by executive order and covers AI systems "directly impacting the public."
Only 19 systems were disclosed across all of New York State's 50+ executive agencies.
Only 13 agencies reported anything at all.

AGENCIES AND SYSTEMS THAT DID REPORT:
{agencies_summary}

NOTABLE AGENCIES ABSENT FROM THIS INVENTORY:
- NY State Police (NYSP)
- Dept. of Corrections and Community Supervision (DOCCS)
- Division of Parole / Dept. of Corrections
- Office of Temporary and Disability Assistance (OTDA) — administers welfare/SNAP/Medicaid
- Division of Criminal Justice Services (DCJS) — statewide criminal justice data hub
- Dept. of Education (NYSED)
- Gaming Commission
- Dept. of Financial Services (DFS)
- Office of Court Administration (OCA) — semi-independent but state-funded
- Dept. of Tax and Finance
- Office of Children and Family Services (OCFS)
- And many others

Analyze the completeness, credibility, and implications of this inventory.
Return ONLY a JSON object with exactly these fields:
{{
  "credibility_assessment": "2-3 sentence assessment of whether 19 systems is credible for all of NYS government and what the low count likely reflects",
  "missing_agencies": [
    {{
      "agency": "full agency name",
      "likely_ai_uses": "specific AI tools or capabilities likely in use that impact the public",
      "concern_level": "HIGH" | "MEDIUM" | "LOW",
      "basis": "concrete reason why we would expect this agency to use public-facing AI"
    }}
  ],
  "missing_ai_categories": [
    {{
      "category": "type of AI use likely absent from inventory",
      "examples": "specific products or systems known to be used in government contexts nationally",
      "concern_level": "HIGH" | "MEDIUM" | "LOW"
    }}
  ],
  "structural_gaps": [3-5 systemic problems with how this inventory was scoped or designed],
  "best_practice_comparison": "How does this inventory compare to California's Automated Decision Systems policy, the EU AI Act transparency requirements, or other leading frameworks?",
  "legislative_questions": [exactly 5 specific, pointed questions the NYS legislature should put to the Office of ITS],
  "headline": "One accurate, punchy headline a journalist at The Markup or ProPublica might write about the limitations of this inventory"
}}

Include at least 6 missing agencies and at least 5 missing AI categories."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse_json(response.content[0].text)
