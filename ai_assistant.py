import os

import json

import time

import pandas as pd

import numpy as np
import streamlit as st

from dotenv import load_dotenv

from google import genai

from google.genai import types

from data_analyzer import (

    get_total_revenue,

    get_average_order_value,

    get_top_products,

    get_category_performance,

    get_region_performance,

    get_monthly_sales

)

# --------------------------------------------------

# 1. GEMINI CONFIGURATION

# --------------------------------------------------

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

# On Streamlit Community Cloud, read the key from App settings > Secrets.
if not API_KEY:
    try:
        API_KEY = st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        API_KEY = None

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. Configure it in your local .env file "
        "or Streamlit Community Cloud Secrets."
    )

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

client = genai.Client(api_key=API_KEY)

# --------------------------------------------------

# 2. CONVERT PANDAS / NUMPY VALUES INTO PYTHON VALUES

# --------------------------------------------------

def convert_to_python_types(data):

    if isinstance(data, pd.DataFrame):

        return [

            convert_to_python_types(row)

            for row in data.to_dict(orient="records")

        ]

    if isinstance(data, pd.Series):

        return convert_to_python_types(data.to_dict())

    if isinstance(data, dict):

        return {

            str(key): convert_to_python_types(value)

            for key, value in data.items()

        }

    if isinstance(data, (list, tuple)):

        return [

            convert_to_python_types(value)

            for value in data

        ]

    if isinstance(data, np.ndarray):

        return convert_to_python_types(data.tolist())

    if isinstance(data, np.generic):

        return convert_to_python_types(data.item())

    if isinstance(data, (pd.Timestamp,)):

        return data.isoformat()

    if isinstance(data, float) and not np.isfinite(data):

        return None

    if pd.isna(data) if not isinstance(data, (str, bytes)) else False:

        return None

    return data

# --------------------------------------------------

# 3. GEMINI API WITH AUTOMATIC RETRY

# --------------------------------------------------

def generate_with_retry(contents, config=None, max_attempts=3):

    last_error = None

    for attempt in range(max_attempts):

        try:

            response = client.models.generate_content(

                model=MODEL_NAME,

                contents=contents,

                config=config

            )

            if not response.text and not response.function_calls:

                raise ValueError("Gemini returned an empty response.")

            return response

        except Exception as error:

            last_error = error

            error_text = str(error)

            retryable = any(

                code in error_text

                for code in ["429", "500", "502", "503", "504"]

            )

            if not retryable:

                raise RuntimeError(

                    f"Gemini API error: {error}"

                ) from error

            if attempt < max_attempts - 1:

                wait_time = 2 ** (attempt + 1)

                print(

                    f"Gemini temporarily unavailable. "

                    f"Retrying in {wait_time} seconds..."

                )

                time.sleep(wait_time)

    raise RuntimeError(

        f"Gemini could not complete the request after "

        f"{max_attempts} attempts. Last error: {last_error}"

    )

# --------------------------------------------------

# 4. DEFINE FUNCTIONS GEMINI CAN USE

# --------------------------------------------------

tools = [

    types.Tool(

        function_declarations=[

            types.FunctionDeclaration(

                name="get_total_revenue",

                description="Calculate total sales revenue.",

                parameters=types.Schema(

                    type=types.Type.OBJECT,

                    properties={}

                )

            ),

            types.FunctionDeclaration(

                name="get_average_order_value",

                description="Calculate average revenue per data row.",

                parameters=types.Schema(

                    type=types.Type.OBJECT,

                    properties={}

                )

            ),

            types.FunctionDeclaration(

                name="get_top_products",

                description="Find the top-selling products.",

                parameters=types.Schema(

                    type=types.Type.OBJECT,

                    properties={

                        "top_n": types.Schema(

                            type=types.Type.INTEGER,

                            description="Number of top products to return."

                        )

                    },

                    required=[]

                )

            ),

            types.FunctionDeclaration(

                name="get_category_performance",

                description="Calculate sales performance by category.",

                parameters=types.Schema(

                    type=types.Type.OBJECT,

                    properties={}

                )

            ),

            types.FunctionDeclaration(

                name="get_region_performance",

                description="Calculate sales performance by region.",

                parameters=types.Schema(

                    type=types.Type.OBJECT,

                    properties={}

                )

            ),

            types.FunctionDeclaration(

                name="get_monthly_sales",

                description="Calculate monthly sales performance.",

                parameters=types.Schema(

                    type=types.Type.OBJECT,

                    properties={}

                )

            )

        ]

    )

]

# --------------------------------------------------

# 5. EXECUTE GEMINI FUNCTION CALLS

# --------------------------------------------------

def execute_function(function_name, arguments, df):

    arguments = arguments or {}

    if function_name == "get_total_revenue":

        result = get_total_revenue(df)

    elif function_name == "get_average_order_value":

        result = get_average_order_value(df)

    elif function_name == "get_top_products":

        top_n = int(arguments.get("top_n", 5))

        top_n = max(1, min(top_n, 20))

        result = get_top_products(df, top_n=top_n)

    elif function_name == "get_category_performance":

        result = get_category_performance(df)

    elif function_name == "get_region_performance":

        result = get_region_performance(df)

    elif function_name == "get_monthly_sales":

        result = get_monthly_sales(df)

    else:

        raise ValueError(

            f"Unknown function requested: {function_name}"

        )

    return convert_to_python_types(result)

# --------------------------------------------------

# 6. AI CHAT ASSISTANT

# --------------------------------------------------

def ask_ai(question, df):

    system_instruction = """

    You are an expert AI Data Analyst Assistant.

    Your job is to help users understand their uploaded datasets.

    Rules:

    1. Use the available Python functions to calculate actual results.

    2. Never invent revenue, sales, products, or statistics.

    3. Explain results in simple business language.

    4. Use tables or bullet points when useful.

    5. Give practical business recommendations when appropriate.

    6. If a question cannot be answered using the available data,

       clearly explain the limitation.

    7. Do not claim that a calculation was performed if it was not.

    """

    config = types.GenerateContentConfig(

        system_instruction=system_instruction,

        tools=tools,

        temperature=0.2

    )

    contents = [

        types.Content(

            role="user",

            parts=[

                types.Part.from_text(text=question)

            ]

        )

    ]

    response = generate_with_retry(

        contents=contents,

        config=config

    )

    # Process function calls, if Gemini requests them.

    function_calls = response.function_calls or []

    if function_calls:

        # Preserve Gemini's original function-call response.

        contents.append(response.candidates[0].content)

        function_response_parts = []

        for call in function_calls:

            try:

                result = execute_function(

                    function_name=call.name,

                    arguments=call.args,

                    df=df

                )

                function_result = {

                    "result": result

                }

            except Exception as error:

                function_result = {

                    "error": str(error)

                }

            function_response_parts.append(

                types.Part.from_function_response(

                    name=call.name,

                    response=function_result

                )

            )

        contents.append(

            types.Content(

                role="user",

                parts=function_response_parts

            )

        )

        # Ask Gemini to explain the calculated results.

        final_response = generate_with_retry(

            contents=contents,

            config=config

        )

        return final_response.text or "I could not generate an answer."

    return response.text or "I could not generate an answer."

# --------------------------------------------------

# 7. GENERATE AI BUSINESS INSIGHTS

# --------------------------------------------------

def generate_business_insights(df):

    if df is None or df.empty:

        raise ValueError("The uploaded dataset is empty.")

    required_columns = ["quantity", "unit_price"]

    missing_columns = [

        column

        for column in required_columns

        if column not in df.columns

    ]

    if missing_columns:

        raise ValueError(

            "Business insights require these columns: "

            + ", ".join(required_columns)

        )

    # Calculate business metrics using Python functions.

    business_data = {

        "total_revenue": get_total_revenue(df),

        "average_revenue_per_row": get_average_order_value(df),

        "top_products": get_top_products(df, top_n=5),

        "category_performance": get_category_performance(df),

        "region_performance": get_region_performance(df),

        "monthly_sales": get_monthly_sales(df)

    }

    # Convert Pandas and NumPy data into JSON-compatible values.

    business_data = convert_to_python_types(business_data)

    business_json = json.dumps(

        business_data,

        indent=2,

        ensure_ascii=False,

        allow_nan=False

    )

    prompt = f"""

    You are a professional Business Intelligence Analyst.

    Analyze the following sales dataset results.

    BUSINESS DATA:

    {business_json}

    Prepare a clear business performance report using these sections:

    ## 1. Overall Business Performance

    Explain total revenue and average revenue per data row.

    ## 2. Best Performing Products

    Identify the best-performing products and explain their contribution.

    ## 3. Category Performance

    Compare the different product categories.

    ## 4. Regional Performance

    Identify the strongest and weakest regions.

    ## 5. Monthly Sales Trends

    Explain the monthly sales pattern.

    Mention growth or decline only when supported by the data.

    ## 6. Five Actionable Business Recommendations

    Give five practical recommendations based on the available numbers.

    IMPORTANT:

    - Use only the supplied business data.

    - Do not invent missing information.

    - Do not assume that a trend will continue.

    - Clearly mention when the dataset is too small for a strong conclusion.

    - Use simple, professional language.

    - Format the answer using Markdown.

    """

    response = generate_with_retry(

        contents=prompt,

        config=types.GenerateContentConfig(

            temperature=0.3

        )

    )

    return response.text
