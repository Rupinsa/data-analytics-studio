
import pandas as pd


# ==========================================
# 1. DATASET ANALYSIS
# ==========================================

def analyze_dataset(df):

    total_rows = len(df)
    total_columns = len(df.columns)

    total_missing = int(df.isnull().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    column_info = []

    for column in df.columns:
        column_info.append({
            "Column": column,
            "Data Type": str(df[column].dtype),
            "Missing Values": int(df[column].isnull().sum()),
            "Unique Values": int(df[column].nunique())
        })

    numerical_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    statistics = df.describe(
        include="all"
    ).fillna("N/A")

    total_cells = total_rows * total_columns

    completeness = (
        ((total_cells - total_missing) / total_cells) * 100
        if total_cells > 0 else 0
    )

    return {
        "total_rows": total_rows,
        "total_columns": total_columns,
        "total_missing": total_missing,
        "duplicate_rows": duplicate_rows,
        "completeness": round(completeness, 2),
        "numerical_columns": numerical_columns,
        "categorical_columns": categorical_columns,
        "column_info": pd.DataFrame(column_info),
        "statistics": statistics
    }


# ==========================================
# 2. PREPARE SALES DATA
# ==========================================

def prepare_sales_data(df):

    required_columns = ["quantity", "unit_price"]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"Required column '{column}' is missing."
            )

    sales_df = df.copy()

    sales_df["quantity"] = pd.to_numeric(
        sales_df["quantity"], errors="coerce"
    )

    sales_df["unit_price"] = pd.to_numeric(
        sales_df["unit_price"], errors="coerce"
    )

    sales_df["revenue"] = (
        sales_df["quantity"] * sales_df["unit_price"]
    )

    return sales_df


# ==========================================
# 3. TOTAL REVENUE
# ==========================================

def get_total_revenue(df):

    sales_df = prepare_sales_data(df)

    return round(sales_df["revenue"].sum(), 2)


# ==========================================
# 4. AVERAGE REVENUE
# ==========================================

def get_average_order_value(df):

    sales_df = prepare_sales_data(df)

    if len(sales_df) == 0:
        return 0

    return round(sales_df["revenue"].mean(), 2)


# ==========================================
# 5. TOP PRODUCTS
# ==========================================

def get_top_products(df, top_n=5):

    sales_df = prepare_sales_data(df)

    if "product" not in sales_df.columns:
        raise ValueError("Product column is missing.")

    return (
        sales_df.groupby("product")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )


# ==========================================
# 6. CATEGORY PERFORMANCE
# ==========================================

def get_category_performance(df):

    sales_df = prepare_sales_data(df)

    if "category" not in sales_df.columns:
        raise ValueError("Category column is missing.")

    return (
        sales_df.groupby("category")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )


# ==========================================
# 7. REGIONAL PERFORMANCE
# ==========================================

def get_region_performance(df):

    sales_df = prepare_sales_data(df)

    if "region" not in sales_df.columns:
        raise ValueError("Region column is missing.")

    return (
        sales_df.groupby("region")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )


# ==========================================
# 8. MONTHLY SALES
# ==========================================

def get_monthly_sales(df):

    sales_df = prepare_sales_data(df)

    if "order_date" not in sales_df.columns:
        raise ValueError("Order date column is missing.")

    sales_df["order_date"] = pd.to_datetime(
        sales_df["order_date"],
        errors="coerce"
    )

    sales_df = sales_df.dropna(
        subset=["order_date"]
    )

    sales_df["month"] = (
        sales_df["order_date"]
        .dt.to_period("M")
        .astype(str)
    )

    return (
        sales_df.groupby("month")["revenue"]
        .sum()
        .reset_index()
    )
