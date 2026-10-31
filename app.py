import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime
from html import escape
from textwrap import dedent
from dotenv import load_dotenv
from openpyxl.styles import Font, PatternFill, Alignment
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from data_analyzer import normalize_columns, profile_dataset, classify_dataset, numeric_summary, top_categories
from ai_assistant import ask_ai, generate_business_insights

load_dotenv()
st.set_page_config(page_title="Data Analytics Studio", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown(

    """

    <style>

    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');



    :root {

        --cyan: #35d5ff;

        --blue: #398cff;

        --purple: #9b78ff;

        --green: #22d6a0;

        --text: #eff6ff;

        --muted: #9bb1cf;

        --line: rgba(111, 166, 230, .22);

    }



    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    .stApp {

        color: var(--text);

        background:

          radial-gradient(ellipse at 75% -5%, rgba(24,105,214,.22), transparent 34%),

          radial-gradient(ellipse at 0% 35%, rgba(20,190,211,.07), transparent 28%),

          linear-gradient(140deg, #050c18 0%, #09172b 55%, #071222 100%);

    }

    [data-testid="stHeader"] {

        background: rgba(5,12,24,.82);

        backdrop-filter: blur(14px);

    }

    [data-testid="stSidebar"] {

        background: linear-gradient(180deg,#07172b 0%,#081326 100%);

        border-right: 1px solid var(--line);

    }

    [data-testid="stSidebar"] > div { padding-top: 1rem; }

    .block-container {
        max-width: 1680px;
        padding-top: 5.5rem !important;
        padding-bottom: 2.4rem;
    }

    /* Keep the Streamlit toolbar (Deploy / menu) above the app content.
       The extra top padding keeps the dashboard search bar below it. */
    [data-testid="stHeader"] {
        height: 3.5rem;
        z-index: 1000;
    }
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 5.5rem !important;
    }



    h1,h2,h3,h4 {

        font-family: 'Space Grotesk',sans-serif !important;

        color: var(--text) !important;

        letter-spacing: -.35px;

    }

    p,label,.stMarkdown { color:#c5d4e9; }



    .brand-row { display:flex; align-items:center; gap:11px; padding:8px 3px 17px; }

    .brand-mark {

        width:43px; height:43px; border-radius:13px; display:grid; place-items:center;

        background:linear-gradient(145deg,rgba(30,143,255,.30),rgba(33,220,255,.16));

        border:1px solid rgba(55,196,255,.45); box-shadow:0 0 25px rgba(30,153,255,.18);

        font-size:22px;

    }

    .brand-title { font:700 16px 'Space Grotesk',sans-serif; color:#f3f7ff; line-height:1.15; }

    .brand-sub { font-size:9px; color:#7795b9; letter-spacing:2px; margin-top:4px; }



    .hero {

        position:relative; overflow:hidden; min-height:190px;

        border:1px solid rgba(48,155,255,.42); border-radius:21px;

        padding:26px 28px; margin:4px 0 17px;

        background:

          radial-gradient(circle at 83% 45%,rgba(27,172,255,.22),transparent 25%),

          linear-gradient(112deg,rgba(8,28,57,.98),rgba(12,37,76,.94) 58%,rgba(18,43,88,.96));

        box-shadow:0 16px 45px rgba(0,0,0,.24),inset 0 1px 0 rgba(255,255,255,.06);

    }

    .hero:after {

        content:"▥"; position:absolute; right:7%; top:-14px; font-size:150px;

        color:rgba(54,174,255,.13); text-shadow:0 0 40px rgba(37,174,255,.25);

        pointer-events:none;

    }

    .hero-eyebrow { color:#69d8ff; font-size:10px; font-weight:700; letter-spacing:2.5px; }

    .hero h1 { font-size:clamp(27px,3vw,39px)!important; margin:8px 0; line-height:1.12; }

    .hero h1 span { color:#3c9dff; }

    .hero-copy { max-width:720px; color:#b6cbe7; font-size:13px; line-height:1.6; }

    .hero-pills { display:flex; flex-wrap:wrap; gap:8px; margin-top:15px; position:relative; z-index:2; }

    .hero-pill {

        padding:8px 11px; border-radius:10px; background:rgba(5,18,39,.58);

        border:1px solid rgba(112,178,255,.25); color:#e3efff; font-size:10px;

    }




   .welcome-row { display:grid; grid-template-columns:minmax(0,2.45fr) minmax(245px,.9fr); gap:14px; margin:4px 0 17px; }
   .welcome-panel { min-height:190px; border:1px solid rgba(48,155,255,.42); border-radius:18px; padding:18px;
       background:linear-gradient(145deg,rgba(8,28,57,.98),rgba(9,33,68,.96)); box-shadow:0 12px 35px rgba(0,0,0,.2); }
   .welcome-panel .date { color:#9bb9df; font-size:11px; }
   .welcome-panel .hello { color:#f3f7ff; font:700 22px 'Space Grotesk',sans-serif; margin:10px 0 6px; }
   .welcome-panel .tip { margin-top:18px; padding:11px; border:1px solid rgba(65,164,240,.24); border-radius:11px;
       background:rgba(10,35,63,.72); color:#bdd1ea; font-size:11px; line-height:1.5; }
   .upload-hint { color:#8fb0d5; font-size:10px; line-height:1.5; }
   @media(max-width:900px) { .welcome-row { grid-template-columns:1fr; } }


   .welcome-row { display:grid; grid-template-columns:minmax(0,2.45fr) minmax(245px,.9fr); gap:14px; margin:4px 0 17px; }
   .welcome-panel { min-height:190px; border:1px solid rgba(48,155,255,.42); border-radius:18px; padding:18px;
       background:linear-gradient(145deg,rgba(8,28,57,.98),rgba(9,33,68,.96)); box-shadow:0 12px 35px rgba(0,0,0,.2); }
   .welcome-panel .date { color:#9bb9df; font-size:11px; }
   .welcome-panel .hello { color:#f3f7ff; font:700 22px 'Space Grotesk',sans-serif; margin:10px 0 6px; }
   .welcome-panel .tip { margin-top:18px; padding:11px; border:1px solid rgba(65,164,240,.24); border-radius:11px;
       background:rgba(10,35,63,.72); color:#bdd1ea; font-size:11px; line-height:1.5; }
   .upload-hint { color:#8fb0d5; font-size:10px; line-height:1.5; }
   @media(max-width:900px) { .welcome-row { grid-template-columns:1fr; } }

   .section-head { margin:17px 0 11px; }

    .section-kicker { color:#47cfff; font-size:9px; letter-spacing:2px; font-weight:700; text-transform:uppercase; }

    .section-title { color:#f0f6ff; font:700 20px 'Space Grotesk',sans-serif; margin-top:3px; }



    .metric-card {

        position:relative; overflow:hidden; min-height:116px; padding:14px 15px;

        border-radius:15px; border:1px solid rgba(95,158,230,.25);

        background:linear-gradient(145deg,rgba(14,35,60,.98),rgba(8,24,43,.98));

        box-shadow:0 10px 28px rgba(0,0,0,.16);

    }

    .metric-card:after {

        content:""; position:absolute; right:-32px; top:-40px; width:105px; height:105px;

        border-radius:50%; background:rgba(43,171,255,.08);

    }

    .metric-top { display:flex; align-items:center; gap:9px; }

    .metric-icon {

        width:37px; height:37px; border-radius:11px; display:grid; place-items:center;

        font-size:17px; background:rgba(25,177,230,.13); border:1px solid rgba(45,199,255,.32);

    }

    .metric-label { color:#a9bdd8; font-size:9px; letter-spacing:.7px; font-weight:700; }

    .metric-value { color:#f4f8ff; font:700 22px 'Space Grotesk',sans-serif; margin-top:8px; }

    .metric-note { color:#7894b7; font-size:9px; margin-top:2px; }



    .feature-card,.glass-card {

        background:linear-gradient(145deg,rgba(15,39,67,.92),rgba(9,25,45,.96));

        border:1px solid rgba(95,164,232,.22); border-radius:14px;

        padding:16px; box-shadow:0 10px 28px rgba(0,0,0,.12);

    }

    .feature-card { min-height:128px; }

    .feature-icon { font-size:22px; margin-bottom:8px; }

    .feature-title,.card-title { color:#f2f7ff; font:700 14px 'Space Grotesk',sans-serif; }

    .feature-copy,.card-sub { color:#91a8c8; font-size:10px; line-height:1.55; margin-top:5px; }



    .dataset-status {

        background:rgba(11,32,53,.85); border:1px solid rgba(85,152,220,.22);

        border-radius:12px; padding:11px; color:#9fb6d5; font-size:10px;

    }

    .footer { color:#607b9e; text-align:center; font-size:9px; letter-spacing:1px; padding:23px 0 2px; }



    div[data-testid="stFileUploader"] {

        background:rgba(13,31,53,.8); border:1px dashed rgba(78,163,235,.42);

        border-radius:13px; padding:9px;

    }

    .stButton > button,.stDownloadButton > button {

        border-radius:10px; border:1px solid rgba(60,190,255,.42);

        background:linear-gradient(100deg,#245be9,#138dc4);

        color:white; font-weight:700; transition:all .2s ease;

    }

    .stButton > button:hover,.stDownloadButton > button:hover {

        box-shadow:0 0 20px rgba(38,170,255,.23); border-color:#55dfff;

        color:white; transform:translateY(-1px);

    }

    div[data-testid="stSelectbox"] > div,div[data-testid="stMultiSelect"] > div,
    div[data-testid="stDateInput"] > div,div[data-testid="stTextInput"] > div {
        background:#0e2036; border-radius:9px;
    }

    div[data-testid="stTextInput"] input {
        background:#0b1b30 !important;
        color:#eff6ff !important;
        border:1px solid rgba(65,160,255,.35) !important;
        border-radius:10px !important;
        min-height:42px;
        box-shadow:none !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border:1px solid #35d5ff !important;
        box-shadow:0 0 12px rgba(53,213,255,.18) !important;
    }

    .stRadio [role=radiogroup] { gap:5px; }

    .stRadio label {

        background:rgba(14,33,56,.68); border:1px solid rgba(93,151,215,.16);

        border-radius:9px; padding:5px 8px; margin:2px 0;

    }

    .stTabs [data-baseweb="tab-list"] { gap:6px; }

    .stTabs [data-baseweb="tab"] {

        background:#10243c; border:1px solid rgba(91,151,218,.18);

        border-radius:9px; padding:7px 13px;

    }

    .stTabs [aria-selected="true"] { background:#153b63!important; border-color:#29bfff!important; }

    [data-testid="stDataFrame"] { border:1px solid rgba(91,151,218,.22); border-radius:11px; overflow:hidden; }

    hr { border-color:rgba(111,166,230,.18); }

    </style>

    """,

    unsafe_allow_html=True,

)





def section(title, kicker="ANALYTICS WORKSPACE"):
    st.markdown(
        f'<div class="section-head"><div class="section-kicker">{escape(kicker)}</div>'
        f'<div class="section-title">{escape(title)}</div></div>',
        unsafe_allow_html=True,
    )

def metric_card(icon, label, value, note, accent="#35d5ff"):
    st.markdown(dedent(f"""
        <div class="metric-card">
          <div class="metric-top">
            <div class="metric-icon" style="color:{accent};border-color:{accent}55">{icon}</div>
            <div class="metric-label">{escape(label)}</div>
          </div>
          <div class="metric-value">{escape(str(value))}</div>
          <div class="metric-note">{escape(note)}</div>
        </div>
    """).strip(), unsafe_allow_html=True)

def style_chart(fig, height=330):
    fig.update_layout(
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#b9cce5", family="DM Sans", size=10),
        margin=dict(l=8, r=12, t=38, b=8),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#a9bdd7", size=9)),
        xaxis=dict(gridcolor="rgba(122,157,198,.10)"),
        yaxis=dict(gridcolor="rgba(122,157,198,.10)"),
        title=dict(font=dict(size=13, color="#eaf3ff")),
    )
    return fig

def read_uploaded_file(uploaded_file, sheet_name=None):
    name = uploaded_file.name.lower()
    uploaded_file.seek(0)
    if name.endswith(".csv"):
        errors = []
        for encoding in ("utf-8-sig", "utf-8", "latin-1"):
            try:
                uploaded_file.seek(0)
                return pd.read_csv(uploaded_file, encoding=encoding, sep=None, engine="python")
            except Exception as exc:
                errors.append(str(exc))
        raise ValueError("Could not read this CSV. Check its delimiter, encoding, and file contents.")
    if name.endswith((".xlsx", ".xls")):
        uploaded_file.seek(0)
        sheets = pd.read_excel(uploaded_file, sheet_name=None)
        if not sheets:
            raise ValueError("No worksheets were found in this Excel file.")
        selected = sheet_name if sheet_name in sheets else next(iter(sheets))
        return sheets[selected]
    raise ValueError("Unsupported format. Upload CSV, XLSX, or XLS.")

def make_excel_report(data, insights=None):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        data.to_excel(writer, sheet_name="Uploaded Data", index=False)
        profile = profile_dataset(data)
        profile["column_info"].to_excel(writer, sheet_name="Data Quality", index=False)
        stats = numeric_summary(data)
        if not stats.empty:
            stats.to_excel(writer, sheet_name="Numeric Summary", index=False)
        if insights:
            pd.DataFrame({"AI Insights": str(insights).splitlines()}).to_excel(writer, sheet_name="AI Insights", index=False)
        for ws in writer.book.worksheets:
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill("solid", fgColor="12365B")
                cell.alignment = Alignment(vertical="center")
            for cells in ws.columns:
                width = max((len(str(cell.value)) if cell.value is not None else 0) for cell in cells)
                ws.column_dimensions[cells[0].column_letter].width = min(width + 3, 42)
    output.seek(0)
    return output

def make_pdf_report(data, insights=None):
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4, rightMargin=14*mm, leftMargin=14*mm, topMargin=15*mm, bottomMargin=18*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="StudioTitle", parent=styles["Title"], textColor=colors.HexColor("#12365B"), fontSize=20, spaceAfter=7))
    styles.add(ParagraphStyle(name="StudioSmall", parent=styles["BodyText"], fontSize=8, leading=11))
    profile = profile_dataset(data)
    summary_rows = [["Dataset metric", "Result"], ["Records", f"{len(data):,}"], ["Columns", str(len(data.columns))],
                    ["Missing cells", f"{int(data.isna().sum().sum()):,}"], ["Duplicate rows", f"{int(data.duplicated().sum()):,}"],
                    ["Completeness", f"{profile['completeness']:.2f}%"]]
    story = [Paragraph("DATA ANALYTICS STUDIO", styles["StudioTitle"]),
             Paragraph(f"Dataset analysis report · Generated {datetime.now():%d %b %Y, %I:%M %p}", styles["StudioSmall"]),
             Spacer(1, 12), Paragraph("Dataset overview", styles["Heading2"])]
    table = Table(summary_rows, colWidths=[75*mm, 75*mm])
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#12365B")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
                               ("GRID",(0,0),(-1,-1),.4,colors.HexColor("#CCD6E0")),("PADDING",(0,0),(-1,-1),7)]))
    story.extend([table, Spacer(1, 12), Paragraph("Column profile", styles["Heading2"])])
    info = profile["column_info"].head(30)
    rows = [list(info.columns)] + info.astype(str).values.tolist()
    col_width = 150*mm / max(len(rows[0]), 1)
    t = Table(rows, colWidths=[col_width]*len(rows[0]), repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#12365B")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
                           ("GRID",(0,0),(-1,-1),.3,colors.HexColor("#CCD6E0")),("FONTSIZE",(0,0),(-1,-1),7),("PADDING",(0,0),(-1,-1),4)]))
    story.extend([t, Spacer(1, 12)])
    stats = numeric_summary(data)
    if not stats.empty:
        story.append(Paragraph("Numeric summary", styles["Heading2"]))
        story.append(Paragraph(escape(stats.round(2).to_string(index=False)).replace("\n","<br/>"), styles["StudioSmall"]))
    if insights:
        story.extend([Spacer(1, 12), Paragraph("AI insights", styles["Heading2"]),
                      Paragraph(escape(str(insights)).replace("\n","<br/>"), styles["StudioSmall"])])
    doc.build(story)
    output.seek(0)
    return output

