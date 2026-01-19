############ update code with Asseration #########

import pandas as pd
import json
import time
from read_filter_data_from_excel import *
from Hit_api import *
from Assertion_engine import build_assertion_result ,result_from_assertion_text ,RequestID_Assertions
from fetch_meter_from_db import get_meterid_and_time ,get_command_reason
from helper_function import get_commandType_only
from ollama_setup import ensure_ollama_running

# ensure_ollama_running()


def get_chunked_df_by_test_id(df, chunk_size=10):
    """
    Takes full DataFrame and yields (chunk_df, test_id)
    """
    if not hasattr(df, "iloc"):
        raise TypeError("Expected pandas DataFrame")

    for test_id in df["_Test ID"].unique():
        test_df = df[df["_Test ID"] == test_id]

        for start in range(0, len(test_df), chunk_size):
            yield test_df.iloc[start:start + chunk_size], test_id




def run_all_tests(excel_file,projectid,client_id,username,password,interval_seconds,allow_set_commandtype):

    results = []
    meter_name, date_value = get_meterid_and_time(excel_file,projectid)
    df, test_ids = execute_metre(meter_name, date_value, excel_file)
    for test_id_value in test_ids:
        result = extract_by_test_id(df, test_id_value)
        x1 = filter_test_fields(result)

        data_dict = json.loads(x1) if isinstance(x1, str) else x1
        
        command_values =get_commandType_only(data_dict,allow_set_commandtype,projectid)

        if command_values is None:
            continue

        start_time =time.time()
        try:

           url,headers, test_id, request_params, response_json, status_code, expected_result,description,body_request_response = run_requests_from_json(data_dict,client_id,username,password,interval_seconds)
        except:
            continue

        end_time =time.time()

        estimate_time =end_time - start_time

        Taking_time=estimate_time.__round__(3)
       
        assertion_text = build_assertion_result(status_code,response_json,expected_result)
        
        values=result_from_assertion_text(assertion_text)
        
        requestID_assertions =RequestID_Assertions(request_params,body_request_response)
        
        if body_request_response.get("RequestState") is None:
            body_request_response["RequestState"]="Not Applicable"
           
        
        final_body_response = dict(body_request_response) if body_request_response else {}

        request_state = final_body_response.get("RequestState")
        e2e_result = request_state 
        if request_state == "Failed":
            reason_df = get_command_reason(projectid,str(final_body_response.get("RequestId")))
            if reason_df is not None and not reason_df.empty:
                reason_text = str(reason_df.iloc[0])
            else:
                reason_text = "Reason not found"

            e2e_result = f"Failed | Reason: {reason_text}"

            print(f"Test ID: {test_id} | Failed Reason: {reason_text}")


        results.append({
            "test_id": test_id,
            "description":description,
            "request_parameter":request_params,
            "response": response_json,
            "expected_result": expected_result,
            "status_code": status_code,
            "result": values,
            "assertion_result": assertion_text,
            "Taking_time(seconds)":Taking_time,
            "requestID_response" :  final_body_response,                         #body_request_response ,
            "requestID_assertions" : requestID_assertions,
            "url":url,
            "headers":headers,
            "requestID": response_json.get("requestId"),
            "E2E_results" :  e2e_result,                #body_request_response.get("RequestState") ,  
            "client_id": client_id,
            "username": username,
            "password": password
            })

    return pd.DataFrame(results)




###### working code #####

