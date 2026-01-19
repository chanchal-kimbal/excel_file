import json
import re
import requests
import pandas as pd
import time
from typing import TypedDict, List, Any

def parse_get_params(raw_text: str) -> dict:
    if not raw_text or not raw_text.strip():
        return {}

    raw_text = raw_text.strip()

    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, dict):
            return parsed
    except:
        pass

    params = {}
    lines = raw_text.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if not line or ":" not in line:
            i += 1
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if value == "":
            buffer = []
            i += 1

            while i < len(lines):
                next_line = lines[i].strip()

                if ":" in next_line and not next_line.startswith("{"):
                    break

                buffer.append(next_line)
                i += 1

            raw_block = "\n".join(buffer).strip()

            try:
                params[key] = json.loads(raw_block)
            except:
                params[key] = raw_block

            continue

        val_lower = value.lower()
        if val_lower == "true":
            value = True
        elif val_lower == "false":
            value = False
        else:
            try:
                value = int(value)
            except:
                try:
                    value = float(value)
                except:
                    pass

        params[key] = value
        i += 1

    return params


def _normalize_datetime(value):

    if isinstance(value, str):
        if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            return f"{value} 00:00:00"

    return value

def normalize_params(params: dict) -> dict:
    final_params = {}

    for key, value in params.items():
        if isinstance(value, dict):
            for sub_key, sub_val in value.items():
                final_params[f"{key}{sub_key}"] = _normalize_datetime(sub_val)
            continue
        if isinstance(value, str):
            match = re.match(
                r"^\s*(\d{4}-\d{2}-\d{2})(?:\s+\d{2}:\d{2}:\d{2})?\s+to\s+"
                r"(\d{4}-\d{2}-\d{2})(?:\s+\d{2}:\d{2}:\d{2})?\s*$",
                value,
                re.IGNORECASE
            )
            if match:
                final_params[f"{key}From"] = _normalize_datetime(match.group(1))
                final_params[f"{key}To"] = _normalize_datetime(match.group(2))
                continue

        final_params[key] = _normalize_datetime(value)

    return final_params



def generate_access_token(client_id,username,password):

    try:

        url = "https://ehes-qa-cmd.kimbal.io/token"  

        payload = {
            "grant_type": "password",
            "username": f"{username}",
            "password": f"{password}",
            "client_id": f"{client_id}",
            "client_secret": "",
            "refresh_token": ""
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(url, data=payload, headers=headers)

        if response.status_code != 200:
            print("Response Text:", response.text)
            return None

        token_response = response.json()
        access_token = token_response.get("access_token")

        return access_token
    
    except Exception as e:
        return f"Error: {e}"


    
   
def build_assertion_result(status_code, response, expected):
  
    if expected is None:
        return "No expected result provided", "FAIL"

    if isinstance(expected, str):
        try:
            expected = json.loads(expected)
        except Exception:
            return "Expected result is not valid JSON", "FAIL"

    if isinstance(response, str):
        try:
            response = json.loads(response)
        except Exception:
            return "Response is not valid JSON", "FAIL"

    expected_status = expected.get("status", 200)
    
    if status_code != expected_status:
        return (
            f"Status code mismatch | Expected: {expected_status} | Actual: {status_code}",
            "FAIL"
        )
    
    if status_code == 200:
        exp_success = expected.get("success")
        act_success = response.get("success")
        expected_requestId_id = expected.get("requestId")

        types = type(expected_requestId_id)

        if exp_success == act_success and expected_requestId_id != 0:
            return (
                f"Status code match with 200 | requestId > 0 ({types}) | Message Success : True",
                "PASS"
            )
        

    if response.get("status") and expected.get("status") and status_code == 400:
        return ("Status code match with 400", "PASS")
    else:
        return (
            f"Status code mismatch | Expected: {expected_status} |","FAIL" #Actual: {status_code}
        )

   


def result_from_assertion_text(value):
    if not value:
        return "FAIL"

    if isinstance(value, tuple):
        value = " ".join(map(str, value))

    if isinstance(value, list):
        value = " ".join(map(str, value))

    value = str(value).lower()

    if "false" in value or "mismatch" in value or "fail" in value:
        return "FAIL"

    return "PASS"
    

def run_requests_from_json(item, client_id, username, password):
    """
    item = one element from filtered_data
    """

    test_id = item.get("_Test ID")
    url = item.get("URL")
    method = item.get("API Type", "GET").upper()
    expected_result = item.get("_Expected Result")
    description = item.get("_desc")
    raw_body = item.get("_Test Data", "{}")
    

    if method == "GET":
        body = parse_get_params(raw_body)
        body = normalize_params(body)
    else:
        try:
            body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        except Exception:
            body = {}

    if body.get("isDlms") == "":
        body["isDlms"] = None

    token = generate_access_token(client_id, username, password)
    if not token:
        return {
            "test_id": test_id,
            "response": {"error": "Token generation failed"},
            "status_code": None,
            "expected_result": expected_result,
            "method": method,
            "description": None
        }

    headers = {"Authorization": f"Bearer {token}"}

    try:
        if method == "GET":
            response = requests.get(url, params=body, headers=headers)
        else:
            response = requests.request(method, url, json=body, headers=headers)

        try:
            response_json = response.json()
        except Exception:
            response_json = {"raw_response": response.text}

        return {
            "test_id": test_id,
            "request": body,
            "response": response_json,
            "status_code": response.status_code,
            "expected_result": expected_result,
            "method": method,
            "description": description
        }

    except Exception as e:
        return {
            "test_id": test_id,
            "response": {"error": str(e)},
            "status_code": None,
            "expected_result": expected_result,
            "method": method,
            "description": description
        }



def run_all_test(state):
    execution_result = state.get("execution_result")
    client_id = state.get("client_id")
    username = state.get("username")
    password = state.get("password")

    if not execution_result:
        raise RuntimeError("❌ execution_result missing in state")

    if isinstance(execution_result, str):
        execution_result = json.loads(execution_result)

    results = []

    for test_block in execution_result:
        test_id = test_block.get("_Test ID")
        # description = test_block.get("_desc")
        filtered_data = test_block.get("filtered_data", [])

        for item in filtered_data:
            start_time = time.time()

            result = run_requests_from_json(
                item, client_id, username, password
            )

            taking_time = round(time.time() - start_time, 3)

            assertion_text = build_assertion_result(
                result["status_code"],
                result["response"],
                result["expected_result"]
            )

            result_value = result_from_assertion_text(assertion_text)

            results.append({
                "test_id": test_id,
                "description": result.get("description"),
                "request_parameter": result.get("request"),
                "response": result.get("response"),
                "expected_result": result.get("expected_result"),
                "status_code": result.get("status_code"),
                "result": result_value,
                "assertion_result": assertion_text,
                "Taking_time(seconds)": taking_time
            })

    state["final_results_df"] = pd.DataFrame(results)
    return state



def execution_Agents(state):
    execution_result = state.get("execution_result")

    if not execution_result:
        raise RuntimeError("❌ execution_result not found in execution agent")

    state = run_all_test(state)

    df = state.get("final_results_df")
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            f"❌ final_results_df must be pandas DataFrame, got {type(df)}"
        )

    return state