# Sidebar
with st.sidebar:
    st.markdown(dedent("""
        <div class="brand-row"><div class="brand-mark">▥</div><div>
        <div class="brand-title">DATA<br>ANALYTICS STUDIO</div>
        <div class="brand-sub">UNIVERSAL DATA WORKSPACE</div></div></div>
    """).strip(), unsafe_allow_html=True)
    st.markdown("---")
    pages = ["Overview", "Column Analysis", "AI Assistant", "Data Explorer", "Reports & Export"]
    selected_page = st.radio("Navigate", pages, format_func=lambda p: {
        "Overview":"⌂  Overview", "Column Analysis":"▥  Column Analysis",
        "AI Assistant":"✦  AI Assistant", "Data Explorer":"▤  Data Explorer",
        "Reports & Export":"▧  Reports & Export"
    }[p], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("##### ⚑ UPLOAD DATASET")
    uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv","xlsx","xls"],
                                     help="Upload structured tabular data. The dashboard adapts to its columns.")
    st.markdown('<div class="upload-hint">Supported: CSV, XLSX and XLS. Excel workbooks with multiple sheets are supported.</div>', unsafe_allow_html=True)

# Header
top_left, top_right = st.columns([4,1])
with top_left:
    search_text = st.text_input("Search dataset", placeholder="Search across text columns...", label_visibility="collapsed", key="dashboard_search")
