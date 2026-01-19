
########## Update Creds with input Client id's ###########

import requests
import json
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


# if __name__ == "__main__":
#     client_id = "BCITS_MDM"
#     username = "chanchal.patidar@kimbal.io"
#     password = "Aeiou@8101"
#     token = generate_access_token(client_id,username,password)
#     print("\nACCESS TOKEN:\n", token)

# "username": "chanchal.patidar@kimbal.io",
#"password": "Aeiou@8101",













  


















############ old code for reference ############

# import json
# import requests
# import threading
# import time

# user_credentials ={
#     "filtered_data": [
#         {
#             "_Test ID": "EHES_LGN_TC_1",
#             "_Test Data": {
#         "email": "Rahul.Rajput@kimbal.io",
#         "password": "KzH5ZDkzF1RLr4yLqQ5uIWQj+AhVT7+i1BTQxg8pGcv3eRZftVp3D/Ks24xIHmVJ0d4mEqkY+qqzcpAppl6gQT7dwbKNaTvVeFb27XqwboQhaOJH6PaoDo32ZMz8CJjYwSnccQI6/DGodq8UbuaSLeu2rDip0C5B2Nqg7nfGzIs=",
#         "grantType": "password",
#         "refreshToken": ""
#     },
#             "_Status code": 200,
#             "API Type": "POST",
#             "URL": "https://ehes-qa-viewer.kimbal.io/api/Authentication/Login"
#         }
#     ]
# }


# def get_user_credentials():
#     return user_credentials


# def run_requests_from_json(data):

#     if "filtered_data" not in data:
#         print("Invalid JSON structure")
#         return None

#     final_response = None       

#     for item in data["filtered_data"]:
#         test_id = item.get("_Test ID")
#         url = item.get("URL")
#         method = item.get("API Type", "GET").upper()
#         expected_status = item.get("_Status code")

#         raw_body = item.get("_Test Data", {})

#         if isinstance(raw_body, dict):
#             body = raw_body                     
#         elif isinstance(raw_body, str):
#             try:
#                 body = json.loads(raw_body)     
#             except:
#                 print(f"ERROR: Unable to parse JSON for test {test_id}")
#                 body = {}
#         else:
#             body = {}     

#         # print(f"\n==============================")
#         # print(f" Running Test: {test_id}")
#         # print(f" URL: {url}")
#         # print(f" Method: {method}")
#         # print(f"==============================")

#         try:
#             if method == "GET":
#                 response = requests.get(url, params=body)
#             else:
#                 response = requests.request(method, url, json=body)

#             # print("Status Code:", response.status_code)

#             if expected_status and response.status_code == expected_status:
#                 print("Status Matched")
#             else:
#                 print("Expected:", expected_status)

#             # print("Response:")

#             try:
#                 final_response = response.json()
#                 # print(json.dumps(final_response, indent=4))
#             except:
#                 final_response = response.text
#                 # print(final_response)

#         except Exception as e:
#             print(f"Request Failed: {e}")

#     return final_response


# REFRESH_INTERVAL = 30 * 60 


# def trigger_user_credentials():
#     print("\n⏰ 30 minutes completed. Refreshing token...")
#     creds = get_user_credentials()
#     run_requests_from_json(creds)
#     schedule_login_refresh()   


# def schedule_login_refresh():
#     timer = threading.Timer(REFRESH_INTERVAL, trigger_user_credentials)
#     timer.daemon = True 
#     timer.start()



# def get_tokens_from_response():
#     creds = get_user_credentials()
#     final_response = run_requests_from_json(creds)
#     tokens = {}
#     if final_response:
#          token = final_response.get("accessToken")
#          tokens.update({"accessToken": token})
#     schedule_login_refresh()
#     return tokens




# def update_tokens():
#     creds = get_user_credentials()
#     tokens=get_tokens_from_response(creds)
#     schedule_login_refresh()
#     return tokens



##### imp update for the future use #####
# Keep program alive
# while True:
#     time.sleep(1)

