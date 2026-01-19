import pandas as pd
import json
import requests

from user_creds import get_tokens_from_response
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

        if method == "GET":
            body = parse_get_params(raw_body)
        else:
            try:
                body = json.loads(raw_body)
            except:
                print(f"❌ ERROR: Unable to parse JSON for test {test_id}")
                body = {}
                
        body_demo=json.dumps(body, indent=4)
        print(f"\n==============================")
        print(f" test data: {body_demo}")
        print(f"\n==============================")
        print(f" Running Test: {test_id}")
        print(f" URL: {url}")
        print(f" Method: {method}")
        print(f"==============================")

        token= get_tokens_from_response()
        token = token.get("accessToken")
        if token is None:
            print("❌ ERROR: No access token available")
            exit(1)
        headers = {"Authorization": f"Bearer {token}"} if token else {}


        try:
            if method == "GET":
                response = requests.get(url, params=body, headers=headers)
            else:
                response = requests.request(method, url, json=body)
                final_response = response.json()
    
                if final_response.get("accessToken") == None:
                    print("ERROR: No access token available")
                    # exit(1)

            if expected_status and response.status_code == expected_status:
                print("Status Matched with status code:",response.status_code)
                if response.status_code ==500:
                    print("Server Error encountered,Result:FAIL")
                else:
                    print("Result:PASS")
            else:
                print("Expected:", expected_status)


            try:
                final_response = response.json()
                # print(json.dumps(final_response, indent=4))
                return json.dumps(final_response, indent=4)
            except:
                final_response = response.text
                # print(final_response)
                return final_response


        except Exception as e:
            print(f"❌ Request Failed: {e}")

    return final_response



# query = input("\nYou: ")
# test_ids = [item.strip() for item in query.split(",")]
# excel_file = "master_file.xlsx"
# df = read_excel(excel_file)

# for test_id_value in test_ids:
#     result = extract_by_test_id(df, test_id_value)

#     x1=filter_test_fields(result)

# if isinstance(x1, str):
#     data_dict = json.loads(x1)
# else:
#     data_dict = x1

# response_json = run_requests_from_json(data_dict)
# print("\nFinal Response JSON:",response_json)






while True:
    query = input("\nYou: ")
    if query.lower() in ["exit", "quit"]:
        print("Exiting the program.")
        break
    if not query.strip():
        print("Please enter a valid Test ID or 'exit' to quit.")
        continue
    test_ids = [item.strip() for item in query.split(",")]
    excel_file = "master_file.xlsx"
    df = read_excel(excel_file)

    for test_id_value in test_ids:
        result = extract_by_test_id(df, test_id_value)

        x1=filter_test_fields(result)

        if isinstance(x1, str):
            data_dict = json.loads(x1)
        else:
            data_dict = x1

        response_json = run_requests_from_json(data_dict)
        print("\nFinal Response JSON:",response_json)




# EHES_LGN_TC_2
# EHES_APPS_TC_2