with top_right:
    st.markdown(f'<div style="text-align:right;color:#9bb2d1;font-size:10px;padding-top:8px">{datetime.now():%A, %d %B %Y}</div>', unsafe_allow_html=True)
st.markdown(dedent("""
<div class="welcome-row"><div class="hero">
<div class="hero-eyebrow">WELCOME TO YOUR ANALYTICS WORKSPACE</div>
<h1>DATA <span>ANALYTICS</span> STUDIO</h1>
<div class="hero-copy">Upload structured data and automatically discover patterns, metrics, trends and insights.</div>
<div class="hero-pills"><div class="hero-pill">▥ Dynamic Analytics</div><div class="hero-pill">✦ AI-Powered Insights</div><div class="hero-pill">▧ Excel & PDF Reports</div></div>
</div><div class="welcome-panel"><div class="date">ADAPTIVE ANALYTICS</div>
<div class="hello">Your data, understood.</div><div class="hero-copy">Sales, finance, HR, marketing, inventory, operations and more.</div>
<div class="tip">💡 Upload a CSV or Excel file to get started. Metrics and charts adapt to available columns.</div></div></div>
"""), unsafe_allow_html=True)

if uploaded_file is None:
    section("Your analytics command center", "WELCOME")
    st.info("Upload a CSV or Excel dataset from the left sidebar. The dashboard will analyze its structure automatically.")
    st.markdown('<div class="footer">DATA ANALYTICS STUDIO · TURNING DATA INTO BETTER DECISIONS</div>', unsafe_allow_html=True)
    st.stop()

