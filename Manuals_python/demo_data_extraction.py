import pandas as pd
import json
import json
import requests
from data_extration import get_tokens_from_response
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
            "URL": row.get("URL")
        }
        filtered_rows.append(filtered_row)

    output = {
        "_Test ID": data.get("_Test ID"),
        "filtered_data": filtered_rows
    }

    return json.dumps(output, indent=4)





def parse_get_params(raw_text):
    """
    Converts 'Key: Value' text into {'Key': 'Value'} dictionary
    """
    params = {}
    try:
        return json.loads(raw_text)
    except:
        pass

    if ":" in raw_text:
        pairs = raw_text.split(",")
        for p in pairs:
            if ":" in p:
                key, val = p.split(":", 1)
                params[key.strip()] = val.strip()
        return params

    return {} 


def run_requests_from_json(data,query):

    if "filtered_data" not in data:
        print("❌ Invalid JSON structure")
        return None

    final_response = None

    for item in data["filtered_data"]:
        test_id = item.get("_Test ID")
        url = item.get("URL")
        method = item.get("API Type", "GET").upper()
        expected_status = item.get("_Status code")

        raw_body = item.get("_Test Data", "{}")

        if method == "GET":
            body = parse_get_params(raw_body)
        else:
            try:
                body = json.loads(raw_body)
            except:
                print(f"❌ ERROR: Unable to parse JSON for test {test_id}")
                body = {}

        print(f"\n==============================")
        print(f" Running Test: {test_id}")
        print(f" URL: {url}")
        print(f" Method: {method}")
        print(f"==============================")

        token,_= get_tokens_from_response(query)
        token = token.get("accessToken")
        if token is None:
            print("❌ ERROR: No access token available")
            exit(1)
            
        headers = {"Authorization": f"Bearer {token}"} if token else {}


        try:
            if method == "GET":
                response = requests.get(url, params=body, headers=headers)
            else:
                response = requests.request(method, url, json=body, headers=headers)

            print("Status Code:", response.status_code)

            if expected_status and response.status_code == expected_status:
                print("✔ Status Matched")
            else:
                print("⚠ Expected:", expected_status)

            print("Response:")
            try:
                final_response = response.json()
                print(json.dumps(final_response, indent=4))
            except:
                final_response = response.text
                print(final_response)

        except Exception as e:
            print(f"❌ Request Failed: {e}")

    return final_response



query = input("\nYou: ")

excel_file = "API_Authentication_Login.xlsx"
df = read_excel(excel_file)

_,test_ids= get_tokens_from_response(query)

for test_id_value in test_ids:
    result = extract_by_test_id(df, test_id_value)
    # print(result)
    x1=filter_test_fields(result)
    # print(x1)

if isinstance(x1, str):
    data_dict = json.loads(x1)
else:
    data_dict = x1

response_json = run_requests_from_json(data_dict,query)
print("\nFinal Response JSON:",response_json)