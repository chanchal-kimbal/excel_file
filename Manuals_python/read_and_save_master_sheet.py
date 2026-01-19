import pandas as pd
import json

from save_data_in_excel import save_test_result
from Assertion_check import check_app_settings
from read_filter_data_from_excel import *
from Hit_api import *




excel_file = "master_file.xlsx"  ### read from master excel file

while True:
    query = input("\nYou: ")
    if query.lower() in ["exit", "quit"]:
        print("Exiting the program.")
        break
    if not query.strip():
        print("Please enter a valid Test ID or 'exit' to quit.")
        continue
    test_ids = [item.strip() for item in query.split(",")]
    
    df = read_excel(excel_file)

    for test_id_value in test_ids:

        result = extract_by_test_id(df, test_id_value)

        x1=filter_test_fields(result)

        if isinstance(x1, str):
            data_dict = json.loads(x1)
        else:
            data_dict = x1

        try:
            test_id, request_params, response_json, status_code,method ,expected_result= run_requests_from_json(data_dict)
            print("\nFinal expected_result JSON:",json.dumps(response_json, indent=4))
            
            assertion_result=check_app_settings(expected_result, method,status_code)
            
            save_test_result(
                test_id,
                request_params,
                response_json,
                status_code,
                "FAIL" if status_code == 500 else "PASS",
                method,
                expected_result,
                assertion_result
            )
        except:
            print(f"ERROR: Failed to process ,Test ID is not found {test_id_value}")
    

