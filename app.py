"""
app.py
Watching the Watchers: NYS AI Ethics Audit & Accountability Gap Analysis
A digital humanities investigation into New York State's first AI inventory.
"""

import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from analysis import analyze_system, analyze_gaps

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Watching the Watchers | NYS AI Oversight",
    page_icon="⚠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── INVENTORY DATA ────────────────────────────────────────────────────────────

INVENTORY = [
    {
        "id": 1,
        "agency": "Office for the Aging",
        "vendor": "Intuition Robotics Inc.",
        "product": "ElliQ",
        "capability": "Personalization",
        "purpose": "Proactive AI companion for older adults combating loneliness and supporting aging-in-place. Provides daily check-ins, medication reminders, health tracking, exercise suggestions, and helps users connect with family and friends via voice commands and on-screen instructions.",
        "flag": None,
    },
    {
        "id": 2,
        "agency": "Dept. of Agriculture and Markets",
        "vendor": "Sorensen",
        "product": "Video Relay System",
        "capability": "Speech/Text Recognition",
        "purpose": "Converts spoken language into text so a staff member who is hearing impaired can answer phone calls.",
        "flag": None,
    },
    {
        "id": 3,
        "agency": "Office for People with Developmental Disabilities",
        "vendor": "Lytx",
        "product": "Machine Vision Plus",
        "capability": "Transportation / Surveillance",
        "purpose": "Advanced video telematics with machine vision and AI (MV+AI) to detect risky and distracted driving behavior inside and outside vehicles operated by or for OPWDD.",
        "flag": "surveillance",
    },
    {
        "id": 4,
        "agency": "Dept. of Labor",
        "vendor": "Eightfold / OpenAI",
        "product": "OpenAI (via Eightfold)",
        "capability": "Personalization / Algorithmic Matching",
        "purpose": "Provides tailored job opportunity recommendations to job seekers based on their experience and interests. Uses AI to match applicants to available job listings.",
        "flag": "algorithmic_decision",
    },
    {
        "id": 5,
        "agency": "Office of Medicaid Inspector General",
        "vendor": "Balto-Genysis",
        "product": "Balto",
        "capability": "Customer Service / Conversational AI",
        "purpose": "Real-time AI guidance platform for customer service associates at contractor Performant. Records and analyzes conversations for coaching. De-identifies PII before storage using numeric and name-dictionary matching. All de-identification occurs in memory.",
        "flag": "recording",
    },
    {
        "id": 6,
        "agency": "Office of Medicaid Inspector General",
        "vendor": "Microsoft",
        "product": "Copilot",
        "capability": "Natural Language Understanding",
        "purpose": "Speech/text recognition for Microsoft Teams calls used by contractor Performant. Transcripts used for recordkeeping and note-taking. Also used for summarizing documents, drafting emails, and searching data within Microsoft 365.",
        "flag": None,
    },
    {
        "id": 7,
        "agency": "Office of Medicaid Inspector General",
        "vendor": "Healthcare Management Solutions, LLC (HMS)",
        "product": "MAVS — Maestro Automated Valuation System",
        "capability": "Automation / Predictive Scoring",
        "purpose": "Automates caseworker tasks using bagged and boosted tree ML models. Valuates Medicaid claims to determine accident-relatedness. Trained on previous caseworker evaluations. The agency states it does not make autonomous medical decisions about individual eligibility.",
        "flag": "automated_decision",
    },
    {
        "id": 8,
        "agency": "Dept. of Health",
        "vendor": "Centers for Disease Control and Prevention",
        "product": "EmarcLite",
        "capability": "Natural Language Understanding",
        "purpose": "Processes free text fields in pathology reports to determine cancer case reportability. Supports statewide public health surveillance.",
        "flag": None,
    },
    {
        "id": 9,
        "agency": "Dept. of Transportation",
        "vendor": "Cubic",
        "product": "GS3 Processor (GRIDSMART)",
        "capability": "Image Recognition / Computer Vision",
        "purpose": "360-degree camera system detecting and classifying vehicles to adjust traffic signal cycle lengths statewide. All timing decisions are made by the 2070 traffic controller, not the AI. Not co-deployed with Miovision units.",
        "flag": None,
    },
    {
        "id": 10,
        "agency": "Dept. of Transportation",
        "vendor": "Miovision",
        "product": "Miovision Core",
        "capability": "Image Recognition / Computer Vision",
        "purpose": "Video stream analysis classifying objects as Cars vs. Heavy Trucks and Bicycles vs. Pedestrians. Interfaces with 2070 traffic controllers statewide. All intersection timing decisions made at the controller level.",
        "flag": None,
    },
    {
        "id": 11,
        "agency": "Dept. of Transportation",
        "vendor": "Iteris",
        "product": "VantageNext",
        "capability": "Image Recognition / Computer Vision",
        "purpose": "Combined radar and video system using CNN-based machine learning to detect vehicles and adjust traffic signal timing statewide. Uses logical OR between radar and video sensors.",
        "flag": None,
    },
    {
        "id": 12,
        "agency": "Dept. of State",
        "vendor": "Google",
        "product": "Google Translate",
        "capability": "Natural Language Understanding",
        "purpose": "Translates form labels for public users accessing state services online.",
        "flag": None,
    },
    {
        "id": 13,
        "agency": "Dept. of Motor Vehicles",
        "vendor": "Google",
        "product": "DocumentAI",
        "capability": "Document AI / IDP",
        "purpose": "Document quality checks, classification, extraction, and validation for online DMV transactions. Pre-fills form fields from uploaded identity documents. Checks for expiration and format compliance to reduce failed in-office visits.",
        "flag": "identity_document",
    },
    {
        "id": 14,
        "agency": "Dept. of Motor Vehicles",
        "vendor": "Smart Communications, Inc.",
        "product": "MAXit",
        "capability": "Natural Language Understanding",
        "purpose": "Assists DMV's Forms team in developing plain language text for accurate translation into 16 foreign languages required for vital documents.",
        "flag": None,
    },
    {
        "id": 15,
        "agency": "Higher Education Services Corp.",
        "vendor": "ElevenLabs",
        "product": "ElevenLabs (TTS)",
        "capability": "Speech Synthesis",
        "purpose": "Generates AI voiceovers for instructional videos used on social media, YouTube, and the public HESC website.",
        "flag": None,
    },
    {
        "id": 16,
        "agency": "Dept. of Environmental Conservation",
        "vendor": "Everblue",
        "product": "Pesticides Exam (Facial Recognition)",
        "capability": "Biometric Surveillance / Facial Recognition",
        "purpose": "Facial recognition monitoring of test-takers during online Pesticide Applicator certification exams. Continuously monitors participants throughout the exam, identifying irregular behavior and flagging potential cheating or misconduct.",
        "flag": "biometric",
    },
    {
        "id": 17,
        "agency": "Dept. of Environmental Conservation",
        "vendor": "Spypoint",
        "product": "Bucktracker AI",
        "capability": "Image Recognition / Computer Vision",
        "purpose": "Automatically analyzes all photos taken by trail cameras to facilitate DEC law enforcement and Forest Protection response and investigation.",
        "flag": "law_enforcement",
    },
    {
        "id": 18,
        "agency": "Dept. of Civil Service",
        "vendor": "LinkedIn Corporation",
        "product": "LinkedIn",
        "capability": "Algorithmic Hiring / Personalization",
        "purpose": "Provides personalized job recommendations and matches applicant skills from LinkedIn profiles and resumes to government job postings. Used in state hiring processes to recommend user matches for open positions.",
        "flag": "algorithmic_decision",
    },
    {
        "id": 19,
        "agency": "Dept. of Homeland Security and Emergency Services",
        "vendor": "Dataminr",
        "product": "Dataminr First Alert",
        "capability": "Monitoring and Surveillance",
        "purpose": "Identifies timely and emerging events relevant to DHSES operations through real-time data and social media monitoring.",
        "flag": "surveillance",
    },
]

