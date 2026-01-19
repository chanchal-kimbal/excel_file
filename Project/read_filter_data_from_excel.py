import pandas as pd
import json
import re
from is_excel_header_validate import *

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


def update_json_date_range(json_text: str, input_date: str) -> str:
    try:
        parsed = json.loads(json_text)

        if isinstance(parsed, dict) and "From" in parsed and "To" in parsed:
            parsed["From"] = input_date
            parsed["To"] = input_date
            return json.dumps(parsed, separators=(",", ":"))
    except Exception:
        pass

    return json_text


def execute_metre(meter_ids, date_values, excel_file):
    column_name = "_Test Data"

    df = pd.read_excel(excel_file)
    df = align_excel_headers(df)

    if column_name not in df.columns:
        raise KeyError(f"Column '{column_name}' not found")

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
            detected_value = match.group(2).strip()

            try:
                parsed = json.loads(detected_value)
                if isinstance(parsed, dict) and "From" in parsed and "To" in parsed:
                    updated_json = update_json_date_range(detected_value, input_date)
                    return match.group(1) + updated_json + match.group(3)
            except Exception:
                pass

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

    if "_Test ID" not in df.columns:
        raise ValueError("❌ '_Test ID' column not found in Excel file")

    result_df = df[df["_Test ID"] == test_id_value]

    if result_df.empty:
        return json.dumps({"error": "Test ID not found", "test_id": test_id_value}, indent=4)

    result_json = result_df.to_dict(orient="records")

    output = {
        "_Test ID": test_id_value,
        "data": result_json
    }

    return json.dumps(output, indent=4)

def filter_test_fields(json_result):
    
    data = json.loads(json_result)

    if "error" in data:
        return json.dumps(data, indent=4)

    filtered_rows = []

    for row in data.get("data", []):
        filtered_row = {
            "_Test ID": row.get("_Test ID"),
            "_Test Data": row.get("_Test Data"),
            "_Status code": row.get("_Status code"),
            "API Type" :row.get("API Type"),
            "URL": row.get("URL"),
            "_Expected Result": row.get("_Expected Result"),
            "_desc":row.get("_desc"),
        }
        filtered_rows.append(filtered_row)

    output = {
        "_Test ID": data.get("_Test ID"),
        "filtered_data": filtered_rows
    }

    return json.dumps(output, indent=4)












