import pandas as pd
import json

from save_data_in_excel import save_test_result
from Assertion_check import check_app_settings
from read_filter_data_from_excel import *
from Hit_api import *

from Demo import get_meterid_and_time 

########### new code for automation #############

excel_file = "sheet2_output.xlsx"  ### read from master excel file


meter_name,date_value= get_meterid_and_time(excel_file)

df,test_ids= execute_metre(meter_name,date_value,excel_file)

test_ids = [item for item in test_ids]
for test_id_value in test_ids:

    result = extract_by_test_id(df, test_id_value)

    x1=filter_test_fields(result)

    if isinstance(x1, str):
        data_dict = json.loads(x1)
    else:
        data_dict = x1

    test_id, request_params, response_json, status_code,method ,expected_result= run_requests_from_json(data_dict)
    print("\nFinal expected_result JSON:",json.dumps(response_json, indent=4))








# excel_file = "sheet2_output.xlsx"  ### read from master excel file
# meter_map_excel="dummy_meter_ids.xlsx"



##### from input id's noly ######

# while True:
#     query = input("\nYou: ")
#     if query.lower() in ["exit", "quit"]:
#         print("Exiting the program.")
#         break
#     if not query.strip():
#         print("Please enter a valid Test ID or 'exit' to quit.")
#         continue
#     test_ids = [item.strip() for item in query.split(",")]
    
#     df = read_excel(excel_file)

#     for test_id_value in test_ids:

#         result = extract_by_test_id(df, test_id_value)

#         x1=filter_test_fields(result)

#         if isinstance(x1, str):
#             data_dict = json.loads(x1)
#         else:
#             data_dict = x1


#         test_id, request_params, response_json, status_code,method ,expected_result= run_requests_from_json(data_dict)
#         print("\nFinal expected_result JSON:",json.dumps(response_json, indent=4))
        
        # assertion_result=check_app_settings(expected_result, method,status_code)
        
        # save_test_result(
        #     test_id,
        #     request_params,
        #     response_json,
        #     status_code,
        #     "FAIL" if status_code == 500 else "PASS",
        #     method,
        #     expected_result,
        #     assertion_result
        # )
        
    





###### input meter number and input dates #######

# while True:
#     query = input("Enter meter number: ").strip()
#     date_value = input("Enter date (YYYY-MM-DD or YYYY-MM-DD to YYYY-MM-DD): ").strip()
#     if query.lower() in ["exit", "quit"]:
#         print("Exiting the program.")
#         break
#     if not query.strip():
#         print("Please enter a valid Test ID or 'exit' to quit.")
#         continue

#     df,ids= execute_metre(query,date_value,excel_file)

#     test_ids = [item.strip() for item in ids]
    
#     for test_id_value in test_ids:

#         result = extract_by_test_id(df, test_id_value)

#         x1=filter_test_fields(result)

#         if isinstance(x1, str):
#             data_dict = json.loads(x1)
#         else:
#             data_dict = x1


#         test_id, request_params, response_json, status_code,method ,expected_result= run_requests_from_json(data_dict)
#         print("\nFinal expected_result JSON:",json.dumps(response_json, indent=4))













        