FLAG_LABELS = {
    "biometric":           "⚠ BIOMETRIC",
    "surveillance":        "⚠ SURVEILLANCE",
    "automated_decision":  "⚠ AUTO-DECISION",
    "algorithmic_decision": "⚠ ALGO-HIRING",
    "recording":           "⚠ RECORDING",
    "law_enforcement":     "⚠ LAW ENFORCEMENT",
    "identity_document":   "⚠ ID DOCUMENT",
}

CAPABILITY_COLORS = {
    "Image Recognition / Computer Vision":      "#4cc9f0",
    "Natural Language Understanding":           "#9b59b6",
    "Personalization":                          "#f72585",
    "Personalization / Algorithmic Matching":   "#f72585",
    "Speech/Text Recognition":                  "#4361ee",
    "Automation / Predictive Scoring":          "#ff6b35",
    "Document AI / IDP":                        "#06d6a0",
    "Customer Service / Conversational AI":     "#ffd700",
    "Monitoring and Surveillance":              "#e63946",
    "Transportation / Surveillance":            "#e63946",
    "Biometric Surveillance / Facial Recognition": "#ff0055",
    "Algorithmic Hiring / Personalization":     "#ff6b35",
    "Speech Synthesis":                         "#4361ee",
}

# ── CSS ───────────────────────────────────────────────────────────────────────

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');

:root {
    --bg:       #0a0a0a;
    --surface:  #111111;
    --surface2: #0d0d0d;
    --border:   #1e1e1e;
    --text:     #e8e8e8;
    --muted:    #666666;
    --red:      #e63946;
    --amber:    #f4a261;
    --green:    #57cc99;
    --blue:     #4cc9f0;
    --font:     'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
    --mono:     'Space Mono', 'Courier New', monospace;
}

.stApp { background-color: var(--bg) !important; }

.main .block-container {
    padding-top: 0 !important;
    padding-bottom: 4rem !important;
    max-width: 1200px !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

* { font-family: var(--font) !important; }
code, pre, .mono { font-family: var(--mono) !important; }

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
div[data-testid="stDecoration"] { display: none; }

/* ── Tabs ────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    font-family: var(--mono) !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    padding: 0.85rem 2rem !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
    color: #ffffff !important;
    border-bottom: 2px solid var(--red) !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: var(--bg) !important;
    padding-top: 2.5rem !important;
}

/* ── Buttons ──────────────────────────────────────────────────────────── */
.stButton > button {
    background: var(--red) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: var(--mono) !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    padding: 0.75rem 2.2rem !important;
    transition: background 0.15s ease !important;
}
.stButton > button:hover { background: #b71c1c !important; border: none !important; }

/* ── Selectbox ───────────────────────────────────────────────────────── */
.stSelectbox > div > div {
    background: var(--surface) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    border-radius: 0 !important;
}

/* ── Metrics ─────────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-left: 3px solid var(--red) !important;
    padding: 1rem 1.2rem !important;
    border-radius: 0 !important;
}
[data-testid="stMetricLabel"] > div {
    font-family: var(--mono) !important;
    font-size: 0.58rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}
[data-testid="stMetricValue"] > div {
    font-family: var(--mono) !important;
    font-size: 2rem !important;
    color: #fff !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"] { display: none; }

/* ── Progress ────────────────────────────────────────────────────────── */
.stProgress > div > div > div { background: var(--red) !important; }

/* ── Sidebar ─────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] input[type="password"] {
    background: var(--bg) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    border-radius: 0 !important;
    font-family: var(--mono) !important;
    font-size: 0.8rem !important;
}

/* ── Spinner ─────────────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--red) !important; }

/* ── Alerts ──────────────────────────────────────────────────────────── */
.stAlert {
    background: var(--surface) !important;
    border-radius: 0 !important;
    color: var(--text) !important;
}

/* ── Scrollbar ───────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: #252525; }

/* ── Custom component classes ─────────────────────────────────────────── */

.hero-eyebrow {
    font-family: var(--mono);
    font-size: 0.65rem;
    letter-spacing: 0.28em;
    color: var(--red);
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}
.hero-title {
    font-size: clamp(2.2rem, 5vw, 3.8rem);
    font-weight: 700;
    line-height: 1.02;
    color: #fff;
    margin-bottom: 1rem;
    letter-spacing: -0.02em;
}
.hero-subtitle {
    font-size: 0.95rem;
    color: #666;
    max-width: 560px;
    line-height: 1.75;
}
.hero-rule {
    border: none;
    border-top: 1px solid #1a1a1a;
    margin: 1.8rem 0 0 0;
}
.hero-source {
    font-family: var(--mono);
    font-size: 0.58rem;
    color: #2a2a2a;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-top: 0.8rem;
}
.section-label {
    font-family: var(--mono);
    font-size: 0.6rem;
    letter-spacing: 0.22em;
    color: #444;
    text-transform: uppercase;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.2rem;
}
.risk-badge-CRITICAL {
    display: inline-block;
    background: #200000;
    color: #ff2222;
    border: 1px solid #660000;
    padding: 0.1rem 0.55rem;
    font-family: var(--mono);
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    font-weight: 700;
}
.risk-badge-HIGH {
    display: inline-block;
    background: #1a0800;
    color: #ff6b35;
    border: 1px solid #663300;
    padding: 0.1rem 0.55rem;
    font-family: var(--mono);
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    font-weight: 700;
}
.risk-badge-MEDIUM {
    display: inline-block;
    background: #1a1400;
    color: #ffd700;
    border: 1px solid #665500;
    padding: 0.1rem 0.55rem;
    font-family: var(--mono);
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    font-weight: 700;
}
.risk-badge-LOW {
    display: inline-block;
    background: #001408;
    color: #57cc99;
    border: 1px solid #005528;
    padding: 0.1rem 0.55rem;
    font-family: var(--mono);
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    font-weight: 700;
}
.flag-tag {
    display: inline-block;
    background: #180e00;
    color: var(--amber);
    border: 1px solid #3d2000;
    padding: 0.08rem 0.4rem;
    font-family: var(--mono);
    font-size: 0.55rem;
    letter-spacing: 0.06em;
    margin-left: 0.5rem;
    vertical-align: middle;
}
.system-row {
    display: flex;
    align-items: flex-start;
    gap: 0.9rem;
    padding: 0.85rem 0;
    border-bottom: 1px solid #151515;
}
.system-num {
    font-family: var(--mono);
    font-size: 0.6rem;
    color: #2a2a2a;
    min-width: 1.8rem;
    padding-top: 0.15rem;
}
.system-name {
    font-size: 0.88rem;
    font-weight: 600;
    color: #fff;
    line-height: 1.3;
}
.system-meta {
    font-size: 0.73rem;
    color: var(--muted);
    margin-top: 0.15rem;
}
.system-cap {
    font-size: 0.7rem;
    color: #333;
    margin-top: 0.1rem;
    font-family: var(--mono);
}
.analysis-section-head {
    font-family: var(--mono);
    font-size: 0.58rem;
    letter-spacing: 0.18em;
    color: #444;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    margin-top: 1.4rem;
}
.analysis-section-head:first-child { margin-top: 0; }
.bullet-item {
    font-size: 0.84rem;
    color: #bbb;
    padding: 0.18rem 0;
    line-height: 1.55;
    padding-left: 1.1rem;
    position: relative;
}
.bullet-item::before {
    content: "→";
    position: absolute;
    left: 0;
    color: var(--red);
    font-family: var(--mono);
    font-size: 0.75rem;
}
.question-item {
    font-size: 0.84rem;
    color: #bbb;
    padding: 0.18rem 0;
    line-height: 1.55;
    padding-left: 1.5rem;
    position: relative;
    counter-increment: q;
}
.question-item::before {
    content: counter(q, decimal-leading-zero);
    position: absolute;
    left: 0;
    color: var(--blue);
    font-family: var(--mono);
    font-size: 0.72rem;
    font-weight: 700;
}
.question-list { counter-reset: q; }
.gap-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--amber);
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.45rem;
}
.gap-agency { font-size: 0.88rem; font-weight: 600; color: #ffd700; }
.gap-detail { font-size: 0.78rem; color: #777; margin-top: 0.25rem; line-height: 1.5; }
.gap-basis  { font-size: 0.72rem; color: #444; margin-top: 0.15rem; font-style: italic; }
.cat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--blue);
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.45rem;
}
.cat-name   { font-size: 0.88rem; font-weight: 600; color: var(--blue); }
.cat-detail { font-size: 0.78rem; color: #777; margin-top: 0.25rem; line-height: 1.5; }
.headline-box {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-left: 5px solid var(--red);
    padding: 1.4rem 1.8rem;
    margin: 1.5rem 0;
}
.headline-label {
    font-family: var(--mono);
    font-size: 0.58rem;
    letter-spacing: 0.2em;
    color: #444;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.headline-text {
    font-size: 1.25rem;
    font-weight: 700;
    color: #fff;
    line-height: 1.3;
}
.credibility-box {
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 1.1rem 1.4rem;
    margin-bottom: 1.5rem;
    font-size: 0.87rem;
    color: #aaa;
    line-height: 1.75;
}
.cred-label {
    font-family: var(--mono);
    font-size: 0.58rem;
    color: #444;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.leg-question {
    background: var(--surface2);
    border-left: 2px solid var(--blue);
    padding: 0.65rem 1rem;
    margin-bottom: 0.35rem;
    font-size: 0.84rem;
    color: #bbb;
    line-height: 1.55;
}
.struct-item {
    font-size: 0.84rem;
    color: #bbb;
    padding: 0.18rem 0 0.18rem 1.1rem;
    line-height: 1.55;
    position: relative;
}
.struct-item::before {
    content: "▸";
    position: absolute;
    left: 0;
    color: var(--red);
    font-size: 0.7rem;
}
.empty-state {
    background: var(--surface);
    border: 1px dashed #1e1e1e;
    padding: 3rem 2rem;
    text-align: center;
    font-family: var(--mono);
    font-size: 0.62rem;
    color: #2a2a2a;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 1rem;
}
.about-card {
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 1.3rem 1.5rem;
    margin-bottom: 0.8rem;
}
.about-label {
    font-family: var(--mono);
    font-size: 0.58rem;
    color: #444;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 0.55rem;
}
.about-text { font-size: 0.87rem; color: #888; line-height: 1.75; }
</style>
"""

# ── HELPER FUNCTIONS ──────────────────────────────────────────────────────────

def risk_badge(level: str) -> str:
    return f'<span class="risk-badge-{level}">{level}</span>'


def flag_html(flag) -> str:
    if not flag:
        return ""
    label = FLAG_LABELS.get(flag, flag.upper())
    return f'<span class="flag-tag">{label}</span>'


def score_color(score: int) -> str:
    if score >= 75:
        return "#e63946"
    if score >= 50:
        return "#ff6b35"
    if score >= 30:
        return "#ffd700"
    return "#57cc99"


def get_client():
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        try:
            key = st.secrets.get("ANTHROPIC_API_KEY", None)
        except Exception:
            key = None
    if not key:
        return None
    from anthropic import Anthropic
    return Anthropic(api_key=key)


def bullet_list(items: list, color: str = "#e63946") -> str:
    style = f"color:{color}"
    return "".join(
        f'<div class="bullet-item" style="--bullet-color:{color}">{item}</div>'
        for item in items
    )


# ── CHARTS ────────────────────────────────────────────────────────────────────

def capability_chart():
    from collections import Counter
    counts = Counter(s["capability"] for s in INVENTORY)
    labels = list(counts.keys())
    values = list(counts.values())
    short_labels = [lb.split("/")[0].strip() for lb in labels]
    colors = [CAPABILITY_COLORS.get(lb, "#333") for lb in labels]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=short_labels,
            orientation="h",
            marker_color=colors,
            text=values,
            textposition="outside",
            textfont=dict(family="Space Mono", size=9, color="#555"),
        )
    )
    fig.update_layout(
        paper_bgcolor="#0a0a0a",
        plot_bgcolor="#0a0a0a",
        font=dict(family="Space Grotesk", color="#666", size=10),
        height=290,
        margin=dict(l=0, r=30, t=8, b=8),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=9, color="#888")),
        showlegend=False,
    )
    return fig


def vendor_donut():
    big_tech = {"Google", "Microsoft", "LinkedIn Corporation"}
    buckets = {"Big Tech": 0, "Specialized Vendor": 0}
    for s in INVENTORY:
        if any(b in s["vendor"] for b in big_tech):
            buckets["Big Tech"] += 1
        else:
            buckets["Specialized Vendor"] += 1

    fig = go.Figure(
        go.Pie(
            labels=list(buckets.keys()),
            values=list(buckets.values()),
            hole=0.62,
            marker_colors=["#4cc9f0", "#e63946"],
            textinfo="label+percent",
            textfont=dict(family="Space Mono", size=8, color="#888"),
        )
    )
    fig.update_layout(
        paper_bgcolor="#0a0a0a",
        font=dict(family="Space Grotesk", color="#666"),
        height=200,
        margin=dict(l=0, r=0, t=8, b=8),
        showlegend=False,
    )
    return fig


# ── MAIN APP ──────────────────────────────────────────────────────────────────

def main():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            '<p style="font-family:\'Space Mono\',monospace;font-size:0.58rem;'
            'color:#444;letter-spacing:0.18em;text-transform:uppercase;margin-bottom:0.4rem">'
            "Anthropic API Key</p>",
            unsafe_allow_html=True,
        )
        api_input = st.text_input(
            "", type="password", placeholder="sk-ant-...", label_visibility="collapsed"
        )
        if api_input:
            os.environ["ANTHROPIC_API_KEY"] = api_input
            st.markdown(
                '<p style="font-family:\'Space Mono\',monospace;font-size:0.6rem;color:#57cc99;margin-top:0.3rem">'
                "● KEY LOADED</p>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<p style="font-family:\'Space Mono\',monospace;font-size:0.6rem;color:#333;margin-top:0.3rem">'
                "● NO KEY — analyses disabled</p>",
                unsafe_allow_html=True,
            )
        st.markdown(
            '<hr style="border:none;border-top:1px solid #1a1a1a;margin:1.2rem 0">'
            '<p style="font-family:\'Space Mono\',monospace;font-size:0.55rem;color:#2a2a2a;line-height:1.7">'
            "Get a key at<br>console.anthropic.com</p>",
            unsafe_allow_html=True,
        )

    # ── HERO ──────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="padding:3.5rem 0 2rem 0; border-bottom:1px solid #1a1a1a; margin-bottom:2.2rem">
            <div class="hero-eyebrow">New York State · AI Transparency Investigation · 2025</div>
            <div class="hero-title">Watching<br>the Watchers</div>
            <div class="hero-subtitle">
                New York State published its first public AI inventory in September 2025.
                Nineteen systems. Thirteen agencies. Across a government of 50+ executive bodies.<br><br>
                This tool examines what was disclosed — and asks hard questions about what wasn't.
            </div>
            <hr class="hero-rule">
            <div class="hero-source">
                Dataset: NYS AI Systems Inventory, Beginning September 2025 &nbsp;·&nbsp;
                Source: NY Open Data / Office of Information Technology Services
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── STATS ROW ─────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Systems Disclosed", "19")
    with c2:
        st.metric("Agencies Reporting", "13")
    with c3:
        st.metric("Total Exec. Agencies", "50+")
    with c4:
        st.metric("Agencies Silent", "37+")

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(
        ["The Inventory", "Ethics Audit", "Accountability Gap", "About"]
    )

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 1 — THE INVENTORY
    # ─────────────────────────────────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-label">All 19 Disclosed Systems</div>', unsafe_allow_html=True)

        col_list, col_charts = st.columns([3, 2], gap="large")

        with col_list:
            for sys in INVENTORY:
                f = flag_html(sys.get("flag"))
                st.markdown(
                    f"""
                    <div class="system-row">
                        <div class="system-num">{'%02d' % sys['id']}</div>
                        <div>
                            <div class="system-name">{sys['product']}{f}</div>
                            <div class="system-meta">{sys['agency']} &nbsp;·&nbsp; {sys['vendor']}</div>
                            <div class="system-cap">{sys['capability']}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with col_charts:
            st.markdown('<div class="section-label">Capability Breakdown</div>', unsafe_allow_html=True)
            st.plotly_chart(
                capability_chart(), use_container_width=True, config={"displayModeBar": False}
            )

            st.markdown('<div class="section-label">Vendor Concentration</div>', unsafe_allow_html=True)
            st.plotly_chart(
                vendor_donut(), use_container_width=True, config={"displayModeBar": False}
            )

            flagged_count = sum(1 for s in INVENTORY if s.get("flag"))
            st.markdown(
                f"""
                <div style="background:var(--surface);border:1px solid var(--border);
                    border-left:3px solid var(--amber);padding:0.9rem 1.1rem;margin-top:0.5rem">
                    <div style="font-family:'Space Mono',monospace;font-size:0.58rem;
                        color:#444;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:0.3rem">
                        High-Attention Flags
                    </div>
                    <div style="font-family:'Space Mono',monospace;font-size:2rem;
                        font-weight:700;color:var(--amber)">{flagged_count}</div>
                    <div style="font-size:0.72rem;color:#555;margin-top:0.15rem">
                        systems with surveillance, biometric, or automated-decision flags
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 2 — ETHICS AUDIT
    # ─────────────────────────────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-label">Live Ethics Analysis · Powered by Claude</div>', unsafe_allow_html=True)
        st.markdown(
            '<p style="font-size:0.84rem;color:#555;line-height:1.75;margin-bottom:1.5rem">'
            "Select any system. Claude analyzes it through a civil liberties and public accountability lens: "
            "assessing risk, identifying affected populations, flagging privacy concerns, and generating "
            "questions the public should be asking."
            "</p>",
            unsafe_allow_html=True,
        )

        options = {f"{s['product']}  —  {s['agency']}": s for s in INVENTORY}
        selected_label = st.selectbox(
            "Select a system", list(options.keys()), label_visibility="collapsed"
        )
        selected = options[selected_label]

        f = flag_html(selected.get("flag"))
        excerpt = selected["purpose"][:200] + ("…" if len(selected["purpose"]) > 200 else "")
        st.markdown(
            f"""
            <div style="background:var(--surface);border:1px solid var(--border);
                padding:1rem 1.2rem;margin:0.8rem 0 1rem 0">
                <span style="font-size:0.88rem;font-weight:600;color:#ccc">{selected['product']}</span>
                {f}
                <span style="color:#2a2a2a">&nbsp;·&nbsp;</span>
                <span style="font-size:0.82rem;color:#555">{selected['agency']}</span>
                <span style="color:#2a2a2a">&nbsp;·&nbsp;</span>
                <span style="font-size:0.82rem;color:#444">{selected['vendor']}</span>
                <div style="font-size:0.78rem;color:#444;margin-top:0.5rem;line-height:1.6">{excerpt}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        run_btn = st.button("Run Ethics Analysis", key="run_ethics")

        if "analyses" not in st.session_state:
            st.session_state.analyses = {}

        if run_btn:
            client = get_client()
            if not client:
                st.warning("Add your Anthropic API key in the sidebar to run live analysis.")
            else:
                with st.spinner("Analyzing…"):
                    try:
                        result = analyze_system(client, selected)
                        st.session_state.analyses[selected_label] = result
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")

        if selected_label in st.session_state.analyses:
            r = st.session_state.analyses[selected_label]
            level = r.get("risk_level", "UNKNOWN")
            score = r.get("risk_score", 0)
            t_score = r.get("transparency_score", 0)

            # Header bar
            st.markdown(
                f"""
                <div style="display:flex;align-items:center;justify-content:space-between;
                    background:var(--surface2);border:1px solid var(--border);
                    padding:1rem 1.5rem;margin-top:0.5rem">
                    <div>
                        <div style="font-family:'Space Mono',monospace;font-size:0.55rem;
                            color:#333;letter-spacing:0.18em;text-transform:uppercase;
                            margin-bottom:0.3rem">Risk Level</div>
                        {risk_badge(level)}
                    </div>
                    <div style="text-align:right">
                        <div style="font-family:'Space Mono',monospace;font-size:0.55rem;
                            color:#333;letter-spacing:0.18em;text-transform:uppercase;
                            margin-bottom:0.3rem">Risk Score</div>
                        <div style="font-family:'Space Mono',monospace;font-size:1.5rem;
                            font-weight:700;color:{score_color(score)}">{score}
                            <span style="font-size:0.65rem;color:#333">/100</span>
                        </div>
                    </div>
                    <div style="text-align:right">
                        <div style="font-family:'Space Mono',monospace;font-size:0.55rem;
                            color:#333;letter-spacing:0.18em;text-transform:uppercase;
                            margin-bottom:0.3rem">Transparency</div>
                        <div style="font-family:'Space Mono',monospace;font-size:1.5rem;
                            font-weight:700;color:var(--blue)">{t_score}
                            <span style="font-size:0.65rem;color:#333">/10</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(score / 100)

            # Summary
            st.markdown(
                f"""
                <div style="background:var(--surface2);border:1px solid var(--border);
                    border-left:3px solid var(--red);padding:1.2rem 1.5rem;margin:0.8rem 0">
                    <div class="analysis-section-head">Summary</div>
                    <p style="font-size:0.87rem;color:#bbb;line-height:1.75;margin:0">
                        {r.get('summary', '')}
                    </p>
                    <p style="font-size:0.78rem;color:#444;line-height:1.6;margin:0.6rem 0 0 0;
                        font-style:italic">
                        {r.get('transparency_assessment', '')}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            left_col, right_col = st.columns(2, gap="medium")

            with left_col:
                pops = r.get("affected_populations", [])
                items_html = "".join(
                    f'<div class="bullet-item">{p}</div>' for p in pops
                )
                st.markdown(
                    f"""
                    <div style="background:var(--surface);border:1px solid var(--border);
                        padding:1rem 1.2rem;margin-bottom:0.5rem">
                        <div class="analysis-section-head">Affected Populations</div>
                        {items_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                privacy = r.get("privacy_concerns", [])
                if privacy:
                    items_html = "".join(
                        f'<div class="bullet-item">{p}</div>' for p in privacy
                    )
                    st.markdown(
                        f"""
                        <div style="background:var(--surface);border:1px solid var(--border);
                            padding:1rem 1.2rem;margin-bottom:0.5rem">
                            <div class="analysis-section-head">Privacy Concerns</div>
                            {items_html}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with right_col:
                clf = r.get("civil_liberties_flags", [])
                if clf:
                    items_html = "".join(
                        f'<div class="bullet-item">{c}</div>' for c in clf
                    )
                    st.markdown(
                        f"""
                        <div style="background:var(--surface);border:1px solid var(--border);
                            border-left:3px solid var(--red);padding:1rem 1.2rem;margin-bottom:0.5rem">
                            <div class="analysis-section-head" style="color:var(--red)">Civil Liberties Flags</div>
                            {items_html}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                gaps_a = r.get("accountability_gaps", [])
                if gaps_a:
                    items_html = "".join(
                        f'<div class="bullet-item">{g}</div>' for g in gaps_a
                    )
                    st.markdown(
                        f"""
                        <div style="background:var(--surface);border:1px solid var(--border);
                            border-left:3px solid var(--amber);padding:1rem 1.2rem;margin-bottom:0.5rem">
                            <div class="analysis-section-head" style="color:var(--amber)">Accountability Gaps</div>
                            {items_html}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            qs = r.get("key_questions", [])
            if qs:
                items_html = "".join(
                    f'<div class="question-item">{q}</div>' for q in qs
                )
                st.markdown(
                    f"""
                    <div style="background:var(--surface2);border:1px solid var(--border);
                        border-left:3px solid var(--blue);padding:1rem 1.5rem">
                        <div class="analysis-section-head" style="color:var(--blue)">
                            Questions to Ask This Agency
                        </div>
                        <div class="question-list">{items_html}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        elif not run_btn:
            st.markdown(
                '<div class="empty-state">Select a system above and click "Run Ethics Analysis"</div>',
                unsafe_allow_html=True,
            )

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 3 — ACCOUNTABILITY GAP
    # ─────────────────────────────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-label">What\'s Missing From the Inventory</div>', unsafe_allow_html=True)
        st.markdown(
            '<p style="font-size:0.84rem;color:#555;line-height:1.75;margin-bottom:1.5rem">'
            "New York State has over 50 executive agencies. Only 13 reported any AI systems. "
            "Claude analyzes the gaps: which agencies likely use public-facing AI but didn't disclose it, "
            "what categories of AI are conspicuously absent, and what questions policymakers should be asking."
            "</p>",
            unsafe_allow_html=True,
        )

        run_gap = st.button("Run Accountability Gap Analysis", key="run_gap")

        if "gap_analysis" not in st.session_state:
            st.session_state.gap_analysis = None

        if run_gap:
            client = get_client()
            if not client:
                st.warning("Add your Anthropic API key in the sidebar to run live analysis.")
            else:
                with st.spinner("Analyzing inventory gaps — this takes about 20 seconds…"):
                    try:
                        result = analyze_gaps(client, INVENTORY)
                        st.session_state.gap_analysis = result
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")

        if st.session_state.gap_analysis:
            g = st.session_state.gap_analysis

            headline = g.get("headline", "")
            if headline:
                st.markdown(
                    f"""
                    <div class="headline-box">
                        <div class="headline-label">Generated Headline</div>
                        <div class="headline-text">"{headline}"</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            cred = g.get("credibility_assessment", "")
            if cred:
                st.markdown(
                    f"""
                    <div class="credibility-box">
                        <div class="cred-label">Credibility Assessment</div>
                        {cred}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            col_miss, col_cat = st.columns(2, gap="medium")

            with col_miss:
                missing = g.get("missing_agencies", [])
                if missing:
                    st.markdown(
                        '<div class="section-label">Agencies Likely Using AI — Not Reported</div>',
                        unsafe_allow_html=True,
                    )
                    for a in missing:
                        lvl = a.get("concern_level", "MEDIUM")
                        st.markdown(
                            f"""
                            <div class="gap-card">
                                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                                    <div class="gap-agency">{a.get('agency','')}</div>
                                    {risk_badge(lvl)}
                                </div>
                                <div class="gap-detail">{a.get('likely_ai_uses','')}</div>
                                <div class="gap-basis">{a.get('basis','')}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            with col_cat:
                cats = g.get("missing_ai_categories", [])
                if cats:
                    st.markdown(
                        '<div class="section-label">AI Categories Absent from Inventory</div>',
                        unsafe_allow_html=True,
                    )
                    for c in cats:
                        lvl = c.get("concern_level", "MEDIUM")
                        st.markdown(
                            f"""
                            <div class="cat-card">
                                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                                    <div class="cat-name">{c.get('category','')}</div>
                                    {risk_badge(lvl)}
                                </div>
                                <div class="cat-detail">{c.get('examples','')}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            structural = g.get("structural_gaps", [])
            if structural:
                items_html = "".join(
                    f'<div class="struct-item">{s}</div>' for s in structural
                )
                st.markdown(
                    f"""
                    <div style="background:var(--surface);border:1px solid var(--border);
                        border-left:3px solid var(--red);padding:1rem 1.5rem;margin-top:0.8rem">
                        <div class="analysis-section-head" style="color:var(--red)">
                            Structural Gaps in Inventory Design
                        </div>
                        {items_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            best = g.get("best_practice_comparison", "")
            if best:
                st.markdown(
                    f"""
                    <div style="background:var(--surface);border:1px solid var(--border);
                        border-left:3px solid var(--blue);padding:1rem 1.5rem;margin-top:0.5rem">
                        <div class="analysis-section-head" style="color:var(--blue)">
                            Compared to Best Practices
                        </div>
                        <p style="font-size:0.86rem;color:#aaa;line-height:1.75;margin:0">{best}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            leg_qs = g.get("legislative_questions", [])
            if leg_qs:
                st.markdown(
                    '<div class="section-label" style="margin-top:1.5rem">'
                    "Questions for the NYS Legislature</div>",
                    unsafe_allow_html=True,
                )
                for i, q in enumerate(leg_qs, 1):
                    st.markdown(
                        f"""
                        <div class="leg-question">
                            <span style="font-family:'Space Mono',monospace;color:var(--blue);
                                font-weight:700;margin-right:0.8rem">{i:02d}.</span>{q}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        elif not run_gap:
            st.markdown(
                '<div class="empty-state">Click "Run Accountability Gap Analysis" to begin</div>',
                unsafe_allow_html=True,
            )

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 4 — ABOUT
    # ─────────────────────────────────────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-label">About This Project</div>', unsafe_allow_html=True)

        col_a, col_b = st.columns([3, 2], gap="large")

        with col_a:
            st.markdown(
                """
                <div class="about-card">
                    <div class="about-label">The Dataset</div>
                    <div class="about-text">
                        The NYS AI Systems Inventory (Beginning September 2025) is New York State's
                        first public disclosure of AI systems used by executive agencies that
                        "directly impact the public." It was published by the Office of Information
                        Technology Services (ITS) Chief AI Office and is updated annually.<br><br>
                        The inventory is self-reported by agencies. Back-office and internal AI tools
                        are explicitly excluded from scope. The dataset's own documentation warns that
                        it "may not capture pilot projects not yet disclosed, systems retired after
                        reporting, or private vendor changes between inventory cycles."
                    </div>
                </div>
                <div class="about-card">
                    <div class="about-label">Methodology</div>
                    <div class="about-text">
                        This tool uses Claude Opus (Anthropic) to analyze each AI system against
                        civil liberties and public accountability frameworks, including the EU AI Act
                        risk tiers, the NIST AI Risk Management Framework, and ACLU AI principles.<br><br>
                        The gap analysis draws on Claude's knowledge of government AI deployments
                        nationally to identify likely undisclosed uses. All AI analysis is generated
                        at runtime and may contain errors or omissions. The goal is to surface
                        questions and frame accountability discussions — not to make definitive
                        legal or policy conclusions.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_b:
            st.markdown(
                """
                <div class="about-card">
                    <div class="about-label">Key Numbers</div>
                    <div class="about-text">
                        <span style="color:#fff;font-weight:600">19</span> AI systems disclosed<br>
                        <span style="color:#fff;font-weight:600">13</span> of 50+ agencies reporting<br>
                        <span style="color:#fff;font-weight:600">7</span> systems with surveillance or biometric flags<br>
                        <span style="color:#fff;font-weight:600">4</span> systems with automated decision components<br>
                        <span style="color:var(--amber);font-weight:600">0</span> agencies from criminal justice<br>
                        <span style="color:var(--amber);font-weight:600">0</span> predictive policing or benefits-scoring tools disclosed
                    </div>
                </div>
                <div class="about-card">
                    <div class="about-label">Further Reading</div>
                    <div class="about-text">
                        · AI Now Institute — Annual AI Index<br>
                        · ACLU — AI and Civil Liberties<br>
                        · The Markup — Government AI Coverage<br>
                        · Electronic Frontier Foundation<br>
                        · NYS Executive Order on AI (2023)<br>
                        · EU AI Act — Risk Classification Framework
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
