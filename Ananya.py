# ============================================================
#  DREMEL — AI Trend Intelligence Dashboard
#  Install: pip install streamlit pandas matplotlib requests vaderSentiment google-generativeai
#  Run: streamlit run dremel_dashboard.py
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
    .main { background-color: #0A3D6B; }
    .stApp { background-color: #0A3D6B; }

    .dremel-header {
        background: linear-gradient(135deg, #0A3D6B 0%, #0F5CA8 100%);
        padding: 25px 30px;
        border-radius: 12px;
        margin-bottom: 20px;
        text-align: center;
        border-left: 6px solid #E8681A;
    }
    .dremel-header h1 {
        color: white;
        font-size: 2.2em;
        font-weight: 900;
        letter-spacing: 4px;
        margin: 0;
    }
    .dremel-header p {
        color: #A8C9E8;
        margin: 5px 0 0 0;
        font-size: 1em;
    }

    .metric-card {
        background: linear-gradient(135deg, #0F5CA8, #0A3D6B);
        border-radius: 10px;
        padding: 18px;
        text-align: center;
        border-top: 4px solid #E8681A;
        margin-bottom: 10px;
    }
    .metric-card h2 { color: white; font-size: 2em; margin: 0; font-weight: 900; }
    .metric-card p { color: #A8C9E8; margin: 5px 0 0 0; font-size: 0.85em; }

    .gap-card-red {
        background: #1a0a0a;
        border-left: 5px solid #E74C3C;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }
    .gap-card-green {
        background: #0a1a0a;
        border-left: 5px solid #2ECC71;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }
    .gap-card-red h4 { color: #E74C3C; margin: 0 0 4px 0; }
    .gap-card-green h4 { color: #2ECC71; margin: 0 0 4px 0; }
    .gap-card-red p, .gap-card-green p { color: #ccc; margin: 0; font-size: 0.85em; }

    .brief-box {
        background: #0D3A5C;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 10px;
        border-left: 4px solid #E8681A;
    }
    .brief-label {
        background: #0F5CA8;
        color: white;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.75em;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 6px;
    }
    .brief-value { color: white; font-size: 0.95em; margin: 0; }

    .stTabs [data-baseweb="tab"] {
        color: #A8C9E8;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        color: white;
        border-bottom: 3px solid #E8681A;
    }

    div[data-testid="stSidebarContent"] {
        background-color: #071F35;
    }

    .keyword-pill {
        display: inline-block;
        background: #0F5CA8;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        margin: 3px;
        font-size: 0.8em;
    }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ────────────────────────────────────────────────
API_KEY = "AIzaSyAtSS10C4ABESNKEt-vM0K6VSm7f06hD0c"
BASE_URL = "https://www.googleapis.com/youtube/v3/search"
STATS_URL = "https://www.googleapis.com/youtube/v3/videos"

DREMEL_BLUE = "#0F5CA8"
DREMEL_DARK = "#0A3D6B"
ORANGE = "#E8681A"

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


def load_or_scrape(keywords):
    files = glob.glob("dremel_trends_*.csv")
    if files:
        latest = max(files, key=os.path.getctime)
        df = pd.read_csv(latest)
        age = datetime.fromtimestamp(os.path.getctime(latest))
        return df, age
    return None, None


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


def generate_brief_gemini(trend, role, growth, product):
    try:
        import google.generativeai as genai
        genai.configure(api_key="YOUR_GEMINI_KEY_HERE")
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
You are a digital marketing expert for Dremel, a UK DIY tools brand.

Trend detected: {trend} (growth: {growth})
Role: {role}
Dremel product to feature: {product}

Generate a specific, actionable content brief for the {role}.
Include: hook, content idea, platform, format, CTA, hashtags, posting time.
Keep it concise and practical. Max 150 words.
"""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return None


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


# ════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🔧 DREMEL")
    st.markdown("**Trend Intelligence System**")
    st.markdown("---")

    st.markdown("**Select Keywords to Track**")
    selected_keywords = st.multiselect(
        "Keywords", KEYWORDS,
        default=KEYWORDS,
        label_visibility="collapsed",
        key="kw_select"
    )

    st.markdown("---")
    st.markdown("**Age Segment Filter**")
    age_filter = st.selectbox(
        "Age", ["All Ages"] + list(AGE_SEGMENTS.keys()),
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
        st.markdown(f"<small style='color:#A8C9E8'>{age.strftime('%d %b %Y, %H:%M')}</small>",
                    unsafe_allow_html=True)
    else:
        st.markdown("<small style='color:#E74C3C'>No data yet — click Refresh</small>",
                    unsafe_allow_html=True)

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
    .agg(avg_score=("trend_score", "mean"),
         avg_views=("views", "mean"),
         video_count=("video_id", "count"),
         dremel_present=("is_dremel", "any"))
    .sort_values("avg_score", ascending=False)
    .reset_index()
)

# ════════════════════════════════════════════════════════════
#  TOP METRICS
# ════════════════════════════════════════════════════════════
col1, col2, col3, col4 = st.columns(4)

top_trend = leaderboard.iloc[0]["keyword_clean"]
top_views = int(leaderboard["avg_views"].max())
gaps = len(leaderboard[~leaderboard["dremel_present"]])
total_videos = len(df)

with col1:
    st.markdown(f"""<div class='metric-card'>
        <h2>#{top_trend}</h2><p>Top Trending Topic</p></div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class='metric-card'>
        <h2>{top_views // 1_000_000}M</h2><p>Peak Avg Views</p></div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class='metric-card'>
        <h2>{gaps}/8</h2><p>Content Gaps Found</p></div>""", unsafe_allow_html=True)
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
        fig, ax = plt.subplots(figsize=(7, 5))
        fig.patch.set_facecolor("#0A3D6B")
        ax.set_facecolor("#0D3A5C")

        lb_sorted = leaderboard.sort_values("avg_score", ascending=True)
        colors = ["#2ECC71" if p else "#E74C3C" for p in lb_sorted["dremel_present"]]

        bars = ax.barh(lb_sorted["keyword_clean"], lb_sorted["avg_score"],
                       color=colors, edgecolor="none", height=0.6)

        for bar, val in zip(bars, lb_sorted["avg_score"]):
            ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                    f"{val:.2f}", va="center", color="white", fontsize=9, fontweight="bold")

        ax.set_title("Trend Score by Keyword", color="white", fontweight="bold", pad=12)
        ax.set_xlabel("Trend Score", color="#A8C9E8")
        ax.tick_params(colors="white", labelsize=8)
        ax.spines[:].set_visible(False)
        ax.set_xlim(0, lb_sorted["avg_score"].max() * 1.25)

        covered = mpatches.Patch(color="#2ECC71", label="Dremel Present")
        gap_p = mpatches.Patch(color="#E74C3C", label="GAP — Missing")
        ax.legend(handles=[covered, gap_p], facecolor="#0A3D6B",
                  edgecolor="none", labelcolor="white", fontsize=8)

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_b:
        fig2, ax2 = plt.subplots(figsize=(7, 5))
        fig2.patch.set_facecolor("#0A3D6B")
        ax2.set_facecolor("#0D3A5C")

        lb_views = leaderboard.sort_values("avg_views", ascending=True)
        colors2 = ["#2ECC71" if p else "#E8681A" for p in lb_views["dremel_present"]]

        bars2 = ax2.barh(lb_views["keyword_clean"],
                         lb_views["avg_views"] / 1_000_000,
                         color=colors2, edgecolor="none", height=0.6)

        for bar, val in zip(bars2, lb_views["avg_views"] / 1_000_000):
            ax2.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                     f"{val:.1f}M", va="center", color="white", fontsize=9, fontweight="bold")

        ax2.set_title("Average Views per Keyword", color="white", fontweight="bold", pad=12)
        ax2.set_xlabel("Avg Views (Millions)", color="#A8C9E8")
        ax2.tick_params(colors="white", labelsize=8)
        ax2.spines[:].set_visible(False)
        ax2.set_xlim(0, lb_views["avg_views"].max() / 1_000_000 * 1.3)

        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()

    # Table
    st.markdown("#### Full Leaderboard Table")
    display_lb = leaderboard.copy()
    display_lb["avg_views"] = display_lb["avg_views"].apply(lambda x: f"{int(x):,}")
    display_lb["avg_score"] = display_lb["avg_score"].apply(lambda x: f"{x:.2f}")
    display_lb["dremel_present"] = display_lb["dremel_present"].apply(
        lambda x: "✅ Yes" if x else "❌ GAP")
    display_lb.columns = ["Keyword", "Avg Score", "Avg Views", "Videos", "Dremel Present?"]
    st.dataframe(display_lb, use_container_width=True, hide_index=True)

# ── TAB 2: GAP ANALYSIS ──────────────────────────────────────
with tab2:
    st.markdown("### Gap Analysis — What Dremel Is Missing")
    st.markdown("*Red = Dremel has no content here. These are missed opportunities.*")

    col_g1, col_g2 = st.columns([3, 2])

    with col_g1:
        gaps_df = leaderboard.sort_values("avg_score", ascending=False)
        for _, row in gaps_df.iterrows():
            present = row["dremel_present"]
            card_class = "gap-card-green" if present else "gap-card-red"
            status = "✅ Dremel is present" if present else "❌ NO DREMEL CONTENT — CREATE NOW"
            action = "Maintain current posting frequency" if present else f"Immediate opportunity: {int(row['avg_views'] / 1e6):.0f}M avg views untapped"
            st.markdown(f"""
            <div class='{card_class}'>
                <h4>{row['keyword_clean']} — Score: {row['avg_score']:.2f}</h4>
                <p><strong>{status}</strong></p>
                <p>{action}</p>
            </div>
            """, unsafe_allow_html=True)

    with col_g2:
        st.markdown("#### Gap Summary")
        n_gaps = len(leaderboard[~leaderboard["dremel_present"]])
        n_covered = len(leaderboard[leaderboard["dremel_present"]])
        total_gap_views = leaderboard[~leaderboard["dremel_present"]]["avg_views"].sum()

        st.metric("Topics with NO Dremel content", f"{n_gaps} / {len(leaderboard)}")
        st.metric("Total untapped avg views", f"{int(total_gap_views / 1e6)}M+")
        st.metric("Topics Dremel covers", f"{n_covered}")

        st.markdown("---")
        st.markdown("**Top Priority Gap:**")
        top_gap = leaderboard[~leaderboard["dremel_present"]].iloc[0]
        st.markdown(f"""
        <div style='background:#1a0a0a; border-left:4px solid #E74C3C;
             border-radius:8px; padding:12px; margin-top:8px;'>
            <p style='color:#E74C3C; font-weight:bold; margin:0;'>
                {top_gap['keyword_clean']}</p>
            <p style='color:white; margin:4px 0 0 0; font-size:0.85em;'>
                Avg {int(top_gap['avg_views'] / 1e6)}M views · Score {top_gap['avg_score']:.2f}</p>
            <p style='color:#E8681A; margin:4px 0 0 0; font-size:0.8em;'>
                → Create content immediately</p>
        </div>""", unsafe_allow_html=True)

# ── TAB 3: TRENDING VIDEOS ───────────────────────────────────
with tab3:
    st.markdown("### Trending DIY Videos — UK YouTube")

    selected_kw = st.selectbox("Filter by keyword:", ["All"] + list(df["keyword_clean"].unique()))

    if selected_kw == "All":
        videos_df = df.sort_values("trend_score", ascending=False).head(20)
    else:
        videos_df = df[df["keyword_clean"] == selected_kw].sort_values(
            "trend_score", ascending=False).head(20)

    for _, row in videos_df.iterrows():
        dremel_badge = "🟢 DREMEL" if row["is_dremel"] else "🔴 Competitor/Creator"
        st.markdown(f"""
        <div style='background:#0D3A5C; border-radius:8px; padding:12px;
             margin-bottom:8px; border-left:3px solid {"#2ECC71" if row["is_dremel"] else "#E8681A"}'>
            <p style='color:white; font-weight:bold; margin:0; font-size:0.95em;'>
                {row['title'][:80]}...</p>
            <p style='color:#A8C9E8; margin:4px 0 0 0; font-size:0.8em;'>
                {row['channel']} · {int(row['views']):,} views ·
                Score: {row['trend_score']} · {dremel_badge}</p>
        </div>""", unsafe_allow_html=True)

# ── TAB 4: AI IDEATION CENTRE ────────────────────────────────
with tab4:
    st.markdown("### AI Ideation Centre")
    st.markdown("*Select a trend and your role — get a ready-to-use content brief instantly*")

    col_i1, col_i2, col_i3 = st.columns(3)

    with col_i1:
        selected_trend = st.selectbox(
            "Select Trending Topic:",
            leaderboard["keyword_clean"].tolist()
        )
    with col_i2:
        selected_role = st.selectbox(
            "Select Your Role:",
            list(ROLE_BRIEFS.keys())
        )
    with col_i3:
        dremel_products = [
            "Dremel 3000 Rotary Tool",
            "Dremel Lite 7760",
            "Dremel 4300",
            "Dremel Engraver 290",
            "Dremel Multi-Max MM40"
        ]
        selected_product = st.selectbox("Dremel Product to Feature:", dremel_products)

    generate_btn = st.button("Generate Content Brief", use_container_width=True)

    if generate_btn:
        trend_row = leaderboard[leaderboard["keyword_clean"] == selected_trend].iloc[0]
        growth = f"+{trend_row['avg_score']:.0f}% engagement score"

        st.markdown("---")
        st.markdown(f"#### Content Brief: **{selected_trend}** × **{selected_role}**")

        brief = generate_brief_template(selected_trend, selected_role, growth, selected_product)

        col_b1, col_b2 = st.columns(2)
        items = list(brief.items())
        half = len(items) // 2

        for label, value in items[:half]:
            with col_b1:
                st.markdown(f"""
                <div class='brief-box'>
                    <span class='brief-label'>{label}</span>
                    <p class='brief-value'>{value}</p>
                </div>""", unsafe_allow_html=True)

        for label, value in items[half:]:
            with col_b2:
                st.markdown(f"""
                <div class='brief-box'>
                    <span class='brief-label'>{label}</span>
                    <p class='brief-value'>{value}</p>
                </div>""", unsafe_allow_html=True)

        # Keyword → Sentence → Idea expansion
        st.markdown("---")
        st.markdown("#### Keyword → Sentence → Idea (Content Depth)")

        col_k1, col_k2, col_k3 = st.columns(3)
        with col_k1:
            st.markdown(f"""
            <div style='background:#0D3A5C; border-radius:8px; padding:14px;
                 border-top:3px solid #0F5CA8;'>
                <p style='color:#A8C9E8; font-size:0.8em; margin:0;'>LEVEL 1 — KEYWORD</p>
                <p style='color:white; font-weight:bold; margin:6px 0 0 0;'>
                    {selected_trend}</p>
            </div>""", unsafe_allow_html=True)
        with col_k2:
            st.markdown(f"""
            <div style='background:#0D3A5C; border-radius:8px; padding:14px;
                 border-top:3px solid #E8681A;'>
                <p style='color:#A8C9E8; font-size:0.8em; margin:0;'>LEVEL 2 — SEARCH INTENT</p>
                <p style='color:white; font-weight:bold; margin:6px 0 0 0;'>
                    "How to do {selected_trend.lower()} for beginners UK"</p>
            </div>""", unsafe_allow_html=True)
        with col_k3:
            st.markdown(f"""
            <div style='background:#0D3A5C; border-radius:8px; padding:14px;
                 border-top:3px solid #2ECC71;'>
                <p style='color:#A8C9E8; font-size:0.8em; margin:0;'>LEVEL 3 — CONTENT IDEA</p>
                <p style='color:white; font-weight:bold; margin:6px 0 0 0;'>
                    "I tried {selected_trend.lower()} using only a {selected_product} —
                    here is what happened"</p>
            </div>""", unsafe_allow_html=True)

# ── TAB 5: AUDIENCE SEGMENTS ─────────────────────────────────
with tab5:
    st.markdown("### Audience Segment Analysis")
    st.markdown("*Which age groups are most interested in each DIY trend*")

    for age, keywords in AGE_SEGMENTS.items():
        matching = [k for k in keywords if any(
            k.lower() in kw.lower() for kw in df["keyword"].unique()
        )]
        rel_df = df[df["keyword"].apply(
            lambda x: any(k in x.lower() for k in keywords)
        )]

        avg_views = int(rel_df["views"].mean()) if len(rel_df) > 0 else 0
        video_count = len(rel_df)

        st.markdown(f"""
        <div style='background:#0D3A5C; border-radius:10px; padding:16px;
             margin-bottom:12px; border-left:5px solid #0F5CA8;'>
            <h4 style='color:white; margin:0;'>{age}</h4>
            <p style='color:#A8C9E8; margin:6px 0; font-size:0.85em;'>
                Relevant keywords: {', '.join([f'<span class="keyword-pill">{k}</span>'
                                               for k in keywords])}
            </p>
            <p style='color:white; margin:4px 0; font-size:0.9em;'>
                Avg views in segment: <strong>{avg_views:,}</strong> ·
                Videos found: <strong>{video_count}</strong>
            </p>
        </div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    "<p style='color:#A8C9E8; text-align:center; font-size:0.8em;'>"
    "DREMEL Trend Intelligence System · Digital & Social Media Marketing · "
    f"Data refreshed: {datetime.now().strftime('%d %b %Y %H:%M')}</p>",
    unsafe_allow_html=True
)