# ============================================================
#  DREMEL — AI Trend Intelligence Dashboard
#  Install: pip install streamlit pandas matplotlib requests vaderSentiment google-generativeai
#  Run: streamlit run Ananya.py
# ============================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import requests
import glob
import os
import json
from datetime import datetime

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="Dremel Trend Intelligence",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Base app background ── */
    .stApp { background-color: #F7F8FA; }
    .main  { background-color: #F7F8FA; }

    /* ── Sidebar ── */
    div[data-testid="stSidebarContent"] {
        background-color: #1C1C2E;
    }
    div[data-testid="stSidebarContent"] * {
        color: #E2E8F0 !important;
    }
    div[data-testid="stSidebarContent"] .stButton > button {
        background-color: #E8681A;
        color: white !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 0;
        width: 100%;
        transition: background 0.2s;
    }
    div[data-testid="stSidebarContent"] .stButton > button:hover {
        background-color: #CF5A14;
    }

    /* ── Header ── */
    .dremel-header {
        background: #1C1C2E;
        padding: 28px 36px;
        border-radius: 14px;
        margin-bottom: 24px;
        text-align: center;
        border-left: 6px solid #E8681A;
    }
    .dremel-header h1 {
        color: #FFFFFF;
        font-size: 2em;
        font-weight: 900;
        letter-spacing: 6px;
        margin: 0;
    }
    .dremel-header p {
        color: #94A3B8;
        margin: 6px 0 0 0;
        font-size: 0.95em;
        letter-spacing: 0.5px;
    }

    /* ── Metric cards ── */
    .metric-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 20px 16px;
        text-align: center;
        border: 1px solid #E2E8F0;
        border-top: 4px solid #E8681A;
        margin-bottom: 10px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .metric-card h2 {
        color: #1C1C2E;
        font-size: 2em;
        margin: 0;
        font-weight: 800;
    }
    .metric-card p {
        color: #64748B;
        margin: 6px 0 0 0;
        font-size: 0.82em;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ── Gap cards ── */
    .gap-card-red {
        background: #FFF5F5;
        border-left: 5px solid #E53E3E;
        border-radius: 0 8px 8px 0;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .gap-card-green {
        background: #F0FFF4;
        border-left: 5px solid #38A169;
        border-radius: 0 8px 8px 0;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .gap-card-red h4 {
        color: #C53030;
        margin: 0 0 4px 0;
        font-size: 1em;
    }
    .gap-card-green h4 {
        color: #276749;
        margin: 0 0 4px 0;
        font-size: 1em;
    }
    .gap-card-red p, .gap-card-green p {
        color: #4A5568;
        margin: 2px 0 0 0;
        font-size: 0.85em;
    }

    /* ── Brief boxes ── */
    .brief-box {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #E8681A;
    }
    .brief-label {
        background: #1C1C2E;
        color: #E2E8F0;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.72em;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 6px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .brief-value {
        color: #1C1C2E;
        font-size: 0.92em;
        margin: 0;
        line-height: 1.5;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 4px;
        border: 1px solid #E2E8F0;
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #64748B;
        font-weight: 600;
        border-radius: 8px;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background: #1C1C2E !important;
        color: #FFFFFF !important;
    }

    /* ── Dataframe ── */
    .stDataFrame { border-radius: 10px; overflow: hidden; }

    /* ── Divider ── */
    hr { border-color: #E2E8F0; }

    /* ── Audience segment cards ── */
    .segment-card {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 16px 18px;
        margin-bottom: 12px;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #1C1C2E;
    }

    /* ── Video cards ── */
    .video-card-dremel {
        background: #F0FFF4;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border-left: 4px solid #38A169;
    }
    .video-card-other {
        background: #FFFFFF;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border-left: 4px solid #CBD5E0;
        border: 1px solid #E2E8F0;
    }

    /* ── Priority gap box ── */
    .priority-gap {
        background: #FFF5F5;
        border-left: 4px solid #E53E3E;
        border-radius: 0 8px 8px 0;
        padding: 14px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ────────────────────────────────────────────────
API_KEY = "AIzaSyAtSS10C4ABESNKEt-vM0K6VSm7f06hD0c"
BASE_URL = "https://www.googleapis.com/youtube/v3/search"
STATS_URL = "https://www.googleapis.com/youtube/v3/videos"

KEYWORDS = [
    "furniture flip UK",
    "DIY home UK",
    "rotary tool DIY",
    "dremel projects",
    "home engraving DIY",
    "cordless DIY tools UK",
    "upcycle furniture UK",
    "DIY craft UK"
]

AGE_SEGMENTS = {
    "18-24 (Gen Z)": ["furniture flip", "upcycle", "DIY craft", "aesthetic room", "thrift flip"],
    "25-34 (Millennials)": ["home renovation", "cordless tools", "DIY home", "first home DIY"],
    "35-44 (Gen X)": ["rotary tool", "engraving", "home remodeling", "workshop DIY"],
    "45+ (Boomers)": ["dremel projects", "precision tools", "woodworking", "garage DIY"]
}

ROLE_BRIEFS = {
    "Social Media Manager": {
        "platform": "YouTube Shorts + Instagram Reels",
        "format": "60-second before/after transformation",
        "hook_template": "POV: I found a £{price} {item} at a car boot sale and turned it into this",
        "cta": "Link in bio → Shop Dremel tools",
        "posting_time": "Thursday 6-8pm UK time",
        "creator_type": "UK micro-creator, 10k-80k followers, home decor niche"
    },
    "Content Manager": {
        "platform": "YouTube long-form + dremel.com blog",
        "format": "8-12 minute tutorial video",
        "hook_template": "Beginner's Guide to {trend} with Dremel — 5 Weekend Projects",
        "cta": "Subscribe + link to product page",
        "posting_time": "Tuesday or Wednesday morning",
        "creator_type": "In-house content team or brand partner creator"
    },
    "Email Marketing Manager": {
        "platform": "Email newsletter to UK subscribers",
        "format": "Trend-driven educational email with soft sell",
        "hook_template": "The {trend} revolution is here — are you ready to create?",
        "cta": "Shop Now button → relevant product page",
        "posting_time": "Tuesday 9am or Thursday 7pm UK",
        "creator_type": "Segment: UK subscribers who browsed related products in 60 days"
    },
    "Website Manager": {
        "platform": "dremel.com landing page + SEO blog",
        "format": "Trend landing page + how-to guide",
        "hook_template": "{trend} with Dremel — Everything You Need to Get Started",
        "cta": "Internal links to product pages + buy now",
        "posting_time": "Publish before trend peaks — within 48hrs of detection",
        "creator_type": "SEO-optimised content targeting UK search terms"
    },
    "E-commerce Manager": {
        "platform": "Amazon UK + dremel.com shop",
        "format": "Updated product listings + bundle creation",
        "hook_template": "Dremel {product} — Perfect for {trend} Projects",
        "cta": "Add to basket + sponsored PPC ad on trend keyword",
        "posting_time": "Update listings within 24hrs of trend detection",
        "creator_type": "A+ content with lifestyle images showing trend use case"
    },
    "Product Manager": {
        "platform": "Internal R&D + marketing strategy",
        "format": "Trend signal report for product team",
        "hook_template": "{trend} showing {growth}% growth — accessory gap identified",
        "cta": "Flag to R&D team + adjust product seeding budget",
        "posting_time": "Weekly Monday morning trend briefing",
        "creator_type": "Data-driven insight for product roadmap decisions"
    }
}

# ── Chart palette ─────────────────────────────────────────────
CHART_BG      = "#F7F8FA"
CHART_SURFACE = "#FFFFFF"
CHART_GREEN   = "#38A169"
CHART_RED     = "#E53E3E"
CHART_ORANGE  = "#E8681A"
CHART_DARK    = "#1C1C2E"
CHART_MUTED   = "#94A3B8"

# ── HELPER FUNCTIONS ─────────────────────────────────────────

@st.cache_data(ttl=3600)
def scrape_youtube(keyword, max_results=8):
    params = {
        "part": "snippet", "q": keyword, "type": "video",
        "regionCode": "GB", "relevanceLanguage": "en",
        "order": "viewCount", "maxResults": max_results,
        "publishedAfter": "2024-01-01T00:00:00Z", "key": API_KEY
    }
    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        data = r.json()
        if "error" in data:
            return []
        results = []
        for item in data.get("items", []):
            results.append({
                "keyword": keyword,
                "video_id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "published": item["snippet"]["publishedAt"][:10],
            })
        return results
    except:
        return []


@st.cache_data(ttl=3600)
def get_stats(video_ids_tuple):
    video_ids = list(video_ids_tuple)
    params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
    try:
        r = requests.get(STATS_URL, params=params, timeout=10)
        data = r.json()
        stats = {}
        for item in data.get("items", []):
            s = item.get("statistics", {})
            stats[item["id"]] = {
                "views": int(s.get("viewCount", 0)),
                "likes": int(s.get("likeCount", 0)),
                "comments": int(s.get("commentCount", 0))
            }
        return stats
    except:
        return {}


def trend_score(views, likes, comments):
    engagement = (likes + comments * 2) / max(views, 1) * 100
    size_score = min(views / 100000, 10)
    return round(engagement * 0.6 + size_score * 0.4, 2)


def scrape_all(keywords, progress_bar, status_text):
    all_videos = []
    for i, kw in enumerate(keywords):
        status_text.text(f"Searching: '{kw}'...")
        progress_bar.progress((i + 1) / len(keywords))
        videos = scrape_youtube(kw)
        if not videos:
            continue
        ids = tuple(v["video_id"] for v in videos)
        stats = get_stats(ids)
        for v in videos:
            s = stats.get(v["video_id"], {"views": 0, "likes": 0, "comments": 0})
            v.update(s)
            v["trend_score"] = trend_score(s["views"], s["likes"], s["comments"])
            all_videos.append(v)
    df = pd.DataFrame(all_videos)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    df.to_csv(f"dremel_trends_{timestamp}.csv", index=False)
    return df


def is_dremel(channel):
    return any(d.lower() in channel.lower() for d in ["dremel", "dremel europe", "dremel tools"])


def clean_label(kw):
    return {
        "furniture flip UK": "Furniture Flip",
        "DIY home UK": "DIY Home",
        "rotary tool DIY": "Rotary Tool",
        "dremel projects": "Dremel Projects",
        "home engraving DIY": "Home Engraving",
        "cordless DIY tools UK": "Cordless Tools",
        "upcycle furniture UK": "Upcycle Furniture",
        "DIY craft UK": "DIY Craft"
    }.get(kw, kw)


def generate_brief_template(trend, role, growth, product):
    r = ROLE_BRIEFS.get(role, ROLE_BRIEFS["Social Media Manager"])
    hook = r["hook_template"].replace("{trend}", trend).replace(
        "{growth}", str(growth)).replace("{product}", product).replace(
        "{price}", "15").replace("{item}", "dresser")
    return {
        "Hook": hook,
        "Platform": r["platform"],
        "Format": r["format"],
        "Product": product,
        "CTA": r["cta"],
        "Best Time to Post": r["posting_time"],
        "Creator Type": r["creator_type"],
        "Hashtags": f"#{trend.lower().replace(' ', '')} #DIYuk #dremel #upcycle #homedecor"
    }


def make_chart(lb_sorted, x_col, x_label, title, fmt_fn):
    fig, ax = plt.subplots(figsize=(7, 5))
    fig.patch.set_facecolor(CHART_BG)
    ax.set_facecolor(CHART_SURFACE)

    colors = [CHART_GREEN if p else CHART_RED for p in lb_sorted["dremel_present"]]
    vals = lb_sorted[x_col]

    bars = ax.barh(lb_sorted["keyword_clean"], vals, color=colors,
                   edgecolor="none", height=0.55)

    for bar, val in zip(bars, vals):
        ax.text(bar.get_width() + vals.max() * 0.02,
                bar.get_y() + bar.get_height() / 2,
                fmt_fn(val), va="center", color=CHART_DARK,
                fontsize=9, fontweight="600")

    ax.set_title(title, color=CHART_DARK, fontweight="bold", pad=14, fontsize=11)
    ax.set_xlabel(x_label, color=CHART_MUTED, fontsize=9)
    ax.tick_params(colors=CHART_DARK, labelsize=8)
    ax.spines[:].set_visible(False)
    ax.set_xlim(0, vals.max() * 1.28)
    ax.xaxis.label.set_color(CHART_MUTED)
    ax.tick_params(axis="x", colors=CHART_MUTED)

    covered = mpatches.Patch(color=CHART_GREEN, label="Dremel Present")
    gap_p   = mpatches.Patch(color=CHART_RED,   label="Gap — Missing")
    ax.legend(handles=[covered, gap_p], facecolor=CHART_SURFACE,
              edgecolor="#E2E8F0", labelcolor=CHART_DARK, fontsize=8,
              framealpha=1)

    plt.tight_layout()
    return fig


# ════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🔧 DREMEL")
    st.markdown("**Trend Intelligence System**")
    st.markdown("---")

    st.markdown("**Select Keywords to Track**")
    selected_keywords = st.multiselect(
        "Keywords",
        KEYWORDS,
        default=KEYWORDS,
        label_visibility="collapsed",
        key="kw_select"
    )

    st.markdown("---")
    st.markdown("**Age Segment Filter**")
    age_filter = st.selectbox(
        "Age Segment",
        ["All Ages"] + list(AGE_SEGMENTS.keys()),
        label_visibility="collapsed",
        key="age_select"
    )

    st.markdown("---")
    run_scrape = st.button("🔄 Refresh Data from YouTube", use_container_width=True)

    st.markdown("---")
    st.markdown("**Last Updated**")
    files = glob.glob("dremel_trends_*.csv")
    if files:
        latest = max(files, key=os.path.getctime)
        age = datetime.fromtimestamp(os.path.getctime(latest))
        st.markdown(
            f"<small style='color:#94A3B8'>{age.strftime('%d %b %Y, %H:%M')}</small>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<small style='color:#FC8181'>No data yet — click Refresh</small>",
            unsafe_allow_html=True
        )

# ════════════════════════════════════════════════════════════
#  HEADER
# ════════════════════════════════════════════════════════════
st.markdown("""
<div class='dremel-header'>
    <h1>DREMEL</h1>
    <p>AI-Powered UK DIY Trend Intelligence Dashboard</p>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  LOAD DATA
# ════════════════════════════════════════════════════════════
df = None

if run_scrape or not glob.glob("dremel_trends_*.csv"):
    st.markdown("### Scraping YouTube UK...")
    progress = st.progress(0)
    status = st.empty()
    df = scrape_all(selected_keywords, progress, status)
    progress.empty()
    status.empty()
    st.success(f"Done! {len(df)} videos analysed.")
else:
    files = glob.glob("dremel_trends_*.csv")
    if files:
        latest = max(files, key=os.path.getctime)
        df = pd.read_csv(latest)

if df is None or len(df) == 0:
    st.warning("No data loaded. Click 'Refresh Data from YouTube' in the sidebar.")
    st.stop()

# Clean
df["keyword_clean"] = df["keyword"].apply(clean_label)
df["is_dremel"] = df["channel"].apply(is_dremel)

# Age filter
if age_filter != "All Ages":
    age_kws = AGE_SEGMENTS[age_filter]
    df_filtered = df[df["keyword"].apply(
        lambda x: any(ak in x.lower() for ak in age_kws)
    )]
    if len(df_filtered) > 0:
        df = df_filtered

# Leaderboard
leaderboard = (
    df.groupby("keyword_clean")
    .agg(
        avg_score=("trend_score", "mean"),
        avg_views=("views", "mean"),
        video_count=("video_id", "count"),
        dremel_present=("is_dremel", "any")
    )
    .sort_values("avg_score", ascending=False)
    .reset_index()
)

# ════════════════════════════════════════════════════════════
#  TOP METRICS
# ════════════════════════════════════════════════════════════
col1, col2, col3, col4 = st.columns(4)

top_trend    = leaderboard.iloc[0]["keyword_clean"]
top_views    = int(leaderboard["avg_views"].max())
gaps         = len(leaderboard[~leaderboard["dremel_present"]])
total_videos = len(df)

with col1:
    st.markdown(f"""<div class='metric-card'>
        <h2>{top_trend}</h2><p>Top Trending Topic</p></div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class='metric-card'>
        <h2>{top_views // 1_000_000}M+</h2><p>Peak Avg Views</p></div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class='metric-card'>
        <h2>{gaps} / 8</h2><p>Content Gaps Found</p></div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class='metric-card'>
        <h2>{total_videos}</h2><p>Videos Analysed</p></div>""", unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════════════════════════════════
#  TABS
# ════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Trend Leaderboard",
    "🔴 Gap Analysis",
    "🎬 Trending Videos",
    "💡 AI Ideation Centre",
    "👥 Audience Segments"
])

# ── TAB 1: TREND LEADERBOARD ─────────────────────────────────
with tab1:
    st.markdown("### UK DIY Trend Leaderboard")
    st.markdown("*Ranked by engagement score — how fast each topic is growing*")

    col_a, col_b = st.columns(2)

    with col_a:
        lb_score = leaderboard.sort_values("avg_score", ascending=True)
        fig1 = make_chart(
            lb_score, "avg_score", "Trend Score",
            "Trend Score by Keyword",
            lambda v: f"{v:.2f}"
        )
        st.pyplot(fig1)
        plt.close()

    with col_b:
        lb_views = leaderboard.sort_values("avg_views", ascending=True).copy()
        lb_views["avg_views_m"] = lb_views["avg_views"] / 1_000_000
        fig2 = make_chart(
            lb_views, "avg_views_m", "Avg Views (Millions)",
            "Average Views per Keyword",
            lambda v: f"{v:.1f}M"
        )
        st.pyplot(fig2)
        plt.close()

    st.markdown("#### Full Leaderboard Table")
    display_lb = leaderboard.copy()
    display_lb["avg_views"] = display_lb["avg_views"].apply(lambda x: f"{int(x):,}")
    display_lb["avg_score"] = display_lb["avg_score"].apply(lambda x: f"{x:.2f}")
    display_lb["dremel_present"] = display_lb["dremel_present"].apply(
        lambda x: "✅ Yes" if x else "❌ Gap"
    )
    display_lb.columns = ["Keyword", "Avg Score", "Avg Views", "Videos", "Dremel Present?"]
    st.dataframe(display_lb, width="stretch", hide_index=True)

# ── TAB 2: GAP ANALYSIS ──────────────────────────────────────
with tab2:
    st.markdown("### Gap Analysis — What Dremel Is Missing")
    st.markdown("*Red = Dremel has no content here. These are missed opportunities.*")

    col_g1, col_g2 = st.columns([3, 2])

    with col_g1:
        gaps_df = leaderboard.sort_values("avg_score", ascending=False)
        for _, row in gaps_df.iterrows():
            present    = row["dremel_present"]
            card_class = "gap-card-green" if present else "gap-card-red"
            status     = "✅ Dremel is present" if present else "❌ NO DREMEL CONTENT — CREATE NOW"
            action     = (
                "Maintain current posting frequency" if present
                else f"Immediate opportunity: {int(row['avg_views'] / 1e6):.0f}M avg views untapped"
            )
            st.markdown(f"""
            <div class='{card_class}'>
                <h4>{row['keyword_clean']} — Score: {row['avg_score']:.2f}</h4>
                <p><strong>{status}</strong></p>
                <p>{action}</p>
            </div>""", unsafe_allow_html=True)

    with col_g2:
        st.markdown("#### Gap Summary")
        n_gaps        = len(leaderboard[~leaderboard["dremel_present"]])
        n_covered     = len(leaderboard[leaderboard["dremel_present"]])
        total_gap_views = leaderboard[~leaderboard["dremel_present"]]["avg_views"].sum()

        st.metric("Topics with NO Dremel content", f"{n_gaps} / {len(leaderboard)}")
        st.metric("Total untapped avg views",       f"{int(total_gap_views / 1e6)}M+")
        st.metric("Topics Dremel covers",           f"{n_covered}")

        st.markdown("---")
        st.markdown("**Top Priority Gap:**")
        top_gap = leaderboard[~leaderboard["dremel_present"]].iloc[0]
        st.markdown(f"""
        <div class='priority-gap'>
            <p style='color:#C53030; font-weight:700; margin:0; font-size:1em;'>
                {top_gap['keyword_clean']}</p>
            <p style='color:#4A5568; margin:5px 0 0 0; font-size:0.85em;'>
                Avg {int(top_gap['avg_views'] / 1e6)}M views · Score {top_gap['avg_score']:.2f}</p>
            <p style='color:#E8681A; margin:5px 0 0 0; font-size:0.82em; font-weight:600;'>
                → Create content immediately</p>
        </div>""", unsafe_allow_html=True)

# ── TAB 3: TRENDING VIDEOS ───────────────────────────────────
with tab3:
    st.markdown("### Trending DIY Videos — UK YouTube")

    selected_kw = st.selectbox(
        "Filter by keyword:",
        ["All"] + list(df["keyword_clean"].unique()),
        key="video_kw_filter"
    )

    videos_df = (
        df.sort_values("trend_score", ascending=False).head(20)
        if selected_kw == "All"
        else df[df["keyword_clean"] == selected_kw]
            .sort_values("trend_score", ascending=False).head(20)
    )

    for _, row in videos_df.iterrows():
        dremel_badge = "🟢 DREMEL" if row["is_dremel"] else "⬜ Competitor / Creator"
        card_class   = "video-card-dremel" if row["is_dremel"] else "video-card-other"
        title_color  = "#276749" if row["is_dremel"] else "#1C1C2E"
        st.markdown(f"""
        <div class='{card_class}'>
            <p style='color:{title_color}; font-weight:600; margin:0; font-size:0.93em;'>
                {row['title'][:85]}...</p>
            <p style='color:#64748B; margin:5px 0 0 0; font-size:0.8em;'>
                {row['channel']} &nbsp;·&nbsp; {int(row['views']):,} views &nbsp;·&nbsp;
                Score: {row['trend_score']} &nbsp;·&nbsp; {dremel_badge}</p>
        </div>""", unsafe_allow_html=True)

# ── TAB 4: AI IDEATION CENTRE ────────────────────────────────
with tab4:
    st.markdown("### AI Ideation Centre")
    st.markdown("*Select a trend and your role — get a ready-to-use content brief instantly*")

    col_i1, col_i2, col_i3 = st.columns(3)

    with col_i1:
        selected_trend = st.selectbox(
            "Trending Topic:",
            leaderboard["keyword_clean"].tolist(),
            key="ideation_trend"
        )
    with col_i2:
        selected_role = st.selectbox(
            "Your Role:",
            list(ROLE_BRIEFS.keys()),
            key="ideation_role"
        )
    with col_i3:
        dremel_products = [
            "Dremel 3000 Rotary Tool",
            "Dremel Lite 7760",
            "Dremel 4300",
            "Dremel Engraver 290",
            "Dremel Multi-Max MM40"
        ]
        selected_product = st.selectbox(
            "Dremel Product:",
            dremel_products,
            key="ideation_product"
        )

    generate_btn = st.button("Generate Content Brief", use_container_width=True)

    if generate_btn:
        trend_row = leaderboard[leaderboard["keyword_clean"] == selected_trend].iloc[0]
        growth    = f"+{trend_row['avg_score']:.0f}% engagement score"

        st.markdown("---")
        st.markdown(f"#### Content Brief: **{selected_trend}** × **{selected_role}**")

        brief = generate_brief_template(selected_trend, selected_role, growth, selected_product)

        col_b1, col_b2 = st.columns(2)
        items = list(brief.items())
        half  = len(items) // 2

        for label, value in items[:half]:
            col_b1.markdown(f"""
            <div class='brief-box'>
                <span class='brief-label'>{label}</span>
                <p class='brief-value'>{value}</p>
            </div>""", unsafe_allow_html=True)

        for label, value in items[half:]:
            col_b2.markdown(f"""
            <div class='brief-box'>
                <span class='brief-label'>{label}</span>
                <p class='brief-value'>{value}</p>
            </div>""", unsafe_allow_html=True)

        # Keyword → Sentence → Idea
        st.markdown("---")
        st.markdown("#### Keyword → Sentence → Idea")

        col_k1, col_k2, col_k3 = st.columns(3)

        def depth_card(label, border_color, label_color, body):
            return f"""
            <div style='background:#FFFFFF; border-radius:10px; padding:16px;
                 border:1px solid #E2E8F0; border-top:4px solid {border_color};'>
                <p style='color:{label_color}; font-size:0.72em; font-weight:700;
                     margin:0; text-transform:uppercase; letter-spacing:0.5px;'>{label}</p>
                <p style='color:#1C1C2E; font-weight:600; margin:8px 0 0 0;
                     font-size:0.9em; line-height:1.5;'>{body}</p>
            </div>"""

        with col_k1:
            st.markdown(depth_card(
                "Level 1 — Keyword", "#1C1C2E", "#64748B",
                selected_trend
            ), unsafe_allow_html=True)
        with col_k2:
            st.markdown(depth_card(
                "Level 2 — Search Intent", "#E8681A", "#E8681A",
                f"How to do {selected_trend.lower()} for beginners UK"
            ), unsafe_allow_html=True)
        with col_k3:
            st.markdown(depth_card(
                "Level 3 — Content Idea", "#38A169", "#38A169",
                f"I tried {selected_trend.lower()} using only a {selected_product} — here's what happened"
            ), unsafe_allow_html=True)

# ── TAB 5: AUDIENCE SEGMENTS ─────────────────────────────────
with tab5:
    st.markdown("### Audience Segment Analysis")
    st.markdown("*Which age groups are most interested in each DIY trend*")

    for age, keywords in AGE_SEGMENTS.items():
        rel_df    = df[df["keyword"].apply(lambda x: any(k in x.lower() for k in keywords))]
        avg_views = int(rel_df["views"].mean()) if len(rel_df) > 0 else 0
        vid_count = len(rel_df)

        pills = " ".join([
            f"<span style='background:#EDF2F7; color:#2D3748; padding:3px 10px; "
            f"border-radius:20px; font-size:0.78em; font-weight:500; "
            f"margin:2px; display:inline-block;'>{k}</span>"
            for k in keywords
        ])

        st.markdown(f"""
        <div class='segment-card'>
            <h4 style='color:#1C1C2E; margin:0 0 8px 0;'>{age}</h4>
            <div style='margin-bottom:8px;'>{pills}</div>
            <p style='color:#4A5568; margin:0; font-size:0.88em;'>
                Avg views in segment: <strong>{avg_views:,}</strong> &nbsp;·&nbsp;
                Videos found: <strong>{vid_count}</strong>
            </p>
        </div>""", unsafe_allow_html=True)

# ── FOOTER ───────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='color:#94A3B8; text-align:center; font-size:0.78em;'>"
    "DREMEL Trend Intelligence System &nbsp;·&nbsp; Digital & Social Media Marketing &nbsp;·&nbsp; "
    f"Data refreshed: {datetime.now().strftime('%d %b %Y %H:%M')}</p>",
    unsafe_allow_html=True
)