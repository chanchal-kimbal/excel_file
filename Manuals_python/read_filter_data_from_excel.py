import pandas as pd
import json


def read_excel(excel_path):
    
    df = pd.read_excel(excel_path)
    return df


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
            "_Expected Result": row.get("_Expected Result")
        }
        filtered_rows.append(filtered_row)

    output = {
        "_Test ID": data.get("_Test ID"),
        "filtered_data": filtered_rows
    }

    return json.dumps(output, indent=4)