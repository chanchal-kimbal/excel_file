import json 
import pandas as pd
import os

RESULT_EXCEL_FILE = "test_results.xlsx"

COLUMNS = [
    "_Test ID",
    "Request Params",
    "Response",
    "Status Code",
    "Result",
    "Method",
    "Assertion Result",
    "Expected Result"
    
]

def load_result_excel():
    if os.path.exists(RESULT_EXCEL_FILE):
        df = pd.read_excel(RESULT_EXCEL_FILE)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = None
        return df
    else:
        return pd.DataFrame(columns=COLUMNS)
    




def save_test_result(test_id, request_params, response, status_code, result, method,expected_result,assertion_result):

    df = load_result_excel()

    new_row = {
        "_Test ID": test_id,
        "Request Params": json.dumps(request_params, indent=2),
        "Response": json.dumps(response, indent=2) if isinstance(response, dict) else response,
        "Status Code": status_code,
        "Result": result,
        "Method": method,
        "Assertion Result": assertion_result,
        "Expected Result": expected_result
        
    }

    if test_id in df["_Test ID"].values:
        idx = df.index[df["_Test ID"] == test_id][0]
        for col, val in new_row.items():
            df.at[idx, col] = val

        print(f"Updated result for Test ID: {test_id}")

    else:
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        print(f"Saved new result for Test ID: {test_id}")

    df.to_excel(RESULT_EXCEL_FILE, index=False)






