import re
import pandas as pd
import numpy as np

ALIASES = {
    "date": ["date", "order date", "transaction date", "created at", "timestamp", "month"],
    "revenue": ["revenue", "sales", "sales amount", "total sales", "amount", "total amount", "value", "profit", "income", "cost", "price"],
    "quantity": ["quantity", "qty", "units", "count", "volume"],
    "product": ["product", "product name", "item", "item name", "service"],
    "category": ["category", "department", "segment", "type", "class"],
    "region": ["region", "location", "city", "state", "country", "territory"],
    "customer": ["customer", "customer name", "client", "user", "employee", "employee name"],
}

def normalize_columns(df):
    """Clean column labels without forcing every dataset into a sales schema."""
    result = df.copy()
    cleaned = []
    used = {}
    for col in result.columns:
        name = re.sub(r"[^a-zA-Z0-9]+", "_", str(col).strip().lower()).strip("_")
        name = name or "column"
        count = used.get(name, 0)
        used[name] = count + 1
        cleaned.append(name if count == 0 else f"{name}_{count+1}")
    result.columns = cleaned
    return result

def detect_column_roles(df):
    roles = {}
    normalized = {str(c).lower().replace("_", " "): c for c in df.columns}
    for role, aliases in ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                roles[role] = normalized[alias]
                break
    date_cols = []
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    for col in df.columns:
        if col not in date_cols and ("date" in str(col).lower() or "time" in str(col).lower()):
            parsed = pd.to_datetime(df[col], errors="coerce")
            if parsed.notna().mean() >= 0.6:
                date_cols.append(col)
    if "date" not in roles and date_cols:
        roles["date"] = date_cols[0]
    return {
        "roles": roles,
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "date_columns": date_cols,
    }

def profile_dataset(df):
    if df is None or df.empty:
        raise ValueError("The uploaded dataset has no rows.")
    numeric = df.select_dtypes(include="number")
    categorical = df.select_dtypes(include=["object", "category", "bool"])
    missing = int(df.isna().sum().sum())
    cells = int(df.shape[0] * df.shape[1])
    info = pd.DataFrame({
        "Column": df.columns,
        "Data Type": [str(df[c].dtype) for c in df.columns],
        "Missing Values": [int(df[c].isna().sum()) for c in df.columns],
        "Unique Values": [int(df[c].nunique(dropna=True)) for c in df.columns],
    })
    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "missing": missing,
        "duplicates": int(df.duplicated().sum()),
        "completeness": round(100 * (1 - missing / max(cells, 1)), 2),
        "numeric_columns": numeric.columns.tolist(),
        "categorical_columns": categorical.columns.tolist(),
        "column_info": info,
        "statistics": df.describe(include="all").transpose(),
        **detect_column_roles(df),
    }

def classify_dataset(df, roles=None):
    roles = roles or detect_column_roles(df)["roles"]
    cols = set(df.columns)
    text = " ".join(map(str, cols))
    if any(x in text for x in ["employee", "salary", "attrition", "department", "hire_date"]):
        return "HR / Employee Analytics"
    if any(x in text for x in ["campaign", "click", "impression", "conversion", "lead", "ad_spend"]):
        return "Marketing Analytics"
    if any(x in text for x in ["expense", "profit", "income", "balance", "budget", "cost"]):
        return "Finance Analytics"
    if any(x in text for x in ["stock", "inventory", "warehouse", "sku"]):
        return "Inventory Analytics"
    if "revenue" in roles or ("quantity" in roles and ("unit_price" in cols or "price" in cols)):
        return "Sales / Business Analytics"
    if roles.get("date") and len(df.select_dtypes(include="number").columns):
        return "Time-Series / Operational Analytics"
    return "General Dataset Analytics"

def analyze_dataset(df):
    return profile_dataset(df)

def numeric_summary(df):
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    rows = []
    for col in numeric_cols:
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(series):
            rows.append({
                "Metric": col,
                "Total": float(series.sum()),
                "Average": float(series.mean()),
                "Median": float(series.median()),
                "Minimum": float(series.min()),
                "Maximum": float(series.max()),
            })
    return pd.DataFrame(rows)

def top_categories(df, column, value_column=None, limit=10):
    if column not in df.columns:
        return pd.DataFrame()
    if value_column in df.select_dtypes(include="number").columns:
        result = df.groupby(column, dropna=False)[value_column].sum().sort_values(ascending=False).head(limit)
        return result.rename("Total").reset_index()
    return df[column].fillna("(Missing)").astype(str).value_counts().head(limit).rename_axis(column).reset_index(name="Records")

# Backwards-compatible sales helpers. They only work when relevant fields exist.
def prepare_sales_data(df):
    out = df.copy()
    if "revenue" not in out.columns:
        if {"quantity", "unit_price"}.issubset(out.columns):
            out["revenue"] = pd.to_numeric(out["quantity"], errors="coerce") * pd.to_numeric(out["unit_price"], errors="coerce")
        else:
            raise ValueError("This dataset does not contain revenue or quantity and unit_price fields.")
    return out

def get_total_revenue(df):
    return float(prepare_sales_data(df)["revenue"].sum())

def get_average_order_value(df):
    sales = prepare_sales_data(df)
    return float(sales["revenue"].mean()) if len(sales) else 0

def get_top_products(df, top_n=5):
    sales = prepare_sales_data(df)
    if "product" not in sales:
        raise ValueError("Product column is missing.")
    return sales.groupby("product")["revenue"].sum().nlargest(top_n).reset_index()

def get_category_performance(df):
    sales = prepare_sales_data(df)
    if "category" not in sales:
        raise ValueError("Category column is missing.")
    return sales.groupby("category")["revenue"].sum().sort_values(ascending=False).reset_index()

def get_region_performance(df):
    sales = prepare_sales_data(df)
    if "region" not in sales:
        raise ValueError("Region column is missing.")
    return sales.groupby("region")["revenue"].sum().sort_values(ascending=False).reset_index()

def get_monthly_sales(df):
    sales = prepare_sales_data(df)
    date_col = "order_date" if "order_date" in sales else "date" if "date" in sales else None
    if not date_col:
        raise ValueError("Date column is missing.")
    dates = pd.to_datetime(sales[date_col], errors="coerce")
    temp = sales.assign(month=dates.dt.to_period("M").astype(str))
    return temp.dropna(subset=[date_col]).groupby("month")["revenue"].sum().reset_index()