def poll_request_id_interval(
    df: pd.DataFrame,
    interval_seconds: int,
    client_id: str,
    username: str,
    password: str,
    projectid: str  ## changes
) -> pd.DataFrame:

    updated_df = df.copy()

    token = generate_access_token(client_id, username, password)
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    for idx, row in updated_df.iterrows():

        request_id = row.get("requestID")
        url = row.get("url")
        test_id= row.get("test_id")

        if pd.isna(request_id) or not url:
            continue


        clean_request_id = int(float(request_id))

        body_demo = normalize_params({"requestId": clean_request_id})

        end_time = time.time() + interval_seconds
        response = None
     
        final_response = None

        while time.time() < end_time:
            response = requests.get(
                url,
                params=body_demo,
                headers=headers
            )

            if response.status_code != 200:
                break

            final_response = response.json()

            request_state = final_response.get("RequestState")
            final_request_state = request_state
            if request_state in ("Completed","Failed","Not Applicable"):
                break

            if not final_request_state:final_request_state = "Unknown"


        if response is None:
            final_response = {"error": "No response"}
        elif response.status_code != 200:
            final_response = {
                "error": f"HTTP {response.status_code}",
                "message": response.text
            }
        else:
            final_response = response.json()


        ######## changes #########

        final_body_response = dict(final_response) if final_response else {}

        request_state = final_body_response.get("RequestState")
        e2e_result = request_state 
        if request_state == "Failed":
            reason_df = get_command_reason(projectid,str(final_body_response.get("RequestId")))
            if reason_df is not None and not reason_df.empty:
                reason_text = str(reason_df.iloc[0])
            else:
                reason_text = "Reason not found"

            e2e_result = f"Failed | Reason: {reason_text}"



        
        updated_df.at[idx, "requestID_response"] = final_body_response   #changes                #final_response
        updated_df.at[idx, "E2E_results"] =e2e_result                    #changes                 #final_request_state
        
        updated_df.at[idx, "requestID_assertions"] = RequestID_Assertions(
            row.get("request_parameter"),
            final_response
        )

      
    return updated_df





def rerun_failed_tests(
    df: pd.DataFrame,
    client_id: str,
    username: str,
    password: str,
    projectid: str
) -> pd.DataFrame:

    updated_df = df.copy()

    for idx, row in updated_df.iterrows():

        # ✅ Re-run ONLY failed tests (with or without reason)
        e2e_val = str(row.get("E2E_results", ""))
        if not e2e_val.startswith("Failed"):
            continue

        print(f"🔁 Re-running FAILED test: {row['test_id']}")

        data_dict = {
            "filtered_data": [{
                "_Test ID": row["test_id"],
                "_Test Data": (
                    json.dumps(row["request_parameter"])
                    if isinstance(row["request_parameter"], dict)
                    else row["request_parameter"]
                ),
                "_Status code": row["status_code"],
                "API Type": "GET",
                "URL": row["url"],
                "_Expected Result": row["expected_result"],
                "_desc": row["description"]
            }]
        }

        try:
            (
                url, headers, test_id, request_params,
                response_json, status_code,
                expected_result, description,
                body_request_response
            ) = run_requests_from_json(
                data_dict,
                client_id,
                username,
                password,
                interval_seconds=None
            )

            final_body_response = dict(body_request_response) if body_request_response else {}

            request_state = final_body_response.get("RequestState", "Unknown")
            e2e_result = request_state

            if request_state == "Failed":
                reason_df = get_command_reason(
                    projectid,
                    str(final_body_response.get("RequestId"))
                )
                reason_text = (
                    str(reason_df.iloc[0])
                    if reason_df is not None and not reason_df.empty
                    else "Reason not found"
                )
                e2e_result = f"Failed | Reason: {reason_text}"

            updated_df.at[idx, "response"] = response_json
            updated_df.at[idx, "requestID_response"] = final_body_response
            updated_df.at[idx, "requestID_assertions"] = RequestID_Assertions(
                request_params,
                final_body_response
            )
            updated_df.at[idx, "E2E_results"] = e2e_result

        except Exception as e:
            print(f"❌ Re-run failed for {row['test_id']}: {e}")

    return updated_df
























#### with chunking #####

# def run_all_tests(excel_file,projectid,client_id,username,password,interval_seconds,allow_set_commandtype):

#     results = []
#     meter_name, date_value = get_meterid_and_time(excel_file,projectid)
#     df, test_ids = execute_metre(meter_name, date_value, excel_file)

    

#     for chunk_df, test_id_value in get_chunked_df_by_test_id(df, chunk_size=10):

#         print(f"Processing test_id={test_id_value}, rows={len(chunk_df)}")

#         # x1 = filter_test_fields(chunk_df)
#         result = extract_by_test_id(df, test_id_value)

#         x1 = filter_test_fields(result)

