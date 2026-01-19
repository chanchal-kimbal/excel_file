
# import json

# from save_data_in_excel import save_test_result
# from read_filter_data_from_excel import *
# from Hit_api import *


import pandas as pd
import json
import re

def normalize_response(data):
    
    if isinstance(data, (dict, list)):
        return data

    if not isinstance(data, str):
        return None

    data = data.strip()

    try:
        return json.loads(data)
    except json.JSONDecodeError:
        pass

    json_match = re.search(r'(\{.*\}|\[.*\])', data, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            return None

    return None



def check_app_settings(expected_result, method, actual_status_code):
    expected_result = normalize_response(expected_result)

    if expected_result is None:
        return "Invalid or non-JSON response"

    if method == "GET":
        app_settings = expected_result.get("appSettingsList")

        if isinstance(app_settings, list):
            if len(app_settings) == 0:
                msg = f"appSettingsList is EMPTY | Status: {False} | StatusCode: {actual_status_code}"
            else:
                msg = f"appSettingsList NOT EMPTY | Status: {True} | StatusCode: {actual_status_code}"
        else:
            msg = "appSettingsList key missing"

        print(msg)
        return msg

    elif method == "POST":
        expected_status = expected_result.get("status")
        message = expected_result.get("message")
        access_token = expected_result.get("accessToken")

        status_match = actual_status_code == expected_status

        status_msg = (
            f"Status code match with {actual_status_code}"
            if status_match
            else f"Status mismatch | Expected {expected_status}, Got {actual_status_code}"
        )

        token_msg = (
            "accessToken is NULL"
            if access_token in [None, ""]
            else " accessToken generated"
        )

        final_msg = f"{status_msg} | {token_msg} | Message: {message}"
        print(final_msg)
        return final_msg

    return None



                    

