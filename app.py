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



# Keep your existing ai_assistant.py in the same project folder.

from ai_assistant import ask_ai, generate_business_insights



load_dotenv()



# =========================================================

# PAGE SETTINGS

# =========================================================

st.set_page_config(

    page_title="Data Analytics Studio",

    page_icon="📊",

    layout="wide",

    initial_sidebar_state="expanded",

)



# =========================================================

# VISUAL DESIGN

# =========================================================

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



# =========================================================

# COMMON HELPERS

# =========================================================

def money(value):

    try:

        return f"₹{float(value):,.2f}"

    except (TypeError, ValueError):

        return "₹0.00"





def number(value):

    try:

        return f"{float(value):,.0f}"

    except (TypeError, ValueError):

        return "0"





def section(title, kicker="ANALYTICS WORKSPACE"):

    st.markdown(

        f'<div class="section-head"><div class="section-kicker">{escape(kicker)}</div>'

        f'<div class="section-title">{escape(title)}</div></div>',

        unsafe_allow_html=True,

    )





def metric_card(icon, label, value, note, accent="#35d5ff"):

    st.markdown(
        dedent(f"""
        <div class="metric-card">
          <div class="metric-top">
            <div class="metric-icon" style="color:{accent};border-color:{accent}55">{icon}</div>
            <div class="metric-label">{escape(label)}</div>
          </div>
          <div class="metric-value">{escape(str(value))}</div>
          <div class="metric-note">{escape(note)}</div>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )





def style_chart(fig, height=330):

    fig.update_layout(

        height=height,

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(color="#b9cce5", family="DM Sans", size=10),

        margin=dict(l=8, r=12, t=38, b=8),

        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#a9bdd7", size=9)),

        xaxis=dict(gridcolor="rgba(122,157,198,.10)", zerolinecolor="rgba(122,157,198,.10)"),

        yaxis=dict(gridcolor="rgba(122,157,198,.10)", zerolinecolor="rgba(122,157,198,.10)"),

        title=dict(font=dict(size=13, color="#eaf3ff")),

    )

    return fig





def normalize_columns(df):

    """Normalize common column labels to consistent names."""

    aliases = {

        "order id": "order_id",

        "orderid": "order_id",

        "order date": "order_date",

        "date": "order_date",

        "unit price": "unit_price",

        "selling price": "unit_price",

        "qty": "quantity",

        "product name": "product",

        "product_name": "product",

        "category name": "category",

        "region name": "region",

    }

    rename = {}

    for col in df.columns:

        clean = str(col).strip().lower().replace("-", " ")

        clean = " ".join(clean.split())

        target = aliases.get(clean, clean.replace(" ", "_"))

        rename[col] = target

    return df.rename(columns=rename)





def load_data(uploaded_file):

    """Read CSV/Excel and prepare revenue/date fields safely."""

    filename = uploaded_file.name.lower()
    if filename.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif filename.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    elif filename.endswith(".xls"):
        try:
            df = pd.read_excel(uploaded_file, engine="xlrd")
        except ImportError as exc:
            raise ImportError(
                "To upload .xls files, install xlrd: python -m pip install xlrd"
            ) from exc
    else:
        raise ValueError("Unsupported file type. Please upload CSV, XLSX, or XLS.")



    df = normalize_columns(df)



    if "quantity" in df.columns:

        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

    if "unit_price" in df.columns:

        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")



    if {"quantity", "unit_price"}.issubset(df.columns):

        df["revenue"] = df["quantity"].fillna(0) * df["unit_price"].fillna(0)

    elif "revenue" in df.columns:

        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0)

    else:

        raise ValueError(

            "Your file needs either 'revenue' or both 'quantity' and 'unit_price' columns."

        )



    if "order_date" in df.columns:

        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    return df





def dataframe_signature(df):

    try:

        return str(pd.util.hash_pandas_object(df, index=True).sum())

    except TypeError:

        return str(hash(df.to_csv(index=False)))





def make_excel_report(data, insights=None):

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        data.to_excel(writer, sheet_name="Filtered Data", index=False)



        orders = data["order_id"].nunique() if "order_id" in data.columns else len(data)

        units = data["quantity"].sum() if "quantity" in data.columns else 0

        summary = pd.DataFrame({

            "Metric": ["Total Revenue", "Unique Orders", "Units Sold", "Average Order Value", "Records"],

            "Value": [

                data["revenue"].sum(), orders, units,

                data["revenue"].sum() / max(orders, 1), len(data),

            ],

        })

        summary.to_excel(writer, sheet_name="Business Summary", index=False)



        for column, sheet in [

            ("product", "Product Analysis"),

            ("category", "Category Analysis"),

            ("region", "Regional Analysis"),

        ]:

            if column in data.columns:

                data.groupby(column, as_index=False)["revenue"].sum().sort_values(

                    "revenue", ascending=False

                ).to_excel(writer, sheet_name=sheet, index=False)



        if "order_date" in data.columns:

            dated = data.dropna(subset=["order_date"]).copy()

            if not dated.empty:

                dated["Month"] = dated["order_date"].dt.to_period("M").astype(str)

                dated.groupby("Month", as_index=False)["revenue"].sum().to_excel(

                    writer, sheet_name="Monthly Sales", index=False

                )



        if insights:

            pd.DataFrame({"AI Insights": str(insights).splitlines()}).to_excel(

                writer, sheet_name="AI Insights", index=False

            )



        for ws in writer.book.worksheets:

            ws.freeze_panes = "A2"

            ws.auto_filter.ref = ws.dimensions

            for cell in ws[1]:

                cell.font = Font(bold=True, color="FFFFFF")

                cell.fill = PatternFill("solid", fgColor="12365B")

                cell.alignment = Alignment(vertical="center")

            for cells in ws.columns:

                width = max(

                    (len(str(cell.value)) if cell.value is not None else 0)

                    for cell in cells

                )

                ws.column_dimensions[cells[0].column_letter].width = min(width + 3, 42)



    output.seek(0)

    return output





def make_pdf_report(data, insights=None):

    output = BytesIO()

    doc = SimpleDocTemplate(

        output, pagesize=A4,

        rightMargin=15 * mm, leftMargin=15 * mm,

        topMargin=15 * mm, bottomMargin=18 * mm,

    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(

        name="StudioTitle", parent=styles["Title"],

        textColor=colors.HexColor("#12365B"), fontSize=21, spaceAfter=7,

    ))

    styles.add(ParagraphStyle(

        name="StudioSmall", parent=styles["BodyText"], fontSize=8, leading=11,

    ))



    orders = data["order_id"].nunique() if "order_id" in data.columns else len(data)

    units = data["quantity"].sum() if "quantity" in data.columns else 0

    rows = [

        ["Metric", "Result"],

        ["Total Revenue", money(data["revenue"].sum())],

        ["Unique Orders", number(orders)],

        ["Units Sold", number(units)],

        ["Average Order Value", money(data["revenue"].sum() / max(orders, 1))],

        ["Records Analyzed", number(len(data))],

    ]

    summary_table = Table(rows, colWidths=[75 * mm, 75 * mm])

    summary_table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12365B")),

        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#CCD6E0")),

        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),

        ("PADDING", (0, 0), (-1, -1), 7),

    ]))



    story = [

        Paragraph("DATA ANALYTICS STUDIO", styles["StudioTitle"]),

        Paragraph(

            f"Business performance report · Generated {datetime.now():%d %b %Y, %I:%M %p}",

            styles["StudioSmall"],

        ),

        Spacer(1, 12),

        Paragraph("Executive Summary", styles["Heading2"]),

        summary_table,

        Spacer(1, 12),

    ]



    for column, heading in [

        ("product", "Product Performance"),

        ("category", "Category Performance"),

        ("region", "Regional Performance"),

    ]:

        if column in data.columns:

            grouped = data.groupby(column, as_index=False)["revenue"].sum().sort_values(

                "revenue", ascending=False

            )

            table_rows = [[heading.replace(" Performance", ""), "Revenue"]]

            table_rows += [

                [str(row[column]), money(row["revenue"])]

                for _, row in grouped.head(12).iterrows()

            ]

            report_table = Table(table_rows, colWidths=[75 * mm, 75 * mm], repeatRows=1)

            report_table.setStyle(TableStyle([

                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12365B")),

                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

                ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#CCD6E0")),

                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),

                ("PADDING", (0, 0), (-1, -1), 6),

            ]))

            story.extend([Paragraph(heading, styles["Heading2"]), report_table, Spacer(1, 10)])



    if insights:

        safe_insights = escape(str(insights)).replace("\n", "<br/>")

        story.extend([

            Paragraph("AI Insights & Recommendations", styles["Heading2"]),

            Paragraph(safe_insights, styles["StudioSmall"]),

        ])



    def footer(canvas, document):

        canvas.saveState()

        canvas.setFont("Helvetica", 8)

        canvas.setFillColor(colors.HexColor("#64748B"))

        canvas.drawString(15 * mm, 9 * mm, "DATA ANALYTICS STUDIO")

        canvas.drawRightString(A4[0] - 15 * mm, 9 * mm, f"Page {document.page}")

        canvas.restoreState()



    doc.build(story, onFirstPage=footer, onLaterPages=footer)

    output.seek(0)

    return output





# =========================================================

# SIDEBAR: BRAND, NAVIGATION, UPLOAD

# =========================================================

with st.sidebar:

    st.markdown(
        dedent("""
        <div class="brand-row">
          <div class="brand-mark">▥</div>
          <div>
            <div class="brand-title">DATA<br>ANALYTICS STUDIO</div>
            <div class="brand-sub">INTELLIGENCE WORKSPACE</div>
          </div>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown("##### ◈ NAVIGATION")



    pages = [

        "Overview", "Sales Analysis", "Product Analysis",

        "Regional Analysis", "AI Assistant", "Data Explorer", "Reports & Export",

    ]

    selected_page = st.radio(

        "Navigate",

        pages,

        format_func=lambda page: {

            "Overview": "⌂  Overview",

            "Sales Analysis": "⌁  Sales Analysis",

            "Product Analysis": "◇  Product Analysis",

            "Regional Analysis": "◎  Regional Analysis",

            "AI Assistant": "✦  AI Assistant",

            "Data Explorer": "▤  Data Explorer",

            "Reports & Export": "▧  Reports & Export",

        }[page],

        label_visibility="collapsed",

    )

    st.markdown("---")

    st.markdown("##### ⚑ UPLOAD DATASET")

    uploaded_file = st.file_uploader(

        "Upload your dataset",

        type=["csv", "xlsx", "xls"],

        help="Upload a CSV or Excel file to begin.",

    )

    st.markdown(
        '<div class="upload-hint">Supported: <b>CSV</b>, <b>Excel .xlsx</b>, and <b>Excel .xls</b>.<br>'
        'For legacy .xls files, install the xlrd package.</div>',
        unsafe_allow_html=True,
    )



# =========================================================

# TOP BAR + HERO

# =========================================================

top_left, top_right = st.columns([4, 1])

with top_left:

    search_text = st.text_input(

        "Search dataset",

        placeholder="Search products, categories, regions...",

        label_visibility="collapsed",

        key="dashboard_search",

    )

with top_right:

    st.markdown(

        f'<div style="text-align:right;color:#9bb2d1;font-size:10px;padding-top:8px">'

        f'{datetime.now():%A, %d %B %Y}</div>',

        unsafe_allow_html=True,

    )



st.markdown(
    """
    <div class="welcome-row">
      <div class="hero">
        <div class="hero-eyebrow">WELCOME TO YOUR ANALYTICS WORKSPACE</div>
        <h1>DATA <span>ANALYTICS</span> STUDIO</h1>
        <div class="hero-copy">Turn your data into insights. Explore trends, discover opportunities,
        and make smarter business decisions with analytics and AI.</div>
        <div class="hero-pills">
          <div class="hero-pill">▥ &nbsp; Interactive Analytics</div>
          <div class="hero-pill">✦ &nbsp; AI-Powered Insights</div>
          <div class="hero-pill">▧ &nbsp; Excel & PDF Reports</div>
        </div>
      </div>
      <div class="welcome-panel">
        <div class="date">""" + datetime.now().strftime("%A, %d %B %Y") + """</div>
        <div class="hello">Good day, Rupin! 👋</div>
        <div class="hero-copy">Here’s what’s happening with your business today.</div>
        <div class="tip">💡 &nbsp; <b style="color:#4bd5ff">Tip of the day</b><br>
        Use filters to analyze specific time periods, products, or regions.</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================

# WELCOME / EMPTY STATE

# =========================================================

if uploaded_file is None:

    section("Your analytics command center", "WELCOME")
    st.info("Upload a CSV or Excel workbook (.xlsx or .xls) using the Dataset uploader in the left sidebar.")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(

            '<div class="feature-card"><div class="feature-icon">📈</div>'

            '<div class="feature-title">Interactive Analytics</div>'

            '<div class="feature-copy">Explore KPIs, sales trends, product performance, and regional comparisons.</div></div>',

            unsafe_allow_html=True,

        )

    with c2:

        st.markdown(

            '<div class="feature-card"><div class="feature-icon">✦</div>'

            '<div class="feature-title">AI Business Insights</div>'

            '<div class="feature-copy">Ask questions in natural language and generate practical recommendations using Gemini.</div></div>',

            unsafe_allow_html=True,

        )

    with c3:

        st.markdown(

            '<div class="feature-card"><div class="feature-icon">📄</div>'

            '<div class="feature-title">Professional Reports</div>'

            '<div class="feature-copy">Export your analysis into structured Excel workbooks and PDF reports.</div></div>',

            unsafe_allow_html=True,

        )

    st.markdown(

        '<div class="footer">DATA ANALYTICS STUDIO · TURNING DATA INTO BETTER DECISIONS</div>',

        unsafe_allow_html=True,

    )

    st.stop()



# =========================================================

# LOAD + VALIDATE DATA

# =========================================================

try:

    data = load_data(uploaded_file)

except Exception as exc:

    st.error(f"Could not load this dataset: {exc}")

    st.stop()



if data.empty:

    st.warning("The uploaded dataset contains no rows.")

    st.stop()



# =========================================================

# SIDEBAR FILTERS

# =========================================================

filtered = data.copy()



if search_text.strip():

    text_columns = filtered.select_dtypes(include=["object", "string"]).columns.tolist()

    if text_columns:

        search_mask = filtered[text_columns].astype(str).apply(

            lambda column: column.str.contains(search_text.strip(), case=False, na=False)

        ).any(axis=1)

        filtered = filtered[search_mask]



with st.sidebar:

    st.markdown("---")

    st.markdown("##### ⚑ FILTERS")



    if "order_date" in filtered.columns and filtered["order_date"].notna().any():

        valid_dates = filtered["order_date"].dropna()

        min_date, max_date = valid_dates.min().date(), valid_dates.max().date()

        selected_dates = st.date_input(

            "Date range",

            value=(min_date, max_date),

            min_value=min_date,

            max_value=max_date,

        )

        if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:

            start_date, end_date = selected_dates

            filtered = filtered[

                filtered["order_date"].dt.date.between(start_date, end_date)

            ]



    for column, label in [

        ("product", "Products"),

        ("category", "Categories"),

        ("region", "Regions"),

    ]:

        if column in filtered.columns:

            options = sorted(filtered[column].dropna().astype(str).unique().tolist())

            selected_values = st.multiselect(label, options, default=options, key=f"filter_{column}")

            filtered = filtered[filtered[column].astype(str).isin(selected_values)]



    st.markdown("---")

    st.markdown(

        f"""

        <div class="dataset-status">

          <div style="font-weight:700;color:#dceaff;margin-bottom:7px">▤ DATASET STATUS</div>

          <div><span style="color:#22d6a0">●</span> Loaded successfully</div>

          <div style="margin-top:5px;color:#dceaff">{len(data):,} total records</div>

          <div style="margin-top:3px">{len(data.columns)} columns · {escape(uploaded_file.name)}</div>

        </div>

        """,

        unsafe_allow_html=True,

    )



if filtered.empty:

    st.warning("No records match the selected filters. Adjust the search or filters.")

    st.stop()



# =========================================================

# METRICS

# =========================================================

total_revenue = float(filtered["revenue"].sum())

total_orders = int(filtered["order_id"].nunique()) if "order_id" in filtered.columns else len(filtered)

total_units = float(filtered["quantity"].fillna(0).sum()) if "quantity" in filtered.columns else 0

average_order_value = total_revenue / max(total_orders, 1)

current_signature = dataframe_signature(filtered)



st.markdown(

    f'<div class="section-kicker" style="margin:4px 0 9px">LIVE DATA OVERVIEW · {len(filtered):,} RECORDS IN VIEW</div>',

    unsafe_allow_html=True,

)

k1, k2, k3, k4 = st.columns(4, gap="small")

with k1:

    metric_card("₹", "TOTAL REVENUE", money(total_revenue), "Current filtered dataset", "#35d5ff")

with k2:

    metric_card("🛒", "TOTAL ORDERS", number(total_orders), "Unique order IDs" if "order_id" in filtered.columns else "Rows counted as records", "#ffb45f")

with k3:

    metric_card("◇", "UNITS SOLD", number(total_units), "Total quantity", "#22d6a0")

with k4:

    metric_card("▥", "AVERAGE ORDER VALUE", money(average_order_value), "Revenue ÷ unique orders", "#9b78ff")



# =========================================================

# OVERVIEW

# =========================================================

if selected_page == "Overview":

    section("Performance overview", "BUSINESS INTELLIGENCE")

    left, right = st.columns([1.55, 1], gap="medium")



    with left:

        if "order_date" in filtered.columns and filtered["order_date"].notna().any():

            dated = filtered.dropna(subset=["order_date"]).copy()

            dated["Month"] = dated["order_date"].dt.to_period("M").astype(str)

            monthly = dated.groupby("Month", as_index=False).agg(

                Revenue=("revenue", "sum"),

                Orders=("order_id", "nunique") if "order_id" in dated.columns else ("revenue", "count"),

            )

            fig = go.Figure()

            fig.add_trace(go.Scatter(

                x=monthly["Month"], y=monthly["Revenue"], name="Revenue",

                mode="lines+markers", line=dict(color="#229dff", width=3),

                fill="tozeroy", fillcolor="rgba(34,157,255,.10)",

                hovertemplate="%{x}<br>Revenue: ₹%{y:,.0f}<extra></extra>",

            ))

            fig.add_trace(go.Scatter(

                x=monthly["Month"], y=monthly["Orders"], name="Orders",

                mode="lines+markers", line=dict(color="#9667ff", width=2),

                yaxis="y2", hovertemplate="%{x}<br>Orders: %{y}<extra></extra>",

            ))

            fig.update_layout(

                title="Revenue trend",

                yaxis=dict(title="Revenue (₹)", gridcolor="rgba(122,157,198,.10)"),

                yaxis2=dict(title="Orders", overlaying="y", side="right", showgrid=False),

                legend=dict(orientation="h", y=1.12, x=.62),

            )

            st.plotly_chart(style_chart(fig, 340), use_container_width=True)

        else:

            st.info("Add an order_date or date column to display monthly revenue.")



    with right:

        if "category" in filtered.columns:

            category = filtered.groupby("category", as_index=False)["revenue"].sum()

            fig = px.pie(

                category, names="category", values="revenue", hole=.67,

                title="Category revenue",

                color_discrete_sequence=["#268dff", "#17c9c2", "#9468ff", "#f3a640", "#ec65b6", "#78a8e8"],

            )

            fig.update_traces(

                textposition="outside", textinfo="percent",

                marker=dict(line=dict(color="#0a1729", width=2)),

                hovertemplate="%{label}<br>Revenue: ₹%{value:,.0f}<extra></extra>",

            )

            fig.add_annotation(

                text=f"<b>{money(total_revenue)}</b><br><span style='font-size:10px'>Total revenue</span>",

                x=.5, y=.5, showarrow=False, font=dict(color="#eff6ff", size=13),

            )

            st.plotly_chart(style_chart(fig, 340), use_container_width=True)

        else:

            st.info("Add a category column to view category revenue.")



    p1, p2, p3 = st.columns([1, 1, 1.2], gap="medium")

    with p1:

        if "product" in filtered.columns:

            product_totals = filtered.groupby("product", as_index=False)["revenue"].sum()

            top = product_totals.nlargest(6, "revenue").sort_values("revenue")

            fig = px.bar(

                top, x="revenue", y="product", orientation="h",

                title="Top products by revenue",

                color="revenue", color_continuous_scale=["#2754a5", "#23c6ff"],

            )

            fig.update_layout(coloraxis_showscale=False)

            st.plotly_chart(style_chart(fig, 290), use_container_width=True)

        else:

            st.info("Add a product column to see product rankings.")



    with p2:

        if "region" in filtered.columns:

            regional = filtered.groupby("region", as_index=False)["revenue"].sum().sort_values("revenue")

            fig = px.bar(

                regional, x="revenue", y="region", orientation="h",

                title="Regional revenue",

                color="revenue", color_continuous_scale=["#344f9c", "#9267ff"],

            )

            fig.update_layout(coloraxis_showscale=False)

            st.plotly_chart(style_chart(fig, 290), use_container_width=True)

        else:

            st.info("Add a region column to compare regions.")



    with p3:

        section("Recent records", "LATEST ACTIVITY")

        recent = filtered.copy()

        if "order_date" in recent.columns:

            recent = recent.sort_values("order_date", ascending=False)

        display_columns = [

            col for col in ["order_id", "order_date", "product", "region", "revenue"]

            if col in recent.columns

        ]

        if display_columns:

            recent = recent[display_columns].head(6).copy()

            if "order_date" in recent.columns:

                recent["order_date"] = recent["order_date"].dt.strftime("%d %b %Y")

            if "revenue" in recent.columns:

                recent["revenue"] = recent["revenue"].map(money)

            st.dataframe(recent, use_container_width=True, hide_index=True, height=250)

        else:

            st.dataframe(filtered.head(6), use_container_width=True, hide_index=True)



# =========================================================

# SALES ANALYSIS

# =========================================================

elif selected_page == "Sales Analysis":

    section("Sales performance & trends", "REVENUE INTELLIGENCE")

    if "order_date" not in filtered.columns:

        st.warning("This analysis needs an order_date or date column.")

    else:

        dated = filtered.dropna(subset=["order_date"]).copy()

        if dated.empty:

            st.info("No valid dates were found in the selected records.")

        else:

            dated["Month"] = dated["order_date"].dt.to_period("M").astype(str)

            monthly = dated.groupby("Month", as_index=False).agg(

                Revenue=("revenue", "sum"),

                Orders=("order_id", "nunique") if "order_id" in dated.columns else ("revenue", "count"),

            )

            c1, c2 = st.columns(2)

            with c1:

                fig = px.area(monthly, x="Month", y="Revenue", title="Monthly revenue", markers=True, color_discrete_sequence=["#28baff"])

                fig.update_traces(line=dict(width=3), fillcolor="rgba(40,186,255,.12)")

                st.plotly_chart(style_chart(fig), use_container_width=True)

            with c2:

                fig = px.bar(monthly, x="Month", y="Orders", title="Orders by month", color_discrete_sequence=["#936aff"])

                st.plotly_chart(style_chart(fig), use_container_width=True)

            st.dataframe(monthly, use_container_width=True, hide_index=True)



    fig = px.histogram(filtered, x="revenue", nbins=20, title="Revenue distribution", color_discrete_sequence=["#1cbda9"])

    st.plotly_chart(style_chart(fig), use_container_width=True)



# =========================================================

# PRODUCT ANALYSIS

# =========================================================

elif selected_page == "Product Analysis":

    section("Product performance", "PRODUCT INTELLIGENCE")

    if "product" not in filtered.columns:

        st.warning("This dataset does not contain a product column.")

    else:

        aggregations = {"Revenue": ("revenue", "sum")}

        if "quantity" in filtered.columns:

            aggregations["Units"] = ("quantity", "sum")

        product = filtered.groupby("product", as_index=False).agg(**aggregations).sort_values("Revenue", ascending=False)

        c1, c2 = st.columns(2)

        with c1:

            fig = px.bar(product, x="product", y="Revenue", title="Revenue by product", color="Revenue", color_continuous_scale=["#244e9b", "#27c4ff"])

            fig.update_layout(coloraxis_showscale=False)

            st.plotly_chart(style_chart(fig), use_container_width=True)

        with c2:

            if "Units" in product.columns:

                fig = px.bar(product, x="product", y="Units", title="Units sold by product", color_discrete_sequence=["#936aff"])

                st.plotly_chart(style_chart(fig), use_container_width=True)

        st.dataframe(product, use_container_width=True, hide_index=True)



# =========================================================

# REGIONAL ANALYSIS

# =========================================================

elif selected_page == "Regional Analysis":

    section("Regional performance", "GEOGRAPHIC INTELLIGENCE")

    if "region" not in filtered.columns:

        st.warning("This dataset does not contain a region column.")

    else:

        aggregations = {"Revenue": ("revenue", "sum")}

        if "order_id" in filtered.columns:

            aggregations["Orders"] = ("order_id", "nunique")

        regional = filtered.groupby("region", as_index=False).agg(**aggregations).sort_values("Revenue", ascending=False)

        c1, c2 = st.columns(2)

        with c1:

            fig = px.bar(regional, x="region", y="Revenue", title="Revenue by region", color="Revenue", color_continuous_scale=["#26529a", "#28c6ff"])

            fig.update_layout(coloraxis_showscale=False)

            st.plotly_chart(style_chart(fig), use_container_width=True)

        with c2:

            fig = px.pie(regional, names="region", values="Revenue", hole=.62, title="Regional revenue share", color_discrete_sequence=["#258eff", "#9467ff", "#18c9c2", "#f1a640", "#ed67b8"])

            st.plotly_chart(style_chart(fig), use_container_width=True)

        st.dataframe(regional, use_container_width=True, hide_index=True)



# =========================================================

# AI ASSISTANT

# =========================================================

elif selected_page == "AI Assistant":

    section("Your AI data analyst", "CONVERSATIONAL ANALYTICS")

    st.markdown(

        '<div class="glass-card"><div class="card-title">✦ Ask questions. Discover insights.</div>'

        '<div class="card-sub">Ask about revenue, products, categories, regions, trends, or request recommendations based on the filtered data.</div></div>',

        unsafe_allow_html=True,

    )



    if "chat_history" not in st.session_state:

        st.session_state.chat_history = []

    if st.session_state.get("chat_signature") != current_signature:

        st.session_state.chat_history = []

        st.session_state.chat_signature = current_signature



    if st.button("✦ Generate business insights"):

        with st.spinner("Gemini is analyzing your dataset..."):

            try:

                insights = generate_business_insights(filtered.copy())

                st.session_state["business_insights"] = insights

                st.session_state["insights_signature"] = current_signature

                st.success("Business insights generated.")

            except Exception as exc:

                st.error(f"Could not generate insights: {exc}")



    if st.session_state.get("insights_signature") == current_signature:

        st.markdown(st.session_state.get("business_insights", ""))



    st.markdown("---")

    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])



    prompt = st.chat_input("Ask your data analyst a question...")

    if prompt:

        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("user"):

            st.markdown(prompt)

        with st.chat_message("assistant"):

            with st.spinner("Analyzing your data..."):

                try:

                    answer = ask_ai(prompt, filtered.copy())

                    st.markdown(answer)

                    st.session_state.chat_history.append({

                        "role": "assistant", "content": str(answer)

                    })

                except Exception as exc:

                    st.error(f"AI assistant error: {exc}")



# =========================================================

# DATA EXPLORER

# =========================================================

elif selected_page == "Data Explorer":

    section("Dataset explorer", "DATA QUALITY & DISCOVERY")

    tab1, tab2, tab3 = st.tabs(["▤ Data preview", "◈ Data quality", "∑ Statistics"])



    with tab1:

        st.dataframe(filtered, use_container_width=True, height=430)

        st.caption(f"{len(filtered):,} records · {len(filtered.columns)} columns")



    with tab2:

        quality = pd.DataFrame({

            "Column": filtered.columns,

            "Data type": [str(dtype) for dtype in filtered.dtypes],

            "Missing": [int(filtered[col].isna().sum()) for col in filtered.columns],

            "Missing %": [round(float(filtered[col].isna().mean() * 100), 2) for col in filtered.columns],

            "Unique": [int(filtered[col].nunique(dropna=True)) for col in filtered.columns],

        })

        st.dataframe(quality, use_container_width=True, hide_index=True)



        q1, q2, q3 = st.columns(3)

        missing_count = int(filtered.isna().sum().sum())

        duplicate_count = int(filtered.duplicated().sum())

        completeness = 100 * (1 - missing_count / max(filtered.size, 1))

        with q1:

            metric_card("!", "MISSING CELLS", number(missing_count), "Across current view", "#ffb45f")

        with q2:

            metric_card("⧉", "DUPLICATE ROWS", number(duplicate_count), "Exact duplicate rows", "#9b78ff")

        with q3:

            metric_card("✓", "COMPLETENESS", f"{completeness:.1f}%", "Non-missing cells", "#22d6a0")



    with tab3:

        st.dataframe(filtered.describe(include="all").transpose(), use_container_width=True)



# =========================================================

# REPORTS & EXPORT

# =========================================================

elif selected_page == "Reports & Export":

    section("Reports & exports", "SHARE YOUR ANALYSIS")

    st.markdown(

        '<div class="glass-card"><div class="card-title">Your report is ready to build</div>'

        '<div class="card-sub">Exports include the currently filtered records, KPI summary, and performance breakdowns.</div></div>',

        unsafe_allow_html=True,

    )



    insights_for_export = None

    if st.session_state.get("insights_signature") == current_signature:

        insights_for_export = st.session_state.get("business_insights")

        st.success("AI insights for this filter selection will be included.")

    else:

        st.info("Optional: generate AI insights in the AI Assistant section to include them.")



    try:

        excel_file = make_excel_report(filtered.copy(), insights_for_export)

        pdf_file = make_pdf_report(filtered.copy(), insights_for_export)

    except Exception as exc:

        st.error(f"Could not prepare reports: {exc}")

        st.stop()



    c1, c2 = st.columns(2)

    with c1:

        st.markdown("### 📘 Excel workbook")

        st.caption("Business summary, filtered data, and product/category/region analysis.")

        st.download_button(

            "Download Excel report",

            data=excel_file,

            file_name=f"data_analytics_report_{datetime.now():%Y%m%d_%H%M}.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            use_container_width=True,

        )

    with c2:

        st.markdown("### 📕 PDF report")

        st.caption("Executive summary and performance breakdowns in a shareable PDF.")

        st.download_button(

            "Download PDF report",

            data=pdf_file,

            file_name=f"data_analytics_report_{datetime.now():%Y%m%d_%H%M}.pdf",

            mime="application/pdf",

            use_container_width=True,

        )



st.markdown(

    '<div class="footer">DATA ANALYTICS STUDIO · ANALYTICS THAT MOVE BUSINESS FORWARD</div>',

    unsafe_allow_html=True,

)
