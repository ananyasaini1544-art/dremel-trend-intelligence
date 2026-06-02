# ============================================================
#  DREMEL — Multi-Platform AI Trend Intelligence Dashboard
#  Install: pip install streamlit pandas matplotlib requests
#           vaderSentiment pytrends google-generativeai
#           python-docx python-dotenv
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
    page_title="Dremel Multi-Platform Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY",  "")

BASE_URL     = "https://www.googleapis.com/youtube/v3/search"
STATS_URL    = "https://www.googleapis.com/youtube/v3/videos"
COMMENTS_URL = "https://www.googleapis.com/youtube/v3/commentThreads"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');
html,body,.stApp{background:#0F0F13;font-family:'DM Sans',sans-serif;}
.main{background:#0F0F13;}
div[data-testid="stSidebarContent"]{background:#16161E;border-right:1px solid #2A2A3A;}
div[data-testid="stSidebarContent"] p,
div[data-testid="stSidebarContent"] label,
div[data-testid="stSidebarContent"] span,
div[data-testid="stSidebarContent"] div{color:#C8C8D8!important;}
div[data-testid="stSidebarContent"] .stButton>button{
  background:#FF4D00;color:white!important;border:none;border-radius:8px;
  font-weight:700;padding:10px 0;width:100%;}
.hero{background:#16161E;border:1px solid #2A2A3A;border-radius:16px;padding:28px 36px;margin-bottom:24px;}
.hero h1{font-family:'Syne',sans-serif;font-size:2.2em;font-weight:800;color:#FFF;margin:0;letter-spacing:3px;}
.hero p{color:#6B6B8A;margin:6px 0 0 0;font-size:0.88em;}
.hero-badge{background:#FF4D00;color:white;padding:6px 16px;border-radius:24px;
            font-size:0.75em;font-weight:700;float:right;margin-top:-36px;}
.metric-card{background:#16161E;border:1px solid #2A2A3A;border-radius:12px;
             padding:18px 14px;text-align:center;border-top:3px solid #FF4D00;}
.metric-card h2{font-family:'Syne',sans-serif;color:#FFF;font-size:1.8em;margin:6px 0 0 0;font-weight:800;}
.metric-card p{color:#6B6B8A;margin:4px 0 0 0;font-size:0.75em;text-transform:uppercase;letter-spacing:1px;}
.dark-card{background:#16161E;border:1px solid #2A2A3A;border-radius:10px;padding:14px 16px;margin-bottom:8px;}
.dark-card h4{font-family:'Syne',sans-serif;color:#FFF;margin:0 0 5px 0;font-size:0.95em;}
.dark-card p{color:#8888AA;margin:0;font-size:0.82em;line-height:1.5;}
.gap-red{background:#1E0A0A;border-left:5px solid #FF3B3B;border-radius:0 10px 10px 0;padding:13px 16px;margin-bottom:8px;}
.gap-green{background:#0A1E0A;border-left:5px solid #00C46A;border-radius:0 10px 10px 0;padding:13px 16px;margin-bottom:8px;}
.gap-red h4{color:#FF6B6B;margin:0 0 4px 0;font-family:'Syne',sans-serif;font-size:0.95em;}
.gap-green h4{color:#00C46A;margin:0 0 4px 0;font-family:'Syne',sans-serif;font-size:0.95em;}
.gap-red p,.gap-green p{color:#8888AA;margin:2px 0 0 0;font-size:0.82em;}
.brief-box{background:#16161E;border:1px solid #2A2A3A;border-left:4px solid #FF4D00;
           border-radius:0 10px 10px 0;padding:13px 15px;margin-bottom:8px;}
.brief-label{background:#FF4D00;color:white;padding:2px 9px;border-radius:4px;
             font-size:0.68em;font-weight:700;letter-spacing:1px;text-transform:uppercase;
             display:inline-block;margin-bottom:5px;}
.brief-value{color:#E0E0F0;font-size:0.88em;margin:0;line-height:1.5;}
.sent-pos{background:#1A3A2A;border-left:4px solid #00C46A;border-radius:0 8px 8px 0;padding:11px 14px;margin-bottom:7px;}
.sent-neu{background:#1A1A2A;border-left:4px solid #4A90D9;border-radius:0 8px 8px 0;padding:11px 14px;margin-bottom:7px;}
.sent-neg{background:#3A1A1A;border-left:4px solid #FF3B3B;border-radius:0 8px 8px 0;padding:11px 14px;margin-bottom:7px;}
.live-badge{background:#00C46A;color:white;padding:3px 10px;border-radius:20px;
            font-size:0.72em;font-weight:700;display:inline-block;margin-left:8px;}
.next-card{background:#16161E;border:1px solid #2A2A3A;border-top:3px solid #FF8C00;
           border-radius:10px;padding:14px;margin-bottom:8px;}
.next-card h4{font-family:'Syne',sans-serif;color:#FF8C00;margin:0 0 5px 0;font-size:0.92em;}
.next-card p{color:#8888AA;margin:0;font-size:0.82em;line-height:1.5;}
.stTabs [data-baseweb="tab-list"]{background:#16161E;border-radius:10px;padding:3px;border:1px solid #2A2A3A;gap:2px;}
.stTabs [data-baseweb="tab"]{color:#6B6B8A;font-weight:600;border-radius:8px;padding:7px 13px;}
.stTabs [aria-selected="true"]{background:#FF4D00!important;color:white!important;}
hr{border-color:#2A2A3A;}
.section-title{font-family:'Syne',sans-serif;color:#FFF;font-size:1.25em;font-weight:700;margin:0 0 3px 0;}
.section-sub{color:#6B6B8A;font-size:0.83em;margin-bottom:14px;}
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
ROLES = ["Social Media Manager", "Content Manager", "Email Marketing Manager", "E-Commerce Manager"]
NEXT_ACTIONS = [
    {"title": "Week 1 — Keyword Auto-Expansion",
     "detail": "Use YouTube autocomplete to expand 10 keywords into 50+ automatically.",
     "effort": "Low", "impact": "High"},
    {"title": "Week 2 — VADER on Live Comments",
     "detail": "Scrape real YouTube comments per video and run VADER on each one.",
     "effort": "Medium", "impact": "High"},
    {"title": "Week 3 — Whisper Transcription",
     "detail": "Auto-download top video audio with yt-dlp and transcribe with OpenAI Whisper.",
     "effort": "Medium", "impact": "Very High"},
    {"title": "Week 4 — Monday Email Automation",
     "detail": "Auto-email role-specific briefs to all 6 marketing managers every Monday 8am.",
     "effort": "Low", "impact": "Very High"},
    {"title": "Week 5 — Competitor Alert System",
     "detail": "Trigger alert when a competitor posts on a keyword where Dremel is absent.",
     "effort": "Medium", "impact": "High"},
    {"title": "Week 6 — Unified Platform Score",
     "detail": "Combine YouTube + Google Trends into one cross-platform momentum score.",
     "effort": "High", "impact": "Very High"},
]
CHART_BG = "#0F0F13"; CHART_SURF = "#16161E"; CHART_TEXT = "#C8C8D8"; CHART_MUT = "#4A4A6A"

# ── HELPERS ──────────────────────────────────────────────────
def dark_chart(figsize=(7, 5)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(CHART_BG); ax.set_facecolor(CHART_SURF)
    ax.tick_params(colors=CHART_TEXT, labelsize=8)
    for s in ax.spines.values(): s.set_visible(False)
    return fig, ax

def clean_label(kw): return KEYWORD_LABELS.get(kw, kw)
def is_dremel(ch): return any(d.lower() in str(ch).lower() for d in ["dremel", "dremel europe", "dremel tools"])
def calc_score(v, l, c): return round(((l + c*2)/max(v,1)*100)*0.6 + min(v/100000,10)*0.4, 2)
def should_refresh():
    files = glob.glob("dremel_multi_*.csv")
    if not files: return True
    return time.time() - os.path.getctime(max(files, key=os.path.getctime)) > 43200

# ── YOUTUBE ──────────────────────────────────────────────────
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

# ── VADER ────────────────────────────────────────────────────
@st.cache_data(ttl=21600)
def get_sentiment(kw, vid_ids):
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        comments = []
        for v in list(vid_ids)[:3]: comments.extend(get_comments(v, 10))
        if not comments: return {"Positive":50,"Neutral":35,"Negative":15,"sample_size":0}
        pos=neu=neg=0
        for c in comments:
            sc = analyzer.polarity_scores(c)["compound"]
            if sc >= 0.05: pos+=1
            elif sc <= -0.05: neg+=1
            else: neu+=1
        t = len(comments)
        return {"Positive":round(pos/t*100),"Neutral":round(neu/t*100),"Negative":round(neg/t*100),"sample_size":t}
    except: return {"Positive":50,"Neutral":35,"Negative":15,"sample_size":0}

# ── GOOGLE TRENDS ────────────────────────────────────────────
@st.cache_data(ttl=21600)
def get_trends(kw):
    try:
        from pytrends.request import TrendReq
        pt = TrendReq(hl="en-GB", tz=0, timeout=(10,25))
        pt.build_payload([kw], cat=0, timeframe="today 3-m", geo="GB")
        df = pt.interest_over_time()
        if df.empty: return {"current":50,"growth":0,"peak":50}
        vals = df[kw].tolist()
        cur  = vals[-1]; prev = vals[-5] if len(vals)>=5 else vals[0]
        return {"current":int(cur),"growth":round(((cur-prev)/max(prev,1))*100,1),"peak":int(max(vals))}
    except: return {"current":50,"growth":0,"peak":50}

# ── GEMINI AI ────────────────────────────────────────────────
def generate_ai_brief(trend, role, product, score, growth):
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        resp  = model.generate_content(f"""
You are a senior digital marketing strategist for Dremel UK, a DIY power tools brand.
LIVE DATA: Trend={trend}, UK Growth={growth}%, Score={score}, Product={product}, Role={role}
Generate a specific actionable content brief. Return EXACTLY this format, no extra text:
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
        st.error(f"Gemini error: {e}"); return None

# ── DOCX ─────────────────────────────────────────────────────
def make_docx(trend, role, product, brief, ideas):
    try:
        from docx import Document
        doc = Document()
        doc.add_heading("DREMEL — AI Content Brief", 0)
        doc.add_heading(f"Trend: {trend}  |  Role: {role}", 1)
        doc.add_paragraph(f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}")
        doc.add_paragraph(f"Product: {product}")
        doc.add_heading("AI Brief", 2)
        for k, v in brief:
            p = doc.add_paragraph(); p.add_run(f"{k}: ").bold = True; p.add_run(str(v))
        doc.add_heading("Video Ideas", 2)
        for idea in ideas: doc.add_paragraph(f"• {idea}", style="List Bullet")
        doc.add_heading("Keyword Expansion", 2)
        doc.add_paragraph(f"Keyword:       {trend}")
        doc.add_paragraph(f"Search Intent: How to do {trend.lower()} for beginners UK 2025")
        doc.add_paragraph(f"Content Idea:  I tried {trend.lower()} using only a {product}")
        buf = BytesIO(); doc.save(buf); buf.seek(0); return buf
    except: return None

# ── SCRAPE ALL ────────────────────────────────────────────────
def scrape_all(keywords, prog, status):
    all_v = []
    for i, kw in enumerate(keywords):
        status.text(f"Scraping: '{kw}'...")
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
    st.markdown("### DREMEL"); st.markdown("**Multi-Platform AI Intelligence**"); st.markdown("---")
    st.markdown("**Keywords to Track**")
    selected_keywords = st.multiselect("KW", KEYWORDS, default=KEYWORDS, label_visibility="collapsed", key="kw_main")
    st.markdown("---"); st.markdown("**Age Segment Filter**")
    age_filter = st.selectbox("Age", ["All Ages"]+list(AGE_SEGMENTS.keys()), label_visibility="collapsed", key="age_main")
    st.markdown("---")
    run_scrape = st.button("Refresh Data from YouTube", use_container_width=True)
    st.markdown("---")
    files = glob.glob("dremel_multi_*.csv")
    if files:
        fa = datetime.fromtimestamp(os.path.getctime(max(files, key=os.path.getctime)))
        st.markdown(f"<small style='color:#6B6B8A'>Last: {fa.strftime('%d %b %Y %H:%M')}</small>", unsafe_allow_html=True)
        if (datetime.now()-fa).seconds//3600 >= 11:
            st.markdown("<small style='color:#FF8C00'>Auto-refresh due soon</small>", unsafe_allow_html=True)
    else:
        st.markdown("<small style='color:#FF6B6B'>No data — click Refresh</small>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<small style='color:#4A4A6A'>Auto-refreshes every 12 hours</small>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  HERO
# ════════════════════════════════════════════════════════════
auto_ref = should_refresh()
st.markdown(f"""
<div class='hero'>
  <h1>DREMEL</h1>
  <p>Multi-Platform AI Intelligence · YouTube · Google Trends · Gemini AI · VADER Sentiment</p>
  <span class='hero-badge'>{'LIVE — AUTO REFRESHING' if auto_ref else 'LIVE INTELLIGENCE'}</span>
</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  LOAD DATA
# ════════════════════════════════════════════════════════════
df = None
if run_scrape or auto_ref or not glob.glob("dremel_multi_*.csv"):
    if auto_ref and not run_scrape: st.info("Auto-refreshing (12-hour cycle)...")
    prog = st.progress(0); status = st.empty()
    df   = scrape_all(selected_keywords, prog, status)
    prog.empty(); status.empty()
    st.success(f"Done! {len(df)} videos analysed from YouTube UK.")
else:
    files = glob.glob("dremel_multi_*.csv")
    if files: df = pd.read_csv(max(files, key=os.path.getctime))

if df is None or len(df) == 0:
    st.warning("No data — click Refresh in the sidebar."); st.stop()

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
#  METRICS
# ════════════════════════════════════════════════════════════
c1,c2,c3,c4,c5 = st.columns(5)
tt = leaderboard.iloc[0]["keyword_clean"]
pv = int(leaderboard["avg_views"].max())
gp = len(leaderboard[~leaderboard["dremel_present"]])
for col,val,lbl in zip([c1,c2,c3,c4,c5],
    [tt, f"{pv//1_000_000}M+", f"{gp}/{len(leaderboard)}", len(df), "4 Real Sources"],
    ["Top Trend","Peak Avg Views","Content Gaps","Videos Analysed","Data Sources"]):
    col.markdown(f"<div class='metric-card'><h2>{val}</h2><p>{lbl}</p></div>", unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════════════════════════════════
#  TABS
# ════════════════════════════════════════════════════════════
tab1,tab2,tab3,tab4,tab5,tab6,tab7 = st.tabs([
    "📊 Trend Leaderboard","📈 Google Trends","💬 Sentiment",
    "🔴 Gap Analysis","🎬 Trending Videos","💡 AI Ideation & Briefs","🗺️ Next Actions"
])

# TAB 1 — LEADERBOARD
with tab1:
    st.markdown("<p class='section-title'>UK DIY Trend Leaderboard</p>", unsafe_allow_html=True)
    st.markdown("<p class='section-sub'>Real YouTube data — ranked by engagement score</p>", unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        fig,ax = dark_chart()
        lb = leaderboard.sort_values("avg_score", ascending=True)
        cols = ["#00C46A" if p else "#FF3B3B" for p in lb["dremel_present"]]
        bars = ax.barh(lb["keyword_clean"], lb["avg_score"], color=cols, edgecolor="none", height=0.55)
        for bar,val in zip(bars, lb["avg_score"]):
            ax.text(bar.get_width()+0.05, bar.get_y()+bar.get_height()/2, f"{val:.2f}", va="center", color=CHART_TEXT, fontsize=9, fontweight="bold")
        ax.set_title("Trend Score by Keyword", color=CHART_TEXT, fontweight="bold", pad=12, fontsize=11)
        ax.set_xlabel("Trend Score", color=CHART_MUT, fontsize=9); ax.xaxis.label.set_color(CHART_MUT)
        ax.tick_params(axis="x", colors=CHART_MUT); ax.set_xlim(0, lb["avg_score"].max()*1.28)
        ax.legend(handles=[mpatches.Patch(color="#00C46A",label="Dremel Present"),
                           mpatches.Patch(color="#FF3B3B",label="Gap")],
                  facecolor=CHART_SURF, edgecolor="#2A2A3A", labelcolor=CHART_TEXT, fontsize=8)
        plt.tight_layout(); st.pyplot(fig); plt.close()
    with cb:
        fig2,ax2 = dark_chart()
        lv = leaderboard.sort_values("avg_views", ascending=True)
        cols2 = ["#00C46A" if p else "#FF4D00" for p in lv["dremel_present"]]
        vals = lv["avg_views"]/1_000_000
        bars2 = ax2.barh(lv["keyword_clean"], vals, color=cols2, edgecolor="none", height=0.55)
        for bar,val in zip(bars2, vals):
            ax2.text(bar.get_width()+0.3, bar.get_y()+bar.get_height()/2, f"{val:.1f}M", va="center", color=CHART_TEXT, fontsize=9, fontweight="bold")
        ax2.set_title("Average Views per Keyword", color=CHART_TEXT, fontweight="bold", pad=12, fontsize=11)
        ax2.set_xlabel("Avg Views (M)", color=CHART_MUT, fontsize=9); ax2.xaxis.label.set_color(CHART_MUT)
        ax2.tick_params(axis="x", colors=CHART_MUT); ax2.set_xlim(0, vals.max()*1.3)
        plt.tight_layout(); st.pyplot(fig2); plt.close()
    st.markdown("#### Full Table")
    d = leaderboard.copy()
    d["avg_views"] = d["avg_views"].apply(lambda x: f"{int(x):,}")
    d["avg_score"] = d["avg_score"].apply(lambda x: f"{x:.2f}")
    d["dremel_present"] = d["dremel_present"].apply(lambda x: "Yes" if x else "Gap")
    d.columns = ["Keyword","Avg Score","Avg Views","Videos","Dremel Present?"]
    st.dataframe(d, width="stretch", hide_index=True)

# TAB 2 — GOOGLE TRENDS
with tab2:
    st.markdown("<p class='section-title'>Google Trends — Real UK Search Data</p>", unsafe_allow_html=True)
    st.markdown("<p class='section-sub'>Live UK search interest and growth rates from Google Trends</p>", unsafe_allow_html=True)
    st.info("Fetching real Google Trends data — takes 20-30 seconds...")
    td = []; gp2 = st.progress(0); kf = selected_keywords[:6]
    for i, kw in enumerate(kf):
        gp2.progress((i+1)/len(kf))
        gt = get_trends(kw)
        td.append({"Keyword": clean_label(kw), "Search Score": gt["current"], "Growth %": gt["growth"], "Peak": gt["peak"]})
        time.sleep(1)
    gp2.empty()
    gt_df = pd.DataFrame(td).sort_values("Growth %", ascending=False)
    ct1, ct2 = st.columns(2)
    with ct1:
        fig3,ax3 = dark_chart()
        c3 = ["#00C46A" if g>0 else "#FF3B3B" for g in gt_df["Growth %"]]
        b3 = ax3.barh(gt_df["Keyword"], gt_df["Growth %"], color=c3, edgecolor="none", height=0.55)
        for bar,val in zip(b3, gt_df["Growth %"]):
            ax3.text(bar.get_width()+(1 if val>=0 else -1), bar.get_y()+bar.get_height()/2, f"{val:+.1f}%", va="center", color=CHART_TEXT, fontsize=9, fontweight="bold")
        ax3.set_title("Real UK Search Growth Rate", color=CHART_TEXT, fontweight="bold", fontsize=11)
        ax3.set_xlabel("Growth % (3 months)", color=CHART_MUT, fontsize=9); ax3.xaxis.label.set_color(CHART_MUT)
        ax3.tick_params(axis="x", colors=CHART_MUT); ax3.axvline(0, color=CHART_MUT, linewidth=0.5)
        plt.tight_layout(); st.pyplot(fig3); plt.close()
    with ct2:
        fig4,ax4 = dark_chart()
        b4 = ax4.barh(gt_df["Keyword"], gt_df["Search Score"], color="#4A90D9", edgecolor="none", height=0.55)
        for bar,val in zip(b4, gt_df["Search Score"]):
            ax4.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2, str(val), va="center", color=CHART_TEXT, fontsize=9, fontweight="bold")
        ax4.set_title("Current UK Search Interest (0-100)", color=CHART_TEXT, fontweight="bold", fontsize=11)
        ax4.set_xlabel("Google Trends Score", color=CHART_MUT, fontsize=9); ax4.xaxis.label.set_color(CHART_MUT)
        ax4.tick_params(axis="x", colors=CHART_MUT); ax4.set_xlim(0, 115)
        plt.tight_layout(); st.pyplot(fig4); plt.close()
    gd = gt_df.copy(); gd["Growth %"] = gd["Growth %"].apply(lambda x: f"{x:+.1f}%")
    st.dataframe(gd, width="stretch", hide_index=True)

# TAB 3 — SENTIMENT
with tab3:
    st.markdown("<p class='section-title'>Sentiment Analysis <span class='live-badge'>LIVE VADER NLP</span></p>", unsafe_allow_html=True)
    st.markdown("<p class='section-sub'>Real sentiment from actual YouTube comments using VADER NLP</p>", unsafe_allow_html=True)
    st.info("Analysing real YouTube comments with VADER NLP...")
    sp = st.progress(0); sr = {}; ka = df["keyword"].unique()[:6]
    for i,kw in enumerate(ka):
        sp.progress((i+1)/len(ka))
        vids = tuple(df[df["keyword"]==kw]["video_id"].tolist())
        sr[kw] = get_sentiment(kw, vids)
    sp.empty()
    cs1, cs2 = st.columns([2,1])
    with cs1:
        st.markdown("#### Sentiment by Keyword — Real YouTube Comments")
        for kw, sent in sr.items():
            pos=sent["Positive"]; neu=sent["Neutral"]; neg=sent["Negative"]; n=sent["sample_size"]
            st.markdown(f"""
            <div class='dark-card'>
                <h4>{clean_label(kw)} <small style='color:#4A4A6A;font-weight:400;'>({n} comments)</small></h4>
                <div style='display:flex;gap:3px;height:10px;border-radius:5px;overflow:hidden;margin-bottom:6px;'>
                    <div style='width:{pos}%;background:#00C46A;'></div>
                    <div style='width:{neu}%;background:#4A90D9;'></div>
                    <div style='width:{neg}%;background:#FF3B3B;'></div>
                </div>
                <p><span style='color:#00C46A;'>Positive {pos}%</span> &nbsp;
                   <span style='color:#4A90D9;'>Neutral {neu}%</span> &nbsp;
                   <span style='color:#FF3B3B;'>Negative {neg}%</span></p>
            </div>""", unsafe_allow_html=True)
    with cs2:
        st.markdown("#### Overall Brand Sentiment")
        if sr:
            ap = int(sum(v["Positive"] for v in sr.values())/len(sr))
            an = int(sum(v["Negative"] for v in sr.values())/len(sr))
            au = 100 - ap - an
        else: ap,au,an = 50,35,15
        st.markdown(f"""
        <div class='sent-pos'><h4 style='color:#00C46A;margin:0;'>Positive</h4>
            <p style='color:#C8C8D8;font-size:1.5em;font-weight:800;margin:3px 0 0 0;'>{ap}%</p>
            <p style='color:#8888AA;'>Engaged positively</p></div>
        <div class='sent-neu'><h4 style='color:#4A90D9;margin:0;'>Neutral</h4>
            <p style='color:#C8C8D8;font-size:1.5em;font-weight:800;margin:3px 0 0 0;'>{au}%</p>
            <p style='color:#8888AA;'>Informational mentions</p></div>
        <div class='sent-neg'><h4 style='color:#FF3B3B;margin:0;'>Negative</h4>
            <p style='color:#C8C8D8;font-size:1.5em;font-weight:800;margin:3px 0 0 0;'>{an}%</p>
            <p style='color:#8888AA;'>Concerns or complaints</p></div>
        """, unsafe_allow_html=True)

# TAB 4 — GAP ANALYSIS
with tab4:
    st.markdown("<p class='section-title'>Gap Analysis — What Dremel Is Missing</p>", unsafe_allow_html=True)
    st.markdown("<p class='section-sub'>Red = zero Dremel content. Real missed opportunities.</p>", unsafe_allow_html=True)
    cg1, cg2 = st.columns([3,2])
    with cg1:
        for _,row in leaderboard.sort_values("avg_score",ascending=False).iterrows():
            p = row["dremel_present"]
            cc = "gap-green" if p else "gap-red"
            st_ = "Dremel is active here" if p else "NO DREMEL CONTENT — ACT NOW"
            ac_ = "Maintain posting frequency" if p else f"Untapped: {int(row['avg_views']/1e6):.0f}M avg views, zero Dremel presence"
            st.markdown(f"""
            <div class='{cc}'>
                <h4>{row['keyword_clean']} — Score: {row['avg_score']:.2f}</h4>
                <p><strong>{st_}</strong></p><p>{ac_}</p>
            </div>""", unsafe_allow_html=True)
    with cg2:
        st.markdown("#### Summary")
        ng = len(leaderboard[~leaderboard["dremel_present"]])
        nc = len(leaderboard[leaderboard["dremel_present"]])
        gv = leaderboard[~leaderboard["dremel_present"]]["avg_views"].sum()
        st.metric("Keywords with zero Dremel content", f"{ng}/{len(leaderboard)}")
        st.metric("Total untapped avg views", f"{int(gv/1e6)}M+")
        st.metric("Keywords Dremel covers", f"{nc}")
        if ng > 0:
            tg = leaderboard[~leaderboard["dremel_present"]].iloc[0]
            st.markdown(f"""
            <div class='gap-red' style='margin-top:12px;'>
                <h4>Top Priority: {tg['keyword_clean']}</h4>
                <p>Avg {int(tg['avg_views']/1e6)}M views · Score {tg['avg_score']:.2f}</p>
                <p style='color:#FF4D00;font-weight:600;'>Create content immediately</p>
            </div>""", unsafe_allow_html=True)

# TAB 5 — TRENDING VIDEOS
with tab5:
    st.markdown("<p class='section-title'>Trending DIY Videos — YouTube UK</p>", unsafe_allow_html=True)
    st.markdown("<p class='section-sub'>Real scraped videos ranked by trend score</p>", unsafe_allow_html=True)
    skw = st.selectbox("Filter by keyword:", ["All"]+list(df["keyword_clean"].unique()), key="vid_kw")
    vdf = (df.sort_values("trend_score",ascending=False).head(20) if skw=="All"
           else df[df["keyword_clean"]==skw].sort_values("trend_score",ascending=False).head(20))
    for _,row in vdf.iterrows():
        isd = row["is_dremel"]
        bc  = "#00C46A" if isd else "#2A2A3A"
        tc  = "#00C46A" if isd else "#FFFFFF"
        bdg = "DREMEL" if isd else "Creator"
        st.markdown(f"""
        <div class='dark-card' style='border-left:4px solid {bc};'>
            <h4 style='color:{tc};'>{str(row['title'])[:85]}...</h4>
            <p>{row['channel']} &nbsp;·&nbsp; {int(row['views']):,} views &nbsp;·&nbsp;
               Score: {row['trend_score']} &nbsp;·&nbsp; {bdg} &nbsp;·&nbsp;
               <a href='{row.get("url","#")}' target='_blank' style='color:#4A90D9;'>Watch</a></p>
        </div>""", unsafe_allow_html=True)

# TAB 6 — AI IDEATION
with tab6:
    st.markdown("<p class='section-title'>AI Ideation Centre <span class='live-badge'>GEMINI AI</span></p>", unsafe_allow_html=True)
    st.markdown("<p class='section-sub'>Real AI briefs — hooks, CTAs, platforms, formats, video ideas — powered by Google Gemini</p>", unsafe_allow_html=True)
    ci1,ci2,ci3 = st.columns(3)
    with ci1: sel_trend   = st.selectbox("Trending Topic:", leaderboard["keyword_clean"].tolist(), key="id_trend")
    with ci2: sel_role    = st.selectbox("Your Role:", ROLES, key="id_role")
    with ci3: sel_product = st.selectbox("Dremel Product:", DREMEL_PRODUCTS, key="id_product")
    gen_btn = st.button("Generate AI Content Brief", use_container_width=True)
    if gen_btn:
        tr  = leaderboard[leaderboard["keyword_clean"]==sel_trend].iloc[0]
        sv  = round(tr["avg_score"], 2)
        rkw = next((k for k,v in KEYWORD_LABELS.items() if v==sel_trend), sel_trend)
        with st.spinner("Gemini AI is generating your brief..."):
            gtd = get_trends(rkw); grw = gtd["growth"]
            aib = generate_ai_brief(sel_trend, sel_role, sel_product, sv, grw)
        st.markdown("---")
        st.markdown(f"### Brief: **{sel_trend}** x **{sel_role}**")
        st.markdown(f"<small style='color:#6B6B8A'>Google Growth: {grw:+.1f}% · Score: {sv}</small>", unsafe_allow_html=True)
        if aib:
            dk   = ["HOOK","PLATFORM","FORMAT","CTA","POST_TIME","HASHTAGS","INSIGHT"]
            ik   = ["IDEA_1","IDEA_2","IDEA_3"]
            bi   = [(k, aib.get(k,"")) for k in dk if aib.get(k)]
            idls = [aib.get(k,"") for k in ik if aib.get(k)]
            cb1,cb2 = st.columns(2); half = len(bi)//2
            for lbl,val in bi[:half]:
                cb1.markdown(f"<div class='brief-box'><span class='brief-label'>{lbl}</span><p class='brief-value'>{val}</p></div>", unsafe_allow_html=True)
            for lbl,val in bi[half:]:
                cb2.markdown(f"<div class='brief-box'><span class='brief-label'>{lbl}</span><p class='brief-value'>{val}</p></div>", unsafe_allow_html=True)
            st.markdown("---"); st.markdown("#### AI Video Ideas")
            for idea in idls:
                st.markdown(f"<div class='dark-card'><p style='color:#E0E0F0;margin:0;'>🎬 {idea}</p></div>", unsafe_allow_html=True)
            st.markdown("---"); st.markdown("#### Keyword Expansion")
            ek1,ek2,ek3 = st.columns(3)
            def dc(bdr,col,lbl,body):
                return (f"<div style='background:#16161E;border-radius:10px;padding:14px;"
                        f"border:1px solid #2A2A3A;border-top:4px solid {bdr};'>"
                        f"<p style='color:{col};font-size:0.68em;font-weight:700;margin:0;"
                        f"text-transform:uppercase;letter-spacing:1px;'>{lbl}</p>"
                        f"<p style='color:#E0E0F0;font-weight:600;margin:7px 0 0 0;"
                        f"font-size:0.86em;line-height:1.5;'>{body}</p></div>")
            ek1.markdown(dc("#4A90D9","#4A90D9","Level 1 — Keyword", sel_trend), unsafe_allow_html=True)
            ek2.markdown(dc("#FF8C00","#FF8C00","Level 2 — Search Intent", f"How to do {sel_trend.lower()} for beginners UK 2025"), unsafe_allow_html=True)
            ek3.markdown(dc("#00C46A","#00C46A","Level 3 — Content Idea", f"I tried {sel_trend.lower()} using only a {sel_product} — here's what happened"), unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("""
            <div class='dark-card' style='border-top:3px solid #4A90D9;'>
                <h4 style='color:#4A90D9;'>Video Transcription (Next Step)</h4>
                <p>Run in terminal to transcribe the top trending video:<br>
                <code style='background:#0F0F13;padding:2px 8px;border-radius:4px;color:#FF8C00;'>pip install yt-dlp openai-whisper</code><br>
                <code style='background:#0F0F13;padding:2px 8px;border-radius:4px;color:#FF8C00;'>yt-dlp [video_url] -x --audio-format mp3 && whisper audio.mp3 --language en</code></p>
            </div>""", unsafe_allow_html=True)
            dbuf = make_docx(sel_trend, sel_role, sel_product, bi, idls)
            if dbuf:
                st.download_button(
                    label="Download Brief as Word Document", data=dbuf,
                    file_name=f"Dremel_Brief_{sel_trend.replace(' ','_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        else:
            st.error("Gemini could not generate a brief. Check your GEMINI_API_KEY in the .env file.")

# TAB 7 — NEXT ACTIONS
with tab7:
    st.markdown("<p class='section-title'>Automation Roadmap</p>", unsafe_allow_html=True)
    st.markdown("<p class='section-sub'>Step-by-step plan to make this fully autonomous</p>", unsafe_allow_html=True)
    cn1,cn2 = st.columns(2)
    for i,a in enumerate(NEXT_ACTIONS):
        col = cn1 if i%2==0 else cn2
        ec = {"Low":"#00C46A","Medium":"#FF8C00","High":"#FF3B3B"}.get(a["effort"],"#C8C8D8")
        ic = {"High":"#FF8C00","Very High":"#FF4D00"}.get(a["impact"],"#C8C8D8")
        col.markdown(f"""
        <div class='next-card'><h4>{a['title']}</h4><p>{a['detail']}</p>
        <p style='margin-top:7px;'>
            <span style='color:{ec};font-weight:600;font-size:0.76em;'>Effort: {a['effort']}</span>
            &nbsp;·&nbsp;
            <span style='color:{ic};font-weight:600;font-size:0.76em;'>Impact: {a['impact']}</span>
        </p></div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div class='dark-card' style='border-top:3px solid #FF4D00;'>
        <h4 style='color:#FF4D00;font-family:Syne,sans-serif;'>End Goal — Fully Autonomous Pipeline</h4>
        <p style='line-height:1.9;'>
        1. Cron job triggers every Monday 7am — scrapes YouTube UK + fetches Google Trends<br>
        2. VADER NLP scores real comments — sentiment dashboard updates automatically<br>
        3. Gemini AI generates role-specific briefs — emailed to all managers by 8am<br>
        4. Competitor gap detected — instant alert sent to marketing team<br>
        5. Dashboard auto-refreshes every 12 hours — zero manual work required
        </p>
    </div>""", unsafe_allow_html=True)

# FOOTER
st.markdown("---")
st.markdown(
    f"<p style='color:#4A4A6A;text-align:center;font-size:0.76em;'>"
    f"DREMEL Multi-Platform AI Intelligence &nbsp;·&nbsp; YouTube + Google Trends + VADER NLP + Gemini AI &nbsp;·&nbsp; "
    f"Auto-refreshes every 12 hours &nbsp;·&nbsp; {datetime.now().strftime('%d %b %Y %H:%M')}</p>",
    unsafe_allow_html=True
)