#         data_dict = json.loads(x1) if isinstance(x1, str) else x1
        
#         command_values =get_commandType_only(data_dict,allow_set_commandtype,projectid)

#         if command_values is None:
#             continue

#         start_time =time.time()
#         try:
#             url,headers, test_id, request_params, response_json, status_code, expected_result,description,body_request_response = run_requests_from_json(data_dict,client_id,username,password,interval_seconds)
#         except:
#             continue

#         end_time =time.time()

#         estimate_time =end_time - start_time

#         Taking_time=estimate_time.__round__(3)
    
#         assertion_text = build_assertion_result(status_code,response_json,expected_result)
        
#         values=result_from_assertion_text(assertion_text)
        
#         requestID_assertions =RequestID_Assertions(request_params,body_request_response)
        
#         if body_request_response.get("RequestState") is None:
#             body_request_response["RequestState"]="Not Applicable"
        
#         final_body_response = dict(body_request_response) if body_request_response else {}

#         request_state = final_body_response.get("RequestState")
#         e2e_result = request_state 
#         if request_state == "Failed":
#             reason_df = get_command_reason(projectid,str(final_body_response.get("RequestId")))
#             if reason_df is not None and not reason_df.empty:
#                 reason_text = str(reason_df.iloc[0])
#             else:
#                 reason_text = "Reason not found"

#             e2e_result = f"Failed | Reason: {reason_text}"

#             print(f"Test ID: {test_id} | Failed Reason: {reason_text}")

#         results.append({
#             "test_id": test_id,
#             "description":description,
#             "request_parameter":request_params,
#             "response": response_json,
#             "expected_result": expected_result,
#             "status_code": status_code,
#             "result": values,
#             "assertion_result": assertion_text,
#             "Taking_time(seconds)":Taking_time,
#             "requestID_response" :  final_body_response,                        
#             "requestID_assertions" : requestID_assertions,
#             "url":url,
#             "headers":headers,
#             "requestID": response_json.get("requestId"),
#             "E2E_results" :  e2e_result,               
#             "client_id": client_id,
#             "username": username,
#             "password": password
#             })

#     return pd.DataFrame(results)



########### working code ###########

# def rerun_failed_tests(
#     df: pd.DataFrame,
#     client_id: str,
#     username: str,
#     password: str,
#     projectid: str  ## changes
# ) -> pd.DataFrame:

#     updated_df = df.copy()

#     for idx, row in updated_df.iterrows():

#         #✅ Only FAILED tests
#         if row.get("E2E_results") != "Failed":
#             continue

#         print(f"🔁 Re-running FAILED test: {row['test_id']}")

#          # Reconstruct data_dict for the test

#         data_dict = {
#         "filtered_data": [{
#             "_Test ID": row["test_id"],
#             "_Test Data": (
#                 json.dumps(row["request_parameter"])
#                 if isinstance(row["request_parameter"], dict)
#                 else row["request_parameter"]
#             ),
#             "_Status code": row["status_code"],
#             "API Type": "GET",
#             "URL": row["url"],
#             "_Expected Result": row["expected_result"],
#             "_desc": row["description"]
#         }]
#     }


#         try:
#             url,headers,test_id,request_params,response_json,status_code,expected_result,description,body_request_response = run_requests_from_json(data_dict,client_id,username,password,interval_seconds=None)

#             updated_df.at[idx, "response"] = response_json
            
#             updated_df.at[idx, "requestID_response"] = body_request_response
#             updated_df.at[idx, "requestID_assertions"] = RequestID_Assertions(
#                 request_params, body_request_response
#             )
#             updated_df.at[idx, "E2E_results"] = body_request_response.get("RequestState")

#         except Exception as e:
#             print(f"❌ Re-run failed for {row['test_id']}: {e}")

#     return updated_df


















# client_id = "Do_Kutte"
# username = "chanchal.patidar@kimbal.io"
# password = "Aeiou@8101"
# projectid=1

# excel="test.xlsx"


# x = run_all_tests(excel, projectid, client_id, username, password,interval_seconds=None,allow_set_commandtype=False)

# print(x)





































































   




















