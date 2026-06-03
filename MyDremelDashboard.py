# ============================================================
#  DREMEL — Enterprise Trend Intelligence Platform
#  Premium SaaS Analytics Dashboard
#  Run: streamlit run MyDremelDashboard.py
# ============================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import requests
import glob
import os
import time
from datetime import datetime
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Dremel Intelligence Platform",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY",  "")
BASE_URL        = "https://www.googleapis.com/youtube/v3/search"
STATS_URL       = "https://www.googleapis.com/youtube/v3/videos"
COMMENTS_URL    = "https://www.googleapis.com/youtube/v3/commentThreads"

# ════════════════════════════════════════════════════════════
#  PREMIUM CSS — Enterprise SaaS Design System
# ════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

/* ── Design Tokens ── */
:root {
    --dremel-navy:      #0B1B3E;
    --dremel-blue:      #1B3A6B;
    --dremel-accent:    #E8681A;
    --dremel-accent-lt: #F5832A;
    --dremel-white:     #FFFFFF;
    --dremel-offwhite:  #F7F8FA;
    --dremel-gray-100:  #F0F2F5;
    --dremel-gray-200:  #E4E7ED;
    --dremel-gray-400:  #9CA3B0;
    --dremel-gray-600:  #6B7280;
    --dremel-gray-800:  #2D3748;
    --dremel-green:     #10B981;
    --dremel-red:       #EF4444;
    --shadow-sm:        0 1px 3px rgba(11,27,62,0.08), 0 1px 2px rgba(11,27,62,0.04);
    --shadow-md:        0 4px 16px rgba(11,27,62,0.10), 0 2px 6px rgba(11,27,62,0.06);
    --shadow-lg:        0 8px 32px rgba(11,27,62,0.12), 0 4px 12px rgba(11,27,62,0.08);
    --radius-sm:        6px;
    --radius-md:        10px;
    --radius-lg:        14px;
}

/* ── Global Reset ── */
html, body, .stApp {
    background-color: var(--dremel-offwhite) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--dremel-gray-800) !important;
}
.main .block-container {
    padding-top: 0 !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--dremel-navy) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }
[data-testid="stSidebarContent"] * { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebarContent"] .stButton > button {
    background: var(--dremel-accent) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82em !important;
    letter-spacing: 0.8px !important;
    padding: 11px 0 !important;
    width: 100% !important;
    text-transform: uppercase !important;
    transition: background 0.2s !important;
    box-shadow: 0 2px 8px rgba(232,104,26,0.3) !important;
}
[data-testid="stSidebarContent"] .stButton > button:hover {
    background: var(--dremel-accent-lt) !important;
}

/* ── Sidebar Logo Block ── */
.sb-logo-block {
    background: linear-gradient(135deg, #0F2447 0%, #162F5C 100%);
    padding: 24px 20px 20px;
    margin-bottom: 4px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.sb-logo {
    font-family: 'Outfit', sans-serif;
    font-size: 1.9em;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: 5px;
    line-height: 1;
    margin: 0 0 4px 0;
}
.sb-logo-accent { color: var(--dremel-accent); }
.sb-tagline {
    font-size: 0.68em;
    font-weight: 500;
    color: rgba(255,255,255,0.4);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 0;
}
.sb-section-label {
    font-size: 0.65em;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.35) !important;
    margin: 20px 0 8px 0;
    padding: 0 20px;
    display: block;
}
.sb-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin: 12px 0;
}
.sb-status-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--dremel-green);
    margin-right: 6px;
    vertical-align: middle;
    box-shadow: 0 0 6px rgba(16,185,129,0.6);
}

/* ── Top Header Bar ── */
.top-header {
    background: linear-gradient(135deg, var(--dremel-navy) 0%, var(--dremel-blue) 100%);
    padding: 0 32px;
    height: 62px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    position: relative;
    overflow: hidden;
}
.top-header::before {
    content: '';
    position: absolute;
    right: -40px; top: -40px;
    width: 180px; height: 180px;
    background: rgba(232,104,26,0.08);
    border-radius: 50%;
}
.top-header::after {
    content: '';
    position: absolute;
    right: 60px; top: -60px;
    width: 120px; height: 120px;
    background: rgba(232,104,26,0.05);
    border-radius: 50%;
}
.header-logo {
    font-family: 'Outfit', sans-serif;
    font-size: 1.6em;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: 6px;
    text-transform: uppercase;
    z-index: 1;
}
.header-logo-accent { color: var(--dremel-accent); }
.header-subtitle {
    font-size: 0.72em;
    font-weight: 400;
    color: rgba(255,255,255,0.45);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-left: 20px;
    z-index: 1;
}
.header-right {
    display: flex;
    align-items: center;
    gap: 16px;
    z-index: 1;
}
.header-badge {
    background: rgba(232,104,26,0.15);
    border: 1px solid rgba(232,104,26,0.4);
    color: var(--dremel-accent);
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.7em;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
.header-date {
    color: rgba(255,255,255,0.4);
    font-size: 0.75em;
    font-weight: 400;
}

/* ── Hero Strip ── */
.hero-strip {
    background: var(--dremel-white);
    border-left: 5px solid var(--dremel-accent);
    border-radius: 0 0 var(--radius-lg) var(--radius-lg);
    padding: 20px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: var(--shadow-md);
}
.hero-strip-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.15em;
    font-weight: 700;
    color: var(--dremel-navy);
    margin: 0;
    letter-spacing: 0.3px;
}
.hero-strip-sub {
    color: var(--dremel-gray-400);
    font-size: 0.82em;
    margin: 3px 0 0 0;
    font-weight: 400;
}
.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #EEF6FF;
    border: 1px solid #C3D9F5;
    color: var(--dremel-blue);
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.72em;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* ── KPI Cards ── */
.kpi-card {
    background: var(--dremel-white);
    border-radius: var(--radius-lg);
    padding: 20px 18px 16px;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--dremel-gray-200);
    position: relative;
    overflow: hidden;
    transition: box-shadow 0.2s, transform 0.2s;
}
.kpi-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}
.kpi-card-accent {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--dremel-accent), var(--dremel-accent-lt));
}
.kpi-card-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #FFF3EC, #FFE6D5);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1em;
    margin-bottom: 12px;
}
.kpi-value {
    font-family: 'Outfit', sans-serif;
    font-size: 2em;
    font-weight: 800;
    color: var(--dremel-navy);
    margin: 0;
    line-height: 1;
    letter-spacing: -0.5px;
}
.kpi-label {
    font-size: 0.72em;
    font-weight: 600;
    color: var(--dremel-gray-400);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 6px 0 0 0;
}

/* ── Section Headers ── */
.section-header-block {
    margin-bottom: 20px;
}
.section-eyebrow {
    font-size: 0.65em;
    font-weight: 700;
    color: var(--dremel-accent);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin: 0 0 4px 0;
}
.section-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.3em;
    font-weight: 700;
    color: var(--dremel-navy);
    margin: 0;
    letter-spacing: -0.3px;
}
.section-subtitle {
    color: var(--dremel-gray-400);
    font-size: 0.83em;
    margin: 4px 0 0 0;
    font-weight: 400;
}
.section-divider {
    height: 2px;
    background: linear-gradient(90deg, var(--dremel-accent) 0%, var(--dremel-gray-200) 40%, transparent 100%);
    border: none;
    margin: 8px 0 20px 0;
}

/* ── Analytics Cards ── */
.analytics-card {
    background: var(--dremel-white);
    border-radius: var(--radius-lg);
    padding: 20px;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--dremel-gray-200);
    margin-bottom: 12px;
}
.analytics-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}
.analytics-card-title {
    font-weight: 700;
    color: var(--dremel-navy);
    font-size: 0.9em;
    margin: 0;
}

