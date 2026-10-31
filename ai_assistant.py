import os
import json
import pandas as pd
import numpy as np
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from data_analyzer import profile_dataset, classify_dataset, numeric_summary

load_dotenv()

def _get_client():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        try:
            key = st.secrets["GEMINI_API_KEY"]
        except (KeyError, FileNotFoundError):
            key = None
    if not key:
        raise ValueError("Gemini API key is not configured. Add GEMINI_API_KEY to .env or Streamlit Cloud Secrets.")
    return genai.Client(api_key=key)

def _safe_value(value):
    if pd.isna(value):
        return None
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if isinstance(value, np.generic):
        return value.item()
    return value

def build_dataset_context(df, max_rows=30):
    profile = profile_dataset(df)
    sample = df.head(max_rows).copy()
    sample = sample.replace({np.nan: None})
    records = [{str(k): _safe_value(v) for k, v in row.items()} for row in sample.to_dict(orient="records")]
    stats = numeric_summary(df).to_dict(orient="records")
    context = {
        "dataset_type": classify_dataset(df, profile["roles"]),
        "shape": {"rows": len(df), "columns": len(df.columns)},
        "columns": [{"name": str(c), "dtype": str(df[c].dtype), "missing": int(df[c].isna().sum()), "unique": int(df[c].nunique(dropna=True))} for c in df.columns],
        "numeric_summary": stats,
        "sample_rows": records,
    }
    return context

def _ask_gemini(prompt, df, task="answer"):
    context = build_dataset_context(df)
    system = (
        "You are DATA ANALYTICS STUDIO, a careful senior data analyst. "
        "Analyze only the supplied dataset context. The sample rows are not the entire dataset; "
        "use full-dataset numeric summaries for totals and averages when provided. "
        "Never invent calculations, claim a sample statistic is a full-data statistic, or assume column meanings. "
        "State limitations clearly. Use concise Markdown, explain insights in plain language, "
        "and make recommendations only when supported by the data."
    )
    client = _get_client()
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
        contents=f"Task: {task}\n\nDataset context (JSON):\n{json.dumps(context, default=str, ensure_ascii=False)}\n\nUser request:\n{prompt}",
        config=types.GenerateContentConfig(system_instruction=system, temperature=0.2),
    )
    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")
    return response.text

def ask_ai(question, df):
    return _ask_gemini(question, df, "Answer the user's question about this dataset.")

def generate_business_insights(df):
    if df is None or df.empty:
        raise ValueError("The uploaded dataset is empty.")
    prompt = (
        "Create a dataset-specific analysis with: 1) dataset overview and likely domain, "
        "2) important numeric findings, 3) notable category or group patterns if available, "
        "4) date trends if a date field exists, 5) data-quality observations, "
        "6) up to five practical recommendations. If the dataset is not business data, "
        "call this a general data analysis rather than forcing business or sales terminology."
    )
    return _ask_gemini(prompt, df, "Generate an insight report.")
