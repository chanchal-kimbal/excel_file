import pandas as pd
import json
import requests


from user_creds import get_tokens_from_response
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
        print("Invalid JSON structure")
        return None, None, None, None

    for item in data["filtered_data"]:
        test_id = item.get("_Test ID")
        url = item.get("URL")
        method = item.get("API Type", "GET").upper()
        expected_status = item.get("_Status code")
        expected_result = item.get("_Expected Result")
        
        raw_body = item.get("_Test Data", "{}")

        if method == "GET":
            body = parse_get_params(raw_body)
        else:
            try:
                body = json.loads(raw_body)
            except:
                print(f"ERROR: Unable to parse JSON for test {test_id}")
                body = {}

        body_demo=json.dumps(body, indent=4)
        print(f"\n==============================")
        print(f" test data: {body_demo}")
        print(f"\n==============================")
        print(f" Running Test: {test_id}")
        print(f" URL: {url}")
        print(f" Method: {method}")
        print(f"==============================")

        token = get_tokens_from_response().get("accessToken")
        if token is None:
            print("ERROR: No access token available")
            exit(1)
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        try:
            if method == "GET":
                response = requests.get(url, params=body, headers=headers)
            else:
                response = requests.request(method, url, json=body)

            status_code = response.status_code

            try:
                final_response = response.json()
            except:
                final_response = response.text

            if expected_status == status_code and status_code != 500:
                result = "PASS"
            else:
                result = "FAIL"

            print("Status Code:", status_code)
            print("Result:", result)

            return test_id, body, final_response, status_code,method,expected_result

        except Exception as e:
            print(f"Request Failed: {e}")
            return test_id, body, str(e), None

    return None, None, None, None