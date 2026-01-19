
import pandas as pd
import json
import json
import requests

def read_excel(excel_path):
    
    df = pd.read_excel(excel_path)
    return df


def get_all_column_names(df):
    return list(df.columns)


def extract_columns(df, column_names):

    missing_cols = [col for col in column_names if col not in df.columns]
    if missing_cols:
        raise ValueError(f"❌ Missing columns in Excel file: {missing_cols}")

    return df[column_names]


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





#### working version ####
def run_requests_from_json(data):

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

        try:
            if method == "GET":
                response = requests.get(url, params=body)
            else:
                response = requests.request(method, url, json=body)

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




# query = input("\nYou: ")

# test_ids = [item.strip() for item in query.split(",")]

# excel_file = "API_Authentication_Login.xlsx"
# df = read_excel(excel_file)

# print("\nJSON output based on Test ID:")

# for test_id_value in test_ids:
#     result = extract_by_test_id(df, test_id_value)
#     # print(result)
#     x1=filter_test_fields(result)
#     print(x1)

# if isinstance(x1, str):
#     data_dict = json.loads(x1)
# else:
#     data_dict = x1

# response_json = run_requests_from_json(data_dict)
# # print("\nFinal Response JSON:",response_json)

# def get_tokens_from_response(response_json):
#      tokens = {}
#      if response_json:
#          token = response_json.get("accessToken")
#          tokens.update({"accessToken": token})
#      return tokens

# print("\nExtracted Tokens:", get_tokens_from_response(response_json))












def get_tokens_from_response(query):

    # query = input("\nYou: ")
    test_ids = [item.strip() for item in query.split(",")]

    excel_file = "API_Authentication_Login.xlsx"
    df = read_excel(excel_file)

    print("\nJSON output based on Test ID:")

    for test_id_value in test_ids:
        result = extract_by_test_id(df, test_id_value)
        # print(result)
        x1=filter_test_fields(result)
        print(x1)

    if isinstance(x1, str):
        data_dict = json.loads(x1)
    else:
        data_dict = x1

    response_json = run_requests_from_json(data_dict)
    tokens = {}
    if response_json:
         token = response_json.get("accessToken")
         tokens.update({"accessToken": token})
    return tokens,test_ids




# query = input("\nYou: ")
# print("\nExtracted Tokens:", get_tokens_from_response(query))



# token = get_tokens_from_response()
# token = token.get("accessToken")
# print("\nExtracted Token:", token)
        