# Excel sheet selection is exposed before reading.
sheet_choice = None
if uploaded_file.name.lower().endswith((".xlsx", ".xls")):
    try:
        uploaded_file.seek(0)
        excel_sheets = pd.ExcelFile(uploaded_file).sheet_names
        if len(excel_sheets) > 1:
            sheet_choice = st.sidebar.selectbox("Choose worksheet", excel_sheets)
    except Exception:
        pass

try:
    uploaded_file.seek(0)
    data = read_uploaded_file(uploaded_file, sheet_choice)
    data = normalize_columns(data)
    data = data.dropna(how="all").copy()
except Exception as exc:
    st.error(f"Could not read this file: {exc}")
    st.stop()

if data.empty or len(data.columns) == 0:
    st.warning("This file does not contain a usable table with rows and columns.")
    st.stop()

# Detect likely date columns without changing unrelated text fields.
profile = profile_dataset(data)
roles = profile["roles"]
date_col = roles.get("date")
if date_col and not pd.api.types.is_datetime64_any_dtype(data[date_col]):
    parsed = pd.to_datetime(data[date_col], errors="coerce")
    if parsed.notna().mean() >= 0.6:
        data[date_col] = parsed
        profile = profile_dataset(data)
        roles = profile["roles"]

filtered = data.copy()
if search_text.strip():
    text_cols = filtered.select_dtypes(include=["object","string","category"]).columns.tolist()
    if text_cols:
        mask = filtered[text_cols].astype(str).apply(lambda s: s.str.contains(search_text.strip(), case=False, na=False)).any(axis=1)
        filtered = filtered[mask]
