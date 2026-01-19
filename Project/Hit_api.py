
import pandas as pd
import json
import requests
import re
import json
from user_creds import generate_access_token
from data_processing import *
import time

def run_requests_from_json(data,client_id,username,password,interval_seconds):

    if "filtered_data" not in data:
        print("Invalid JSON structure")
        return None, None, None, None
   
    for item in data["filtered_data"]:
        test_id = item.get("_Test ID")
        url = item.get("URL")
        method = item.get("API Type", "GET").upper()
        expected_status = item.get("_Status code")
        expected_result = item.get("_Expected Result")
        description = item.get("_desc")

        raw_body = item.get("_Test Data", "{}")
        
        if method == "GET":
                body = parse_get_params(raw_body)
        else:
            try:
                body = json.loads(raw_body)
            except:
                print(f"ERROR: Unable to parse JSON for test {test_id}")
                body = {}
        if  body.get("isDlms") == "":
            body["isDlms"]=None    
        token = generate_access_token(client_id,username,password)
        if token is None:
            print("ERROR: No access token available")
            exit(1)
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        try:
            if method == "GET":
                body = normalize_params(body)
                response = requests.get(url, params=body, headers=headers)
            else:
                response = requests.request(method, url, json=body)

            status_code = expected_status  #### make changes here

            try:
                final_response = response.json()
                # final_response = json.dumps(response.json(), indent=4)
            except:
                final_response = response.text
            
            if final_response:
                requestsId = final_response.get("requestId")
                body_demo = {"requestId": requestsId}
                body_demo = normalize_params(body_demo)
                body_request_response = requests.get(url,params=body_demo,headers=headers).json()

            return url,headers ,test_id, body, final_response, status_code,expected_result,description ,body_request_response

        except Exception as e:
            print(f"Request Failed: {e}")
            return test_id, body, str(e), None
           

    return None, None, None, None






























### working code ####
# import pandas as pd
# import json
# import requests
# import re
# import json
# from user_creds import generate_access_token
# from data_processing import *
# import time

# def run_requests_from_json(data,client_id,username,password,interval_seconds):

#     # interval_seconds = None

#     if "filtered_data" not in data:
#         print("Invalid JSON structure")
#         return None, None, None, None

#     for item in data["filtered_data"]:
#         test_id = item.get("_Test ID")
#         url = item.get("URL")
#         method = item.get("API Type", "GET").upper()
#         expected_status = item.get("_Status code")
#         expected_result = item.get("_Expected Result")
#         description = item.get("_desc")

#         raw_body = item.get("_Test Data", "{}")
        
#         if method == "GET":
#                 body = parse_get_params(raw_body)
#         else:
#             try:
#                 body = json.loads(raw_body)
#             except:
#                 print(f"ERROR: Unable to parse JSON for test {test_id}")
#                 body = {}
#         if  body.get("isDlms") == "":
#             body["isDlms"]=None    
#         token = generate_access_token(client_id,username,password)
#         if token is None:
#             print("ERROR: No access token available")
#             exit(1)
#         headers = {"Authorization": f"Bearer {token}"} if token else {}

#         try:
#             if method == "GET":
#                 body = normalize_params(body)
#                 response = requests.get(url, params=body, headers=headers)
#             else:
#                 response = requests.request(method, url, json=body)

#             status_code = expected_status  #### make changes here

#             try:
#                 final_response = response.json()
#                 # final_response = json.dumps(response.json(), indent=4)
#             except:
#                 final_response = response.text
            
#             # if final_response:
#             #     requestsId=final_response.get("requestId")
#             #     body_demo={"requestId":requestsId}
#             #     body_demo = normalize_params(body_demo)
#             #     # body_request_response = response = requests.get(url, params=body_demo, headers=headers)
#             #     body_request_response  = requests.get(url, params=body_demo, headers=headers)
#             #     body_request_response =body_request_response.json()


#             def hit_api():
#                 if final_response:
#                     requestId = final_response.get("requestId")
#                     body_demo = {"requestId": requestId}
#                     body_demo = normalize_params(body_demo)
#                     body_request_response = requests.get(url, params=body_demo, headers=headers)
#                     resp =body_request_response.json()
#                     return resp
        
#             if interval_seconds:
#                 while True:
#                     body_request_response = hit_api()
#                     time.sleep(interval_seconds)
#             else:
#                 body_request_response = hit_api()
 
#             return test_id, body, final_response, status_code,method,expected_result,description ,body_request_response

#         except Exception as e:
#             print(f"Request Failed: {e}")
#             return test_id, body, str(e), None

#     return None, None, None, None



