/* ── Gap Cards ── */
.gap-card {
    border-radius: var(--radius-md);
    padding: 14px 18px;
    margin-bottom: 10px;
    border: 1px solid transparent;
}
.gap-card-danger {
    background: #FFF8F5;
    border-color: #FDDCCC;
    border-left: 4px solid var(--dremel-accent);
}
.gap-card-success {
    background: #F0FDF6;
    border-color: #BBF7D0;
    border-left: 4px solid var(--dremel-green);
}
.gap-card-title {
    font-weight: 700;
    font-size: 0.88em;
    margin: 0 0 4px 0;
}
.gap-card-danger .gap-card-title { color: #9A3412; }
.gap-card-success .gap-card-title { color: #065F46; }
.gap-card p { color: var(--dremel-gray-600); margin: 0; font-size: 0.82em; line-height: 1.5; }

/* ── Brief Boxes ── */
.brief-card {
    background: var(--dremel-white);
    border-radius: var(--radius-md);
    padding: 14px 16px;
    margin-bottom: 10px;
    border: 1px solid var(--dremel-gray-200);
    box-shadow: var(--shadow-sm);
}
.brief-tag {
    display: inline-block;
    background: var(--dremel-navy);
    color: var(--dremel-accent);
    padding: 2px 10px;
    border-radius: 4px;
    font-size: 0.62em;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 7px;
}
.brief-text {
    color: var(--dremel-gray-800);
    font-size: 0.88em;
    line-height: 1.6;
    margin: 0;
    font-weight: 400;
}

/* ── Sentiment Blocks ── */
.sent-block {
    background: var(--dremel-white);
    border-radius: var(--radius-md);
    padding: 16px;
    margin-bottom: 10px;
    border: 1px solid var(--dremel-gray-200);
    box-shadow: var(--shadow-sm);
}
.sent-bar {
    height: 6px;
    border-radius: 3px;
    margin: 10px 0 6px;
    overflow: hidden;
    background: var(--dremel-gray-100);
    display: flex;
    gap: 2px;
}

/* ── Video Cards ── */
.video-row {
    background: var(--dremel-white);
    border-radius: var(--radius-md);
    padding: 14px 18px;
    margin-bottom: 8px;
    border: 1px solid var(--dremel-gray-200);
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.15s;
}
.video-row:hover { box-shadow: var(--shadow-md); }
.video-row-dremel {
    border-left: 4px solid var(--dremel-accent);
    background: linear-gradient(to right, #FFF9F5, var(--dremel-white));
}
.video-title { font-weight: 600; color: var(--dremel-navy); font-size: 0.88em; margin: 0 0 5px 0; line-height: 1.4; }
.video-meta { color: var(--dremel-gray-400); font-size: 0.76em; margin: 0; }

/* ── Status Pills ── */
.pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.68em;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.pill-orange { background: #FFF3EC; color: var(--dremel-accent); border: 1px solid #FDDCCC; }
.pill-green  { background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; }
.pill-blue   { background: #EEF6FF; color: var(--dremel-blue); border: 1px solid #C3D9F5; }
.pill-navy   { background: var(--dremel-navy); color: white; }
.pill-live   { background: #ECFDF5; color: #059669; border: 1px solid #6EE7B7; }

/* ── Roadmap Cards ── */
.roadmap-card {
    background: var(--dremel-white);
    border-radius: var(--radius-md);
    padding: 16px 18px;
    margin-bottom: 10px;
    border: 1px solid var(--dremel-gray-200);
    box-shadow: var(--shadow-sm);
    border-top: 3px solid var(--dremel-navy);
}
.roadmap-card-title {
    font-weight: 700;
    color: var(--dremel-navy);
    font-size: 0.88em;
    margin: 0 0 6px 0;
}
.roadmap-card p { color: var(--dremel-gray-600); font-size: 0.82em; line-height: 1.5; margin: 0 0 10px 0; }

/* ── Insight Panel ── */
.insight-panel {
    background: linear-gradient(135deg, var(--dremel-navy) 0%, var(--dremel-blue) 100%);
    border-radius: var(--radius-lg);
    padding: 24px 28px;
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
}
.insight-panel::before {
    content: '';
    position: absolute;
    right: -30px; bottom: -30px;
    width: 140px; height: 140px;
    background: rgba(232,104,26,0.1);
    border-radius: 50%;
}
.insight-eyebrow {
    font-size: 0.65em;
    font-weight: 700;
    color: var(--dremel-accent);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin: 0 0 8px 0;
}
.insight-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.2em;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0 0 10px 0;
}
.insight-body { color: rgba(255,255,255,0.7); font-size: 0.84em; line-height: 1.7; margin: 0; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--dremel-white) !important;
    border-radius: var(--radius-md) !important;
    padding: 4px !important;
    border: 1px solid var(--dremel-gray-200) !important;
    gap: 2px !important;
    box-shadow: var(--shadow-sm) !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--dremel-gray-600) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82em !important;
    border-radius: 7px !important;
    padding: 8px 14px !important;
    letter-spacing: 0.2px !important;
}
.stTabs [aria-selected="true"] {
    background: var(--dremel-navy) !important;
    color: white !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: var(--dremel-white) !important;
    border: 1px solid var(--dremel-gray-200) !important;
    border-radius: var(--radius-md) !important;
    padding: 14px !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--dremel-gray-200) !important;
    overflow: hidden !important;
}

/* ── Streamlit generic ── */
hr { border-color: var(--dremel-gray-200) !important; }
.stAlert { border-radius: var(--radius-md) !important; }
.stSpinner > div { color: var(--dremel-accent) !important; }

/* ── Footer ── */
.platform-footer {
    background: var(--dremel-navy);
    border-radius: var(--radius-lg);
    padding: 20px 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 16px;
}
.footer-logo {
    font-family: 'Outfit', sans-serif;
    font-size: 1.1em;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: 4px;
}
.footer-logo span { color: var(--dremel-accent); }
.footer-meta { color: rgba(255,255,255,0.35); font-size: 0.72em; text-align: right; }
.footer-powered { color: rgba(255,255,255,0.5); font-size: 0.72em; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ────────────────────────────────────────────────
KEYWORDS = [
    "furniture flip UK", "DIY home UK", "rotary tool DIY",
    "dremel projects", "home engraving DIY", "cordless DIY tools UK",
    "upcycle furniture UK", "DIY craft UK", "power tool beginner UK", "woodcarving UK"
]
KEYWORD_LABELS = {
    "furniture flip UK": "Furniture Flip", "DIY home UK": "DIY Home",
    "rotary tool DIY": "Rotary Tool", "dremel projects": "Dremel Projects",
    "home engraving DIY": "Home Engraving", "cordless DIY tools UK": "Cordless Tools",
    "upcycle furniture UK": "Upcycle Furniture", "DIY craft UK": "DIY Craft",
    "power tool beginner UK": "Beginner Tools", "woodcarving UK": "Woodcarving"
}
AGE_SEGMENTS = {
    "Gen Z (18-24)":       ["furniture flip", "upcycle", "DIY craft", "thrift flip"],
    "Millennials (25-34)": ["home renovation", "cordless tools", "DIY home", "first home"],
    "Gen X (35-44)":       ["rotary tool", "engraving", "woodcarving", "workshop"],
    "Boomers (45+)":       ["dremel projects", "precision tools", "woodworking", "garage DIY"]
}
DREMEL_PRODUCTS = [
    "Dremel 3000 Rotary Tool", "Dremel Lite 7760",
    "Dremel 4300", "Dremel Engraver 290", "Dremel Multi-Max MM40"
]
ROLES = [
    "Social Media Manager", "Content Manager",
    "Email Marketing Manager", "Website Manager",
    "E-Commerce Manager", "Product Manager"
]
NEXT_ACTIONS = [
    {"title": "Week 1 — Keyword Auto-Expansion", "detail": "Expand 10 seed keywords into 50+ via YouTube autocomplete and Google Suggest API.", "effort": "Low", "impact": "High"},
    {"title": "Week 2 — Live Comment NLP", "detail": "Run VADER sentiment on scraped YouTube comments in real time for brand health tracking.", "effort": "Medium", "impact": "High"},
    {"title": "Week 3 — Whisper Transcription", "detail": "Auto-transcribe top trending videos using yt-dlp + OpenAI Whisper for content mining.", "effort": "Medium", "impact": "Very High"},
    {"title": "Week 4 — Automated Monday Briefs", "detail": "Email role-specific content briefs to all 6 Dremel marketing managers every Monday 8am.", "effort": "Low", "impact": "Very High"},
    {"title": "Week 5 — Competitor Alert Engine", "detail": "Real-time alerts when competitors publish content on keywords where Dremel is absent.", "effort": "Medium", "impact": "High"},
    {"title": "Week 6 — Unified Momentum Score", "detail": "Merge YouTube + Google Trends + sentiment into one cross-platform trend momentum index.", "effort": "High", "impact": "Very High"},
]

# ── CHART THEME ───────────────────────────────────────────────
NAVY   = "#0B1B3E"; BLUE = "#1B3A6B"; ACCENT = "#E8681A"
GREEN  = "#10B981"; RED  = "#EF4444"; GRAY   = "#9CA3B0"
C_BG   = "#FFFFFF"; C_SURF = "#F7F8FA"

def premium_chart(figsize=(7, 4.5)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_SURF)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(colors="#6B7280", labelsize=8)
    ax.grid(axis="x", color="#E4E7ED", linewidth=0.7, linestyle="--", alpha=0.8)
    ax.set_axisbelow(True)
    return fig, ax

@st.cache_data(ttl=21600)
def auto_generate_keywords():
    base_terms = ["DIY UK", "dremel", "rotary tool", "furniture flip", "home craft UK"]
    all_keywords = []
    for term in base_terms:
        try:
            url = f"https://suggestqueries.google.com/complete/search?client=youtube&ds=yt&q={term}&hl=en"
            r = requests.get(url, timeout=5)
            suggestions = r.json()[1]
            for s in suggestions[:3]:
                if len(s[0]) > 3:
                    all_keywords.append(s[0])
        except:
            continue
    # Remove duplicates and limit to 15
    seen = set()
    unique = []
    for kw in all_keywords:
        if kw.lower() not in seen:
            seen.add(kw.lower())
            unique.append(kw)
    return unique[:15] if unique else KEYWORDS
def is_dremel(ch): return any(d.lower() in str(ch).lower() for d in ["dremel", "dremel europe", "dremel tools"])
def calc_score(v, l, c): return round(((l + c*2)/max(v,1)*100)*0.6 + min(v/100000,10)*0.4, 2)
def should_refresh():
    files = glob.glob("dremel_multi_*.csv")
    if not files: return True
    return time.time() - os.path.getctime(max(files, key=os.path.getctime)) > 43200

# ── YOUTUBE API ───────────────────────────────────────────────
@st.cache_data(ttl=21600)
def scrape_youtube(kw, n=8):
    try:
        r = requests.get(BASE_URL, params={
            "part":"snippet","q":kw,"type":"video","regionCode":"GB",
            "relevanceLanguage":"en","order":"viewCount","maxResults":n,
            "publishedAfter":"2024-01-01T00:00:00Z","key":YOUTUBE_API_KEY
        }, timeout=10)
        data = r.json()
        if "error" in data: return []
        return [{"keyword":kw,"video_id":i["id"]["videoId"],"title":i["snippet"]["title"],
                 "channel":i["snippet"]["channelTitle"],"published":i["snippet"]["publishedAt"][:10],
                 "url":f"https://youtube.com/watch?v={i['id']['videoId']}"} for i in data.get("items",[])]
    except: return []

@st.cache_data(ttl=21600)
def get_stats(ids):
    try:
        r = requests.get(STATS_URL, params={"part":"statistics","id":",".join(ids),"key":YOUTUBE_API_KEY}, timeout=10)
        out = {}
        for i in r.json().get("items",[]):
            s = i.get("statistics",{})
            out[i["id"]] = {"views":int(s.get("viewCount",0)),"likes":int(s.get("likeCount",0)),"comments":int(s.get("commentCount",0))}
        return out
    except: return {}

@st.cache_data(ttl=21600)
def get_comments(vid_id, n=15):
    try:
        r = requests.get(COMMENTS_URL, params={"part":"snippet","videoId":vid_id,"maxResults":n,"key":YOUTUBE_API_KEY}, timeout=10)
        return [i["snippet"]["topLevelComment"]["snippet"]["textDisplay"] for i in r.json().get("items",[])]
    except: return []

# ── VADER ─────────────────────────────────────────────────────
@st.cache_data(ttl=21600)
def get_sentiment(kw, vid_ids):
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        az = SentimentIntensityAnalyzer(); comments = []
        for v in list(vid_ids)[:3]: comments.extend(get_comments(v, 10))
        if not comments: return {"Positive":50,"Neutral":35,"Negative":15,"sample_size":0}
        pos=neu=neg=0
        for c in comments:
            sc = az.polarity_scores(c)["compound"]
            if sc >= 0.05: pos+=1
            elif sc <= -0.05: neg+=1
            else: neu+=1
        t = len(comments)
        return {"Positive":round(pos/t*100),"Neutral":round(neu/t*100),"Negative":round(neg/t*100),"sample_size":t}
    except: return {"Positive":50,"Neutral":35,"Negative":15,"sample_size":0}

# ── GOOGLE TRENDS ─────────────────────────────────────────────
@st.cache_data(ttl=21600)
def get_trends(kw):
    try:
        from pytrends.request import TrendReq
        pt = TrendReq(hl="en-GB", tz=0, timeout=(10,25))
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="GB")
        df = pt.interest_over_time()
        if df.empty: return {"current":50,"growth":0,"peak":50}
        vals = df[kw].tolist(); cur = vals[-1]
        prev = vals[-5] if len(vals)>=5 else vals[0]
        return {"current":int(cur),"growth":round(((cur-prev)/max(prev,1))*100,1),"peak":int(max(vals))}
    except: return {"current":50,"growth":0,"peak":50}

# ── GEMINI ────────────────────────────────────────────────────
def generate_video_script(trend, product, hook, idea):
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"""
Write a complete 60-second YouTube video script for Dremel UK.
Topic: {trend}
Product: {product}
Hook: {hook}
Video idea: {idea}

Return the script in this exact format:
HOOK (0-5 sec): [Opening line to grab attention]
PROBLEM (5-15 sec): [Identify the viewer's problem or desire]
SOLUTION (15-35 sec): [Show how Dremel {product} solves it - step by step]
DEMO (35-50 sec): [Specific actions to show on camera]
CTA (50-60 sec): [Call to action - what to do next]
CAPTION: [One line caption for the video post]
"""
            }],
            max_tokens=600,
            temperature=0.7
        )
        result = {}
        for line in response.choices[0].message.content.strip().split("\n"):
            if ":" in line:
                k, _, v = line.partition(":")
                result[k.strip()] = v.strip()
        return result if result else None
    except Exception as e:
        return None
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"""
You are a senior digital marketing strategist for Dremel UK, a professional DIY tools brand.
LIVE DATA: Trend={trend}, UK Growth={growth}%, Score={score}, Product={product}, Role={role}
Generate a specific actionable content brief. Return EXACTLY this format only, no extra text:
HOOK: [Punchy opening line max 15 words]
PLATFORM: [Best platforms to post on]
FORMAT: [Exact content format e.g. 60-sec Reel]
CTA: [Specific call to action]
POST_TIME: [Best day and UK time to post]
HASHTAGS: [5-7 relevant UK DIY hashtags]
IDEA_1: [Specific video title idea]
IDEA_2: [Second video title idea]
IDEA_3: [Third video title idea]
INSIGHT: [One strategic marketing insight max 20 words]
"""
            }],
            max_tokens=600,
            temperature=0.7
        )
        result = {}
        for line in response.choices[0].message.content.strip().split("\n"):
            if ":" in line:
                k, _, v = line.partition(":")
                result[k.strip()] = v.strip()
        return result if result else None
    except Exception as e:
        st.error(f"AI error: {e}")
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Auto retry up to 3 times with wait
        for attempt in range(3):
            try:
                resp = model.generate_content(f"""
You are a senior digital marketing strategist for Dremel UK.
LIVE DATA: Trend={trend}, UK Growth={growth}%, Score={score}, Product={product}, Role={role}
Generate an actionable content brief. Return EXACTLY this format, no extra text:
HOOK: [Punchy opening line max 15 words]
PLATFORM: [Best platforms]
FORMAT: [Exact content format]
CTA: [Specific call to action]
POST_TIME: [Best UK time to post]
HASHTAGS: [5-7 UK DIY hashtags]
IDEA_1: [Specific video idea]
IDEA_2: [Another video idea]
IDEA_3: [Another video idea]
INSIGHT: [Sharp marketing insight max 20 words]
""")
                result = {}
                for line in resp.text.strip().split("\n"):
                    if ":" in line:
                        k, _, v = line.partition(":")
                        result[k.strip()] = v.strip()
                return result if result else None

            except Exception as e:
                if "429" in str(e) and attempt < 2:
                    st.warning(f"Rate limit hit — waiting 60 seconds before retry {attempt + 2}/3...")
                    time.sleep(60)
                else:
                    raise e

    except Exception as e:
        st.error(f"Gemini error: {e}")
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")
        resp = model.generate_content(f"""
You are a senior digital marketing strategist for Dremel UK, a professional DIY tools brand.
LIVE TREND DATA: Topic={trend}, UK Search Growth={growth}%, Engagement Score={score}, Product={product}, Role={role}
Generate a specific, actionable content brief. Return EXACTLY this format only:
HOOK: [One punchy hook line, max 15 words]
PLATFORM: [Best platforms to post on]
FORMAT: [Exact content format e.g. 60-sec Reel]
CTA: [Specific call to action]
POST_TIME: [Best day and UK time to post]
HASHTAGS: [5-7 relevant UK DIY hashtags]
IDEA_1: [Specific video title idea]
IDEA_2: [Second video title idea]
IDEA_3: [Third video title idea]
INSIGHT: [One strategic marketing insight, max 20 words]
""")
        result = {}
        for line in resp.text.strip().split("\n"):
            if ":" in line:
                k, _, v = line.partition(":")
                result[k.strip()] = v.strip()
        return result if result else None
    except Exception as e:
        st.error(f"Gemini error: {e}"); return None