if filtered.empty:
    st.warning("No records match your search. Clear the search field.")
    st.stop()

profile = profile_dataset(filtered)
roles = profile["roles"]
numeric_cols = filtered.select_dtypes(include="number").columns.tolist()
categorical_cols = filtered.select_dtypes(include=["object","category","bool"]).columns.tolist()
date_col = roles.get("date")
dataset_type = classify_dataset(filtered, roles)

with st.sidebar:
    st.markdown("---")
    st.markdown("##### ⚑ DATASET STATUS")
    st.success("Dataset loaded")
    st.caption(f"{len(data):,} rows · {len(data.columns)} columns")
    st.caption(f"Type: {dataset_type}")
    st.markdown("---")
    st.markdown("##### ⚑ FILTERS")
    filter_cols = [c for c in categorical_cols if filtered[c].nunique(dropna=True) <= 100][:4]
    for col in filter_cols:
        opts = sorted(filtered[col].dropna().astype(str).unique().tolist())
        chosen = st.multiselect(f"Filter: {col.replace('_',' ').title()}", opts, default=opts, key=f"dynamic_filter_{col}")
        filtered = filtered[filtered[col].astype(str).isin(chosen)]
    if date_col and pd.api.types.is_datetime64_any_dtype(filtered[date_col]) and filtered[date_col].notna().any():
        dmin, dmax = filtered[date_col].min().date(), filtered[date_col].max().date()
        if dmin < dmax:
            date_range = st.date_input("Date range", value=(dmin,dmax), min_value=dmin, max_value=dmax)
            if isinstance(date_range, (tuple,list)) and len(date_range)==2:
                filtered = filtered[filtered[date_col].dt.date.between(date_range[0],date_range[1])]

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

