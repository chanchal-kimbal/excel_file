from typing import List, TypedDict, Union
import pandas as pd
import re
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent 
from langchain_core.messages import HumanMessage # Ensure HumanMessage is imported here
from ollama_setup import *
from langchain_core.tools import tool
import json


def is_date_value(value: str) -> bool:
    if pd.isna(value):
        return False

    value = str(value).strip()

    try:
        parsed = json.loads(value)
        if isinstance(parsed, dict) and "From" in parsed and "To" in parsed:
            return True
    except Exception:
        pass

    parsed_date = pd.to_datetime(value, errors="coerce")
    return not pd.isna(parsed_date)

def execute_metre(meter_ids, date_values, aligned_df):
    column_name = "_Test Data"

    df = aligned_df.copy()

    if column_name not in df.columns:
        raise KeyError(f"Column '{column_name}' not found")

    if "_Test ID" not in df.columns:
        raise KeyError("Column '_Test ID' not found")

    ids = df["_Test ID"]

    for idx, text in enumerate(df[column_name].astype(str)):
        meter_number = meter_ids[idx]
        input_date = date_values[idx]

        if pd.isna(meter_number):
            continue

        text = re.sub(
            r"meterNo:\s*\S+",
            f"meterNo: {meter_number}",
            text
        )

        def replace_date(match):
            detected_value = match.group(2)
            if is_date_value(detected_value):
                return match.group(1) + input_date + match.group(3)
            return match.group(0)

        pattern = r"(commandValue:\s*)(.*?)(\n(?:isDlms|$))"
        text = re.sub(pattern, replace_date, text, flags=re.S)

        text = re.sub(
            r'commandValue:\s*\n\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            r'commandValue: \1',
            text
        )

        df.at[idx, column_name] = text

    return df, ids


def extract_by_test_id(df, test_id_value):
    result_df = df[df["_Test ID"] == test_id_value]

    if result_df.empty:
        return {"error": "Test ID not found", "test_id": test_id_value}

    return {
        "_Test ID": test_id_value,
        "data": result_df.to_dict(orient="records")
    }


def filter_test_fields(result):
    if "error" in result:
        return result

    filtered = []
    for row in result.get("data", []):
        filtered.append({
            "_Test ID": row.get("_Test ID"),
            "_Test Data": row.get("_Test Data"),
            "_Status code": row.get("_Status code"),
            "API Type": row.get("API Type"),
            "URL": row.get("URL"),
            "_Expected Result": row.get("_Expected Result"),
            "_desc":row.get("_desc")
        })

    return {
        "_Test ID": result.get("_Test ID"),
        "filtered_data": filtered
    }


@tool
def execute_excel_test_pipeline(
    aligned_df: pd.DataFrame,
    meter_ids: list,
    date_values: list,
):
    """
    Executes Excel test pipeline using prepared state data
    """

    if aligned_df is None or aligned_df.empty:
        raise ValueError("❌ aligned_df is required")

    if not meter_ids or not date_values:
        raise ValueError("❌ meter_ids and date_values cannot be empty")

    if len(meter_ids) != len(date_values):
        raise ValueError("❌ meter_ids and date_values length mismatch")

    df, test_ids = execute_metre(
        meter_ids=meter_ids,
        date_values=date_values,
        aligned_df=aligned_df
    )

    final_output = []

    for test_id in test_ids:
        extracted = extract_by_test_id(df, test_id)
        filtered = filter_test_fields(extracted)
        final_output.append(filtered)

    return json.dumps(final_output, indent=4)



system_prompt="""

You are a Planning Agent in a multi-agent automated test execution system.

Your responsibility is to transform fetched execution inputs into a concrete, ordered execution plan.

You must:

Read meter_ids, communication_dates, and contextual test definitions from the shared state.

Generate a complete and valid list of test cases to be executed, strictly based on the provided inputs.

Produce a deterministic planned_tests structure that downstream execution agents can consume directly.

Ensure each planned test contains all required fields (test metadata, API details, parameters, and expectations).

Preserve logical execution order and avoid duplicate or redundant test generation.

Never invent, assume, or hallucinate test data or parameters.

Never perform API calls or execution logic.

Write only the planned_tests key back into the state.

Do not modify, delete, or rename any other state fields.

If required inputs are missing, incomplete, or inconsistent, fail immediately with a clear and explicit error.

Your output must be precise, reproducible, and fully compatible with the execution agent.

"""



def plan_agent():
    llm = ChatOllama(model="llama3.1:8B",temperature=0.2)
    tools = [execute_excel_test_pipeline]
    understanding_agent = create_react_agent(model=llm,tools=tools,name="plan_agent",prompt=system_prompt)
    return understanding_agent


def planning_agent(state):
    aligned_df = state.get("aligned_df")
    meter_ids = state.get("meter_ids")
    communication_dates = state.get("communication_dates")

    if aligned_df is None:
        raise RuntimeError("❌ aligned_df missing in planning_agent")

    if not meter_ids or not communication_dates:
        raise RuntimeError("❌ meter_ids or communication_dates missing")

    result = execute_excel_test_pipeline.invoke({
        "aligned_df": aligned_df,
        "meter_ids": meter_ids,
        "date_values": communication_dates
    })

    state["execution_result"] = result
    return state










