# ── DOCX ──────────────────────────────────────────────────────
def make_docx(trend, role, product, brief, ideas):
    try:
        from docx import Document
        doc = Document()
        doc.add_heading("DREMEL — AI Content Brief", 0)
        doc.add_heading(f"Trend: {trend}  |  Role: {role}", 1)
        doc.add_paragraph(f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')} | Product: {product}")
        doc.add_heading("Brief", 2)
        for k, v in brief:
            p = doc.add_paragraph(); p.add_run(f"{k}: ").bold = True; p.add_run(str(v))
        doc.add_heading("Video Ideas", 2)
        for idea in ideas: doc.add_paragraph(f"• {idea}", style="List Bullet")
        buf = BytesIO(); doc.save(buf); buf.seek(0); return buf
    except: return None

# ── SCRAPE ALL ────────────────────────────────────────────────
def scrape_all(keywords, prog, status):
    all_v = []
    for i, kw in enumerate(keywords):
        status.text(f"Scraping YouTube UK — '{kw}'...")
        prog.progress((i+1)/len(keywords))
        videos = scrape_youtube(kw)
        if not videos: continue
        ids = tuple(v["video_id"] for v in videos)
        stats = get_stats(ids)
        for v in videos:
            s = stats.get(v["video_id"], {"views":0,"likes":0,"comments":0})
            v.update(s)
            v["trend_score"]   = calc_score(s["views"], s["likes"], s["comments"])
            v["keyword_clean"] = clean_label(kw)
            v["is_dremel"]     = is_dremel(v["channel"])
            all_v.append(v)
    df = pd.DataFrame(all_v)
    df.to_csv(f"dremel_multi_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", index=False)
    return df

# ════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class='sb-logo-block'>
        <div class='sb-logo'>DRE<span class='sb-logo-accent'>MEL</span></div>
        <p class='sb-tagline'>Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<span class='sb-section-label'>Data Filters</span>", unsafe_allow_html=True)
    st.markdown("<div style='padding:0 0 0 0;'>", unsafe_allow_html=True)
    selected_keywords = st.multiselect(
        "Keywords to Monitor", KEYWORDS, default=KEYWORDS,
        label_visibility="visible", key="kw_main"
    )
    age_filter = st.selectbox(
        "Audience Age Segment", ["All Ages"] + list(AGE_SEGMENTS.keys()),
        label_visibility="visible", key="age_main"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr class='sb-divider'>", unsafe_allow_html=True)
    run_scrape = st.button("Refresh YouTube Data", use_container_width=True)

    st.markdown("<hr class='sb-divider'>", unsafe_allow_html=True)
    files = glob.glob("dremel_multi_*.csv")
    if files:
        fa = datetime.fromtimestamp(os.path.getctime(max(files, key=os.path.getctime)))
        hrs = (datetime.now() - fa).seconds // 3600
        st.markdown(f"""
        <div style='padding:0 16px;'>
            <p style='font-size:0.65em;color:rgba(255,255,255,0.35);letter-spacing:1.5px;text-transform:uppercase;margin:0 0 4px 0;'>System Status</p>
            <p style='font-size:0.78em;color:rgba(255,255,255,0.7);margin:0;'><span class='sb-status-dot'></span>Live &amp; Active</p>
            <p style='font-size:0.72em;color:rgba(255,255,255,0.35);margin:6px 0 0 0;'>Last sync: {fa.strftime('%d %b, %H:%M')}</p>
            {'<p style="font-size:0.72em;color:#E8681A;margin:4px 0 0 0;">⚡ Refresh due soon</p>' if hrs >= 11 else ''}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<p style='font-size:0.78em;color:#E8681A;padding:0 16px;'>No data — click Refresh</p>", unsafe_allow_html=True)

    st.markdown("""
    <div style='padding:20px 16px 16px; margin-top:auto;'>
        <p style='font-size:0.62em;color:rgba(255,255,255,0.2);letter-spacing:0.5px;line-height:1.6;margin:0;'>
            Auto-refreshes every 12 hours<br>
            YouTube · Google Trends · Gemini AI
        </p>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  HEADER
# ════════════════════════════════════════════════════════════
auto_ref = should_refresh()
now_str  = datetime.now().strftime("%d %b %Y  %H:%M")

st.markdown(f"""
<div class='top-header'>
    <div style='display:flex;align-items:center;gap:0;z-index:1;'>
        <span class='header-logo'>DRE<span class='header-logo-accent'>MEL</span></span>
        <span class='header-subtitle'>UK DIY Trend Intelligence Platform</span>
    </div>
    <div class='header-right'>
        <span class='header-badge'>{'⚡ Live — Auto Refreshing' if auto_ref else '● Live Data'}</span>
        <span class='header-date'>{now_str}</span>
    </div>
</div>
<div class='hero-strip'>
    <div>
        <p class='hero-strip-title'>Market Trend Intelligence Dashboard</p>
        <p class='hero-strip-sub'>Automated UK DIY trend detection · YouTube scraping · NLP sentiment · AI content recommendations</p>
    </div>
    <div style='display:flex;gap:8px;flex-wrap:wrap;'>
        <span class='hero-pill'>🎯 YouTube UK</span>
        <span class='hero-pill'>📈 Google Trends</span>
        <span class='hero-pill'>🤖 Gemini AI</span>
        <span class='hero-pill'>💬 VADER NLP</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  LOAD DATA
# ════════════════════════════════════════════════════════════
df = None
if run_scrape or auto_ref or not glob.glob("dremel_multi_*.csv"):
    if auto_ref and not run_scrape:
        st.info("Auto-refreshing data — 12-hour intelligence cycle...")
    prog = st.progress(0); status = st.empty()
    df = scrape_all(selected_keywords, prog, status)
    prog.empty(); status.empty()
    st.success(f"Intelligence update complete — {len(df)} videos analysed from YouTube UK.")
else:
    files = glob.glob("dremel_multi_*.csv")
    if files:
        try:
            try:
                df = pd.read_csv(max(files, key=os.path.getctime))
                if len(df) == 0:
                    df = None
            except:
                df = None
            if df.empty:
                df = None
        except:
            df = None

if df is None or len(df) == 0:
    st.warning("No data loaded. Click Refresh in the sidebar to begin scraping.")
    st.stop()

if "keyword_clean" not in df.columns: df["keyword_clean"] = df["keyword"].apply(clean_label)
if "is_dremel"     not in df.columns: df["is_dremel"]     = df["channel"].apply(is_dremel)

if age_filter != "All Ages":
    age_kws = AGE_SEGMENTS[age_filter]
    dff = df[df["keyword"].apply(lambda x: any(a in str(x).lower() for a in age_kws))]
    if len(dff) > 0: df = dff

leaderboard = (
    df.groupby("keyword_clean")
    .agg(avg_score=("trend_score","mean"), avg_views=("views","mean"),
         video_count=("video_id","count"), dremel_present=("is_dremel","any"))
    .sort_values("avg_score", ascending=False).reset_index()
)

# ════════════════════════════════════════════════════════════
#  KPI CARDS
# ════════════════════════════════════════════════════════════
tt = leaderboard.iloc[0]["keyword_clean"]
pv = int(leaderboard["avg_views"].max())
gp = len(leaderboard[~leaderboard["dremel_present"]])

k1,k2,k3,k4,k5 = st.columns(5)
kpi_data = [
    ("🔥", tt, "Top Trending Topic"),
    ("👁️", f"{pv//1_000_000}M+", "Peak Avg Views"),
    ("⚠️", f"{gp}/{len(leaderboard)}", "Content Gaps"),
    ("📹", str(len(df)), "Videos Analysed"),
    ("🌐", "4 Sources", "Real Data Sources"),
]
for col, (icon, val, lbl) in zip([k1,k2,k3,k4,k5], kpi_data):
    col.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-card-accent'></div>
        <div class='kpi-card-icon'>{icon}</div>
        <p class='kpi-value'>{val}</p>
        <p class='kpi-label'>{lbl}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  TABS
# ════════════════════════════════════════════════════════════
tab1,tab2,tab3,tab4,tab5,tab6,tab7 = st.tabs([
    "📊  Trend Leaderboard",
    "📈  Google Trends UK",
    "💬  Audience Sentiment",
    "🔴  Gap Analysis",
    "🎬  YouTube Insights",
    "💡  AI Ideation & Briefs",
    "🗺️  Roadmap"
])

# ── TAB 1 — TREND LEADERBOARD ────────────────────────────────
with tab1:
    st.markdown("""
    <div class='section-header-block'>
        <p class='section-eyebrow'>Market Intelligence</p>
        <p class='section-title'>UK DIY Trend Leaderboard</p>
        <p class='section-subtitle'>Real YouTube engagement scores — ranked by trend momentum across UK DIY content</p>
    </div>
    <hr class='section-divider'>
    """, unsafe_allow_html=True)

    ca,cb = st.columns(2)
    with ca:
        fig,ax = premium_chart()
        lb = leaderboard.sort_values("avg_score", ascending=True)
        bar_colors = [GREEN if p else ACCENT for p in lb["dremel_present"]]
        bars = ax.barh(lb["keyword_clean"], lb["avg_score"], color=bar_colors, edgecolor="none", height=0.52)
        for bar,val in zip(bars, lb["avg_score"]):
            ax.text(bar.get_width()+0.04, bar.get_y()+bar.get_height()/2,
                    f"{val:.2f}", va="center", color=NAVY, fontsize=8.5, fontweight="700")
        ax.set_title("Trend Engagement Score by Keyword", color=NAVY, fontweight="bold", pad=12, fontsize=10.5, loc="left")
        ax.set_xlabel("Engagement Score", color=GRAY, fontsize=8.5)
        ax.set_xlim(0, lb["avg_score"].max()*1.3)
        ax.legend(handles=[mpatches.Patch(color=GREEN,label="Dremel Active"),
                           mpatches.Patch(color=ACCENT,label="Content Gap")],
                  facecolor=C_BG, edgecolor="#E4E7ED", labelcolor=NAVY, fontsize=8)
        plt.tight_layout(); st.pyplot(fig); plt.close()

    with cb:
        fig2,ax2 = premium_chart()
        lv = leaderboard.sort_values("avg_views", ascending=True)
        bar_colors2 = [GREEN if p else BLUE for p in lv["dremel_present"]]
        vals = lv["avg_views"]/1_000_000
        bars2 = ax2.barh(lv["keyword_clean"], vals, color=bar_colors2, edgecolor="none", height=0.52)
        for bar,val in zip(bars2, vals):
            ax2.text(bar.get_width()+0.15, bar.get_y()+bar.get_height()/2,
                     f"{val:.1f}M", va="center", color=NAVY, fontsize=8.5, fontweight="700")
        ax2.set_title("Average Views per Keyword (Millions)", color=NAVY, fontweight="bold", pad=12, fontsize=10.5, loc="left")
        ax2.set_xlabel("Avg Views (Millions)", color=GRAY, fontsize=8.5)
        ax2.set_xlim(0, vals.max()*1.3)
        plt.tight_layout(); st.pyplot(fig2); plt.close()

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    d = leaderboard.copy()
    d["avg_views"]      = d["avg_views"].apply(lambda x: f"{int(x):,}")
    d["avg_score"]      = d["avg_score"].apply(lambda x: f"{x:.2f}")
    d["dremel_present"] = d["dremel_present"].apply(lambda x: "✅ Active" if x else "⚠️ Gap")
    d.columns = ["Keyword","Trend Score","Avg Views","Videos","Dremel Status"]
    st.dataframe(d, width="stretch", hide_index=True)

# ── TAB 2 — GOOGLE TRENDS ────────────────────────────────────
with tab2:
    st.markdown("""
    <div class='section-header-block'>
        <p class='section-eyebrow'>Search Intelligence</p>
        <p class='section-title'>Google Trends — Real UK Search Data</p>
        <p class='section-subtitle'>Live search interest scores and 3-month growth rates pulled directly from Google Trends UK</p>
    </div>
    <hr class='section-divider'>
    """, unsafe_allow_html=True)

    st.info("Fetching live UK search intelligence from Google Trends — estimated 20–30 seconds...")
    td=[]; gp2=st.progress(0); kf=selected_keywords[:6]
    for i,kw in enumerate(kf):
        gp2.progress((i+1)/len(kf))
        gt_result=get_trends(kw)
        td.append({"Keyword":kw,"Search Score":gt_result["current"],"Growth %":gt_result["growth"],"Peak":gt_result["peak"]})
        time.sleep(3)
    gp2.empty()
    gt_df = pd.DataFrame(td).sort_values("Growth %", ascending=False)

    ct1,ct2 = st.columns(2)
    with ct1:
        fig3,ax3 = premium_chart()
        c3 = [GREEN if g>0 else RED for g in gt_df["Growth %"]]
        b3 = ax3.barh(gt_df["Keyword"], gt_df["Growth %"], color=c3, edgecolor="none", height=0.52)
        for bar,val in zip(b3, gt_df["Growth %"]):
            ax3.text(bar.get_width()+(0.4 if val>=0 else -0.4), bar.get_y()+bar.get_height()/2,
                     f"{val:+.1f}%", va="center", color=NAVY, fontsize=8.5, fontweight="700")
        ax3.set_title("UK Search Growth Rate — Last 3 Months", color=NAVY, fontweight="bold", fontsize=10.5, loc="left")
        ax3.axvline(0, color="#E4E7ED", linewidth=1.2)
        plt.tight_layout(); st.pyplot(fig3); plt.close()

    with ct2:
        fig4,ax4 = premium_chart()
        b4 = ax4.barh(gt_df["Keyword"], gt_df["Search Score"], color=NAVY, edgecolor="none", height=0.52, alpha=0.85)
        for bar,val in zip(b4, gt_df["Search Score"]):
            ax4.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2,
                     str(val), va="center", color=NAVY, fontsize=8.5, fontweight="700")
        ax4.set_title("Current UK Search Interest (0–100)", color=NAVY, fontweight="bold", fontsize=10.5, loc="left")
        ax4.set_xlim(0, 115)
        plt.tight_layout(); st.pyplot(fig4); plt.close()

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    gd = gt_df.copy(); gd["Growth %"] = gd["Growth %"].apply(lambda x: f"{x:+.1f}%")
    st.dataframe(gd, width="stretch", hide_index=True)

# ── TAB 3 — SENTIMENT ────────────────────────────────────────
with tab3:
    st.markdown("""
    <div class='section-header-block'>
        <p class='section-eyebrow'>Brand Health</p>
        <p class='section-title'>Audience Sentiment Analysis</p>
        <p class='section-subtitle'>Real NLP sentiment scoring on live YouTube comments using VADER natural language processing</p>
    </div>
    <hr class='section-divider'>
    """, unsafe_allow_html=True)

    st.info("Analysing real YouTube comments with VADER NLP — fetching live audience data...")
    sp=st.progress(0); sr={}; ka=df["keyword"].unique()[:6]
    for i,kw in enumerate(ka):
        sp.progress((i+1)/len(ka))
        vids=tuple(df[df["keyword"]==kw]["video_id"].tolist())
        sr[kw]=get_sentiment(kw,vids)
    sp.empty()

    cs1,cs2 = st.columns([3,2])
    with cs1:
        st.markdown("<p style='font-weight:700;color:#0B1B3E;font-size:0.9em;margin-bottom:14px;'>Sentiment Breakdown by Keyword</p>", unsafe_allow_html=True)
        for kw,sent in sr.items():
            pos=sent["Positive"]; neu=sent["Neutral"]; neg=sent["Negative"]; n=sent["sample_size"]
            st.markdown(f"""
            <div class='analytics-card' style='padding:14px 18px;margin-bottom:8px;'>
                <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>
                    <p style='font-weight:700;color:#0B1B3E;font-size:0.88em;margin:0;'>{kw}</p>
                    <span style='font-size:0.72em;color:#9CA3B0;'>{n} comments analysed</span>
                </div>
                <div style='height:6px;border-radius:3px;overflow:hidden;background:#F0F2F5;display:flex;gap:1px;margin-bottom:8px;'>
                    <div style='width:{pos}%;background:{GREEN};'></div>
                    <div style='width:{neu}%;background:#4A6CF7;'></div>
                    <div style='width:{neg}%;background:{ACCENT};'></div>
                </div>
                <div style='display:flex;gap:16px;'>
                    <span style='font-size:0.75em;font-weight:600;color:{GREEN};'>● Positive {pos}%</span>
                    <span style='font-size:0.75em;font-weight:600;color:#4A6CF7;'>● Neutral {neu}%</span>
                    <span style='font-size:0.75em;font-weight:600;color:{ACCENT};'>● Negative {neg}%</span>
                </div>
            </div>""", unsafe_allow_html=True)

    with cs2:
        if sr:
            ap=int(sum(v["Positive"] for v in sr.values())/len(sr))
            an=int(sum(v["Negative"] for v in sr.values())/len(sr))
            au=100-ap-an
        else: ap,au,an=50,35,15

        st.markdown(f"""
        <div class='insight-panel'>
            <p class='insight-eyebrow'>Overall Brand Sentiment</p>
            <p class='insight-title'>Dremel UK Audience Health</p>
            <p class='insight-body'>Based on real YouTube comment analysis across {len(sr)} keyword categories.</p>
        </div>
        <div class='analytics-card' style='margin-top:12px;'>
            <div style='display:flex;justify-content:space-between;margin-bottom:14px;'>
                <div style='text-align:center;'>
                    <p style='font-family:Outfit,sans-serif;font-size:2em;font-weight:800;color:{GREEN};margin:0;'>{ap}%</p>
                    <p style='font-size:0.72em;font-weight:600;color:#9CA3B0;text-transform:uppercase;letter-spacing:1px;margin:4px 0 0 0;'>Positive</p>
                </div>
                <div style='text-align:center;'>
                    <p style='font-family:Outfit,sans-serif;font-size:2em;font-weight:800;color:#4A6CF7;margin:0;'>{au}%</p>
                    <p style='font-size:0.72em;font-weight:600;color:#9CA3B0;text-transform:uppercase;letter-spacing:1px;margin:4px 0 0 0;'>Neutral</p>
                </div>
                <div style='text-align:center;'>
                    <p style='font-family:Outfit,sans-serif;font-size:2em;font-weight:800;color:{ACCENT};margin:0;'>{an}%</p>
                    <p style='font-size:0.72em;font-weight:600;color:#9CA3B0;text-transform:uppercase;letter-spacing:1px;margin:4px 0 0 0;'>Negative</p>
                </div>
            </div>
            <div style='height:8px;border-radius:4px;overflow:hidden;display:flex;gap:2px;'>
                <div style='width:{ap}%;background:{GREEN};'></div>
                <div style='width:{au}%;background:#4A6CF7;'></div>
                <div style='width:{an}%;background:{ACCENT};'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── TAB 4 — GAP ANALYSIS ─────────────────────────────────────
with tab4:
    st.markdown("""
    <div class='section-header-block'>
        <p class='section-eyebrow'>Opportunity Intelligence</p>
        <p class='section-title'>Content Gap Analysis</p>
        <p class='section-subtitle'>Identifying where Dremel is absent from high-traffic UK DIY conversations</p>
    </div>
    <hr class='section-divider'>
    """, unsafe_allow_html=True)

    cg1,cg2 = st.columns([3,2])
    with cg1:
        for _,row in leaderboard.sort_values("avg_score",ascending=False).iterrows():
            p=row["dremel_present"]
            cc="gap-card-success" if p else "gap-card-danger"
            st_="Dremel is active — maintain and optimise posting cadence" if p else "No Dremel content detected — immediate action required"
            ac=f"Untapped reach: {int(row['avg_views']/1e6):.0f}M average views with zero Dremel presence" if not p else ""
            st.markdown(f"""
            <div class='gap-card {cc}'>
                <div style='display:flex;justify-content:space-between;align-items:center;'>
                    <p class='gap-card-title'>{row['keyword_clean']}</p>
                    <span style='font-size:0.72em;font-weight:700;color:#9CA3B0;'>Score: {row['avg_score']:.2f}</span>
                </div>
                <p>{st_}</p>
                {"<p style='color:#9A3412;font-weight:600;margin-top:4px;'>"+ac+"</p>" if ac else ""}
            </div>""", unsafe_allow_html=True)

    with cg2:
        ng=len(leaderboard[~leaderboard["dremel_present"]])
        nc=len(leaderboard[leaderboard["dremel_present"]])
        gv=leaderboard[~leaderboard["dremel_present"]]["avg_views"].sum()

        st.markdown(f"""
        <div class='insight-panel'>
            <p class='insight-eyebrow'>Gap Summary</p>
            <p class='insight-title'>{ng} of {len(leaderboard)} Keywords Uncovered</p>
            <p class='insight-body'>{int(gv/1e6)}M+ average views are untapped by Dremel across {ng} trending topics.</p>
        </div>
        """, unsafe_allow_html=True)

        st.metric("Keywords with no Dremel content", f"{ng} / {len(leaderboard)}")
        st.metric("Total untapped avg views",        f"{int(gv/1e6)}M+")
        st.metric("Active Dremel keywords",          f"{nc}")

        if ng > 0:
            tg=leaderboard[~leaderboard["dremel_present"]].iloc[0]
            st.markdown(f"""
            <div class='gap-card gap-card-danger' style='margin-top:16px;'>
                <p style='font-size:0.65em;font-weight:700;color:{ACCENT};letter-spacing:2px;text-transform:uppercase;margin:0 0 6px 0;'>🚨 Top Priority Gap</p>
                <p class='gap-card-title'>{tg['keyword_clean']}</p>
                <p>Avg {int(tg['avg_views']/1e6)}M views · Score {tg['avg_score']:.2f}</p>
                <p style='color:#9A3412;font-weight:700;margin-top:6px;'>Create content immediately →</p>
            </div>""", unsafe_allow_html=True)

# ── TAB 5 — YOUTUBE INSIGHTS ─────────────────────────────────
with tab5:
    st.markdown("""
    <div class='section-header-block'>
        <p class='section-eyebrow'>YouTube Intelligence</p>
        <p class='section-title'>Trending DIY Videos — UK Market</p>
        <p class='section-subtitle'>Real-time scraped videos ranked by trend engagement score</p>
    </div>
    <hr class='section-divider'>
    """, unsafe_allow_html=True)

    skw=st.selectbox("Filter by keyword category:", ["All Keywords"]+list(df["keyword_clean"].unique()), key="vid_kw")
    vdf=(df.sort_values("trend_score",ascending=False).head(20) if skw=="All Keywords"
         else df[df["keyword_clean"]==skw].sort_values("trend_score",ascending=False).head(20))

    for _,row in vdf.iterrows():
        isd=row["is_dremel"]
        card_class="video-row video-row-dremel" if isd else "video-row"
        badge=f'<span class="pill pill-orange" style="font-size:0.65em;">DREMEL</span>' if isd else f'<span class="pill" style="background:#F0F2F5;color:#6B7280;font-size:0.65em;border:1px solid #E4E7ED;">CREATOR</span>'
        st.markdown(f"""
        <div class='{card_class}'>
            <div style='display:flex;justify-content:space-between;align-items:flex-start;gap:12px;'>
                <p class='video-title'>{str(row['title'])[:95]}...</p>
                {badge}
            </div>
            <p class='video-meta'>
                {row['channel']} &nbsp;·&nbsp; {int(row['views']):,} views
                &nbsp;·&nbsp; Trend Score: <strong>{row['trend_score']}</strong>
                &nbsp;·&nbsp; <a href='{row.get("url","#")}' target='_blank' style='color:{ACCENT};font-weight:600;text-decoration:none;'>Watch on YouTube →</a>
            </p>
        </div>""", unsafe_allow_html=True)

# ── TAB 6 — AI IDEATION ──────────────────────────────────────
with tab6:
    st.markdown(f"""
    <div class='section-header-block'>
        <p class='section-eyebrow'>AI Recommendations</p>
        <p class='section-title'>Content Ideation Centre &nbsp;<span class='pill pill-green' style='font-size:0.55em;vertical-align:middle;'>GROQ AI LIVE</span></p>
        <p class='section-subtitle'>AI-powered content briefs — hooks, CTAs, platforms, formats, video ideas generated by Groq AI</p>
    </div>
    <hr class='section-divider'>
    """, unsafe_allow_html=True)

    ci1,ci2,ci3 = st.columns(3)
    with ci1:
        st.markdown("<p style='font-size:0.75em;font-weight:700;color:#6B7280;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;'>Trending Topic</p>", unsafe_allow_html=True)
        sel_trend=st.selectbox("T",leaderboard["keyword_clean"].tolist(),label_visibility="collapsed",key="id_trend")
    with ci2:
        st.markdown("<p style='font-size:0.75em;font-weight:700;color:#6B7280;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;'>Marketing Role</p>", unsafe_allow_html=True)
        sel_role=st.selectbox("R",ROLES,label_visibility="collapsed",key="id_role")
    with ci3:
        st.markdown("<p style='font-size:0.75em;font-weight:700;color:#6B7280;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;'>Dremel Product</p>", unsafe_allow_html=True)
        sel_product=st.selectbox("P",DREMEL_PRODUCTS,label_visibility="collapsed",key="id_product")

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    gen_btn=st.button("Generate AI Content Brief", use_container_width=True)

    if gen_btn:
        tr=leaderboard[leaderboard["keyword_clean"]==sel_trend].iloc[0]
        sv=round(tr["avg_score"],2)
        rkw=next((k for k,v in KEYWORD_LABELS.items() if v==sel_trend), sel_trend)

        with st.spinner("Groq AI is generating your strategic brief..."):
            gtd = get_trends(rkw)
            grw = gtd["growth"]
            aib = generate_ai_brief(sel_trend, sel_role, sel_product, sv, grw)
            
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='insight-panel' style='margin-bottom:20px;'>
            <p class='insight-eyebrow'>AI Content Brief — {sel_role}</p>
            <p class='insight-title'>{sel_trend} × {sel_product}</p>
            <p class='insight-body'>Google Trends Growth: {grw:+.1f}% &nbsp;·&nbsp; Engagement Score: {sv} &nbsp;·&nbsp; Generated {datetime.now().strftime('%d %b %Y, %H:%M')}</p>
        </div>
        """, unsafe_allow_html=True)

        if aib:
            dk=["HOOK","PLATFORM","FORMAT","CTA","POST_TIME","HASHTAGS","INSIGHT"]
            ik=["IDEA_1","IDEA_2","IDEA_3"]
            bi=[(k,aib.get(k,"")) for k in dk if aib.get(k)]
            idls=[aib.get(k,"") for k in ik if aib.get(k)]

            cb1,cb2=st.columns(2); half=len(bi)//2
            for lbl,val in bi[:half]:
                cb1.markdown(f"<div class='brief-card'><span class='brief-tag'>{lbl}</span><p class='brief-text'>{val}</p></div>", unsafe_allow_html=True)
            for lbl,val in bi[half:]:
                cb2.markdown(f"<div class='brief-card'><span class='brief-tag'>{lbl}</span><p class='brief-text'>{val}</p></div>", unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(
                "<p style='font-weight:700;color:#0B1B3E;font-size:0.92em;margin-bottom:12px;'>Auto-Generated 60-Second Video Script</p>",
                unsafe_allow_html=True)

            if idls:
                with st.spinner("Generating 60-second video script..."):
                    hook_text = aib.get("HOOK", f"Watch this {sel_trend} transformation")
                    script = generate_video_script(sel_trend, sel_product, hook_text, idls[0])

                if script:
                    script_keys = ["HOOK (0-5 sec)", "PROBLEM (5-15 sec)", "SOLUTION (15-35 sec)",
                                   "DEMO (35-50 sec)", "CTA (50-60 sec)", "CAPTION"]
                    for sk in script_keys:
                        val = script.get(sk, "")
                        if val:
                            color = {"HOOK (0-5 sec)": "#E8681A", "CTA (50-60 sec)": "#10B981",
                                     "CAPTION": "#1B3A6B"}.get(sk, "#0B1B3E")
                            st.markdown(f"""
                            <div class='brief-card' style='border-left:4px solid {color};'>
                                <span class='brief-tag' style='background:{color};'>{sk}</span>
                                <p class='brief-text'>{val}</p>
                            </div>""", unsafe_allow_html=True)
                else:
                    st.warning("Script generation failed — try again in a moment.")
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<p style='font-weight:700;color:#0B1B3E;font-size:0.92em;margin-bottom:12px;'>Content Ideas</p>", unsafe_allow_html=True)
            ic1,ic2,ic3=st.columns(3)
            for idx,(idea,col) in enumerate(zip(idls,[ic1,ic2,ic3])):
                col.markdown(f"""
                <div class='analytics-card' style='border-top:3px solid {ACCENT};'>
                    <p style='font-size:0.65em;font-weight:700;color:{ACCENT};text-transform:uppercase;letter-spacing:1.5px;margin:0 0 8px 0;'>Video Idea {idx+1}</p>
                    <p style='font-weight:600;color:#0B1B3E;font-size:0.88em;line-height:1.5;margin:0;'>🎬 {idea}</p>
                </div>""", unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<p style='font-weight:700;color:#0B1B3E;font-size:0.92em;margin-bottom:12px;'>Keyword → Search Intent → Content Idea</p>", unsafe_allow_html=True)
            ek1,ek2,ek3=st.columns(3)
            lvl_colors=[NAVY,ACCENT,GREEN]
            lvl_labels=["Level 1 — Keyword","Level 2 — Search Intent","Level 3 — Content Idea"]
            lvl_bodies=[sel_trend,f"How to do {sel_trend.lower()} for beginners UK 2025",f"I tried {sel_trend.lower()} using only a {sel_product} — here's what happened"]
            for col,color,lbl,body in zip([ek1,ek2,ek3],lvl_colors,lvl_labels,lvl_bodies):
                col.markdown(f"""
                <div class='analytics-card' style='border-top:3px solid {color};'>
                    <p style='font-size:0.65em;font-weight:700;color:{color};text-transform:uppercase;letter-spacing:1.5px;margin:0 0 8px 0;'>{lbl}</p>
                    <p style='font-weight:600;color:#0B1B3E;font-size:0.88em;line-height:1.5;margin:0;'>{body}</p>
                </div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            dbuf=make_docx(sel_trend,sel_role,sel_product,bi,idls)
            if dbuf:
                st.download_button(
                    label="📄  Download Brief as Word Document",
                    data=dbuf,
                    file_name=f"Dremel_Brief_{sel_trend.replace(' ','_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        else:
            st.error("Gemini could not generate a brief. Please check your GEMINI_API_KEY in the .env file.")

# ── TAB 7 — ROADMAP ──────────────────────────────────────────
with tab7:
    st.markdown("""
    <div class='section-header-block'>
        <p class='section-eyebrow'>Strategic Planning</p>
        <p class='section-title'>Automation Roadmap — Next Steps</p>
        <p class='section-subtitle'>Six-week plan to evolve this dashboard into a fully autonomous Dremel intelligence pipeline</p>
    </div>
    <hr class='section-divider'>
    """, unsafe_allow_html=True)

    cn1,cn2=st.columns(2)
    effort_colors={"Low":GREEN,"Medium":ACCENT,"High":RED}
    impact_colors={"High":ACCENT,"Very High":RED}
    for i,a in enumerate(NEXT_ACTIONS):
        col=cn1 if i%2==0 else cn2
        ec=effort_colors.get(a["effort"],GRAY)
        ic=impact_colors.get(a["impact"],GRAY)
        col.markdown(f"""
        <div class='roadmap-card'>
            <p class='roadmap-card-title'>{a['title']}</p>
            <p>{a['detail']}</p>
            <div style='display:flex;gap:8px;flex-wrap:wrap;'>
                <span style='display:inline-block;background:{ec}15;color:{ec};border:1px solid {ec}40;padding:2px 10px;border-radius:20px;font-size:0.68em;font-weight:700;'>Effort: {a["effort"]}</span>
                <span style='display:inline-block;background:{ic}15;color:{ic};border:1px solid {ic}40;padding:2px 10px;border-radius:20px;font-size:0.68em;font-weight:700;'>Impact: {a["impact"]}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='insight-panel'>
        <p class='insight-eyebrow'>End State Vision</p>
        <p class='insight-title'>Fully Autonomous Dremel Intelligence System</p>
        <div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px;'>
            <div style='background:rgba(255,255,255,0.06);border-radius:8px;padding:14px 16px;border:1px solid rgba(255,255,255,0.08);'>
                <p style='color:{ACCENT};font-weight:700;font-size:0.75em;text-transform:uppercase;letter-spacing:1px;margin:0 0 5px 0;'>01 — Auto Scrape</p>
                <p style='color:rgba(255,255,255,0.65);font-size:0.82em;line-height:1.5;margin:0;'>Cron job every Monday 7am — scrapes YouTube UK + Google Trends automatically</p>
            </div>
            <div style='background:rgba(255,255,255,0.06);border-radius:8px;padding:14px 16px;border:1px solid rgba(255,255,255,0.08);'>
                <p style='color:{ACCENT};font-weight:700;font-size:0.75em;text-transform:uppercase;letter-spacing:1px;margin:0 0 5px 0;'>02 — NLP Pipeline</p>
                <p style='color:rgba(255,255,255,0.65);font-size:0.82em;line-height:1.5;margin:0;'>VADER scores real YouTube comments — sentiment dashboard updates automatically</p>
            </div>
            <div style='background:rgba(255,255,255,0.06);border-radius:8px;padding:14px 16px;border:1px solid rgba(255,255,255,0.08);'>
                <p style='color:{ACCENT};font-weight:700;font-size:0.75em;text-transform:uppercase;letter-spacing:1px;margin:0 0 5px 0;'>03 — AI Briefs</p>
                <p style='color:rgba(255,255,255,0.65);font-size:0.82em;line-height:1.5;margin:0;'>Gemini AI generates role-specific briefs — emailed to all 6 managers by 8am Monday</p>
            </div>
            <div style='background:rgba(255,255,255,0.06);border-radius:8px;padding:14px 16px;border:1px solid rgba(255,255,255,0.08);'>
                <p style='color:{ACCENT};font-weight:700;font-size:0.75em;text-transform:uppercase;letter-spacing:1px;margin:0 0 5px 0;'>04 — Zero Manual Work</p>
                <p style='color:rgba(255,255,255,0.65);font-size:0.82em;line-height:1.5;margin:0;'>Dashboard auto-refreshes every 12 hours — team arrives to live intelligence daily</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── FOOTER ───────────────────────────────────────────────────
st.markdown(f"""
<div class='platform-footer'>
    <div>
        <div class='footer-logo'>DRE<span>MEL</span></div>
        <p class='footer-powered'>UK DIY Trend Intelligence Platform</p>
    </div>
    <div class='footer-meta'>
        YouTube Data API · Google Trends · VADER NLP · Gemini AI<br>
        {datetime.now().strftime('%d %b %Y  %H:%M')} · Auto-refreshes every 12 hours
    </div>
</div>
""", unsafe_allow_html=True)