profile = profile_dataset(filtered)
numeric_cols = filtered.select_dtypes(include="number").columns.tolist()
categorical_cols = filtered.select_dtypes(include=["object","category","bool"]).columns.tolist()
roles = profile["roles"]
date_col = roles.get("date")
dataset_type = classify_dataset(filtered, roles)
stats = numeric_summary(filtered)

# Dynamic KPIs: always show record/field counts, plus useful numeric summaries.
section("Live dataset overview", dataset_type.upper())
kpis = [("▤","RECORDS",f"{len(filtered):,}","Rows in current view","#35d5ff"),
        ("▥","COLUMNS",f"{len(filtered.columns):,}","Fields detected","#9b78ff"),
        ("✓","COMPLETENESS",f"{profile['completeness']:.1f}%","Non-missing cells","#22d6a0"),
        ("⧉","DUPLICATES",f"{profile['duplicates']:,}","Exact duplicate rows","#ffb45f")]
if not stats.empty:
    chosen_metric = st.selectbox("Choose a numeric field for the main KPI", numeric_cols, key="main_numeric_metric")
    metric_total = pd.to_numeric(filtered[chosen_metric], errors="coerce").sum()
    kpis[0] = ("∑",f"TOTAL {chosen_metric.upper()}",f"{metric_total:,.2f}","Sum of selected numeric field","#35d5ff")
cols = st.columns(4, gap="small")
for col, item in zip(cols,kpis):
    with col:
        metric_card(*item)

if selected_page == "Overview":
    section("Automatic insights & visual discovery", "DYNAMIC OVERVIEW")
    if not stats.empty:
        st.markdown("#### Numeric summary")
        st.dataframe(stats.round(2), use_container_width=True, hide_index=True)
    c1,c2 = st.columns(2, gap="medium")
    with c1:
        if date_col and pd.api.types.is_datetime64_any_dtype(filtered[date_col]) and filtered[date_col].notna().any() and numeric_cols:
            metric = st.selectbox("Trend metric", numeric_cols, key="trend_metric")
            trend = filtered.dropna(subset=[date_col]).copy()
            trend["_period"] = trend[date_col].dt.to_period("M").astype(str)
            trend = trend.groupby("_period", as_index=False)[metric].sum()
            st.plotly_chart(style_chart(px.line(trend,x="_period",y=metric,markers=True,title=f"{metric} over time")), use_container_width=True)
        elif numeric_cols:
            metric = numeric_cols[0]
            st.plotly_chart(style_chart(px.histogram(filtered,x=metric,nbins=25,title=f"Distribution of {metric}")), use_container_width=True)
        else:
            st.info("No numeric fields were detected for a numeric chart.")
    with c2:
        if categorical_cols:
            cat = st.selectbox("Category field", categorical_cols, key="overview_category")
            value = st.selectbox("Measure", ["Record count"] + numeric_cols, key="overview_measure")
            grouped = top_categories(filtered, cat, None if value=="Record count" else value, 12)
            ycol = "Records" if value=="Record count" else "Total"
            st.plotly_chart(style_chart(px.bar(grouped,x=cat,y=ycol,title=f"{value} by {cat}",color=ycol)), use_container_width=True)
        elif numeric_cols:
            st.plotly_chart(style_chart(px.box(filtered,y=numeric_cols[0],title=f"Spread of {numeric_cols[0]}")), use_container_width=True)
        else:
            st.info("No categorical or numeric columns available for charts.")
    st.markdown("#### Data preview")
    st.dataframe(filtered.head(15), use_container_width=True, hide_index=True)

elif selected_page == "Column Analysis":
    section("Explore individual fields", "COLUMN INTELLIGENCE")
    if not filtered.columns.tolist():
        st.info("No columns available.")
    else:
        selected_col = st.selectbox("Select a column", filtered.columns.tolist())
        series = filtered[selected_col]
        a,b,c = st.columns(3)
        a.metric("Data type", str(series.dtype))
        b.metric("Unique values", f"{series.nunique(dropna=True):,}")
        c.metric("Missing values", f"{series.isna().sum():,}")
        if pd.api.types.is_numeric_dtype(series):
            st.write(series.describe().to_frame("Statistics"))
            st.plotly_chart(style_chart(px.histogram(filtered,x=selected_col,nbins=30,title=f"Distribution: {selected_col}")), use_container_width=True)
        elif pd.api.types.is_datetime64_any_dtype(series):
            counts = series.dropna().dt.to_period("M").astype(str).value_counts().sort_index().rename_axis("Period").reset_index(name="Records")
            st.plotly_chart(style_chart(px.line(counts,x="Period",y="Records",markers=True,title=f"Records over time: {selected_col}")), use_container_width=True)
        else:
            counts = series.fillna("(Missing)").astype(str).value_counts().head(25).rename_axis(selected_col).reset_index(name="Records")
            st.plotly_chart(style_chart(px.bar(counts,x=selected_col,y="Records",title=f"Most common values: {selected_col}")), use_container_width=True)
        st.dataframe(filtered[[selected_col]].head(100), use_container_width=True, hide_index=True)

elif selected_page == "AI Assistant":
    section("Your AI data analyst", "CONVERSATIONAL ANALYTICS")
    st.markdown('<div class="glass-card"><div class="card-title">✦ Ask questions. Discover insights.</div><div class="card-sub">Ask questions about any columns in the uploaded dataset. Gemini receives a data profile, numeric summaries and a small sample.</div></div>', unsafe_allow_html=True)
    signature = str(pd.util.hash_pandas_object(filtered, index=True).sum())
    if st.session_state.get("chat_signature") != signature:
        st.session_state.chat_history = []
        st.session_state.chat_signature = signature
    if st.button("✦ Generate dataset insights"):
        with st.spinner("Gemini is analyzing your dataset..."):
            try:
                st.session_state["business_insights"] = generate_business_insights(filtered.copy())
                st.session_state["insights_signature"] = signature
            except Exception as exc:
                st.error(f"Could not generate insights: {exc}")
    if st.session_state.get("insights_signature") == signature:
        st.markdown(st.session_state.get("business_insights",""))
    for message in st.session_state.get("chat_history",[]):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    prompt = st.chat_input("Ask anything about your uploaded data...")
    if prompt:
        st.session_state.chat_history.append({"role":"user","content":prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your data..."):
                try:
                    answer = ask_ai(prompt, filtered.copy())
                    st.markdown(answer)
                    st.session_state.chat_history.append({"role":"assistant","content":str(answer)})
                except Exception as exc:
                    st.error(f"AI assistant error: {exc}")

elif selected_page == "Data Explorer":
    section("Dataset explorer", "DATA QUALITY & DISCOVERY")
    tab1,tab2,tab3 = st.tabs(["▤ Data preview","◈ Data quality","∑ Statistics"])
    with tab1:
        st.dataframe(filtered,use_container_width=True,height=430)
        st.caption(f"{len(filtered):,} records · {len(filtered.columns)} columns")
    with tab2:
        st.dataframe(profile["column_info"],use_container_width=True,hide_index=True)
        q1,q2,q3=st.columns(3)
        q1.metric("Missing cells",f"{profile['missing']:,}")
        q2.metric("Duplicate rows",f"{profile['duplicates']:,}")
        q3.metric("Completeness",f"{profile['completeness']:.1f}%")
    with tab3:
        st.dataframe(filtered.describe(include="all").transpose(),use_container_width=True)

elif selected_page == "Reports & Export":
    section("Reports & exports", "SHARE YOUR ANALYSIS")
    st.markdown('<div class="glass-card"><div class="card-title">Your dataset report is ready to build</div><div class="card-sub">Exports include the current filtered data, data quality profile and numeric summary. AI insights are included when generated.</div></div>',unsafe_allow_html=True)
    signature = str(pd.util.hash_pandas_object(filtered,index=True).sum())
    insights = st.session_state.get("business_insights") if st.session_state.get("insights_signature")==signature else None
    try:
        xlsx = make_excel_report(filtered.copy(),insights)
        pdf = make_pdf_report(filtered.copy(),insights)
        c1,c2=st.columns(2)
        with c1:
            st.markdown("### 📘 Excel workbook")
            st.download_button("Download Excel report",data=xlsx,file_name=f"data_analytics_report_{datetime.now():%Y%m%d_%H%M}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
        with c2:
            st.markdown("### 📕 PDF report")
            st.download_button("Download PDF report",data=pdf,file_name=f"data_analytics_report_{datetime.now():%Y%m%d_%H%M}.pdf",mime="application/pdf",use_container_width=True)
    except Exception as exc:
        st.error(f"Could not prepare reports: {exc}")

st.markdown('<div class="footer">DATA ANALYTICS STUDIO · ADAPTIVE ANALYTICS FOR EVERY DATASET</div>', unsafe_allow_html=True)
