# import requests
# import json
# def generate_access_token():

#     try:

#         url = "https://ehes-qa-cmd.kimbal.io/token"  

#         payload = {
#             "grant_type": "password",
#             "username": "chanchal.patidar@kimbal.io",
#             "password": "Aeiou@8101",
#             "client_id": "Do_Kutte",
#             "client_secret": "",
#             "refresh_token": ""
#         }

#         headers = {
#             "Content-Type": "application/x-www-form-urlencoded"
#         }

#         response = requests.post(url, data=payload, headers=headers)

#         # print("Status Code:", response.status_code)

#         if response.status_code != 200:
#             print("Response Text:", response.text)
#             return None

#         token_response = response.json()
#         access_token = token_response.get("access_token")

#         return access_token
    
#     except Exception as e:
#         return f"Error: {e}"


# # # if __name__ == "__main__":
# # #     token = generate_access_token()
# # #     print("\nACCESS TOKEN:\n", token)



# params = {
#     "meterNo": "AP16002571",
#     "commandType": 8,
#     "commandValue": "2025-09-17 06:57:09",
#     # 'commandValue': {"From":"2026-01-06 00:00:00","To":"2025-09-17 06:57:09"},
#     "isDlms": True
# }

# # params = {
# #     'meterNo': 'AS9005753',
# #     'commandType': 2,
# #     "commandValue": 500,
   
# #     # 'commandValue': '{"From":"2026-01-06 00:00:00","To":"2026-01-06 01:00:00"}',
    
# #     'isDlms': False
# # }



# import re

# def normalize_params(params: dict) -> dict:
#     final_params = {}

#     for key, value in params.items():

#         # 1️⃣ Dict range → flatten
#         if isinstance(value, dict):
#             for sub_key, sub_val in value.items():
#                 final_params[f"{key}{sub_key}"] = _normalize_datetime(sub_val)
#             continue

#         # 2️⃣ String range: "date to date"
#         if isinstance(value, str):
#             match = re.match(
#                 r"^\s*(\d{4}-\d{2}-\d{2})(?:\s+\d{2}:\d{2}:\d{2})?\s+to\s+"
#                 r"(\d{4}-\d{2}-\d{2})(?:\s+\d{2}:\d{2}:\d{2})?\s*$",
#                 value,
#                 re.IGNORECASE
#             )
#             if match:
#                 final_params[f"{key}From"] = _normalize_datetime(match.group(1))
#                 final_params[f"{key}To"] = _normalize_datetime(match.group(2))
#                 continue

#         # 3️⃣ Single scalar
#         final_params[key] = _normalize_datetime(value)

#     return final_params


# def _normalize_datetime(value):
#     """
#     Converts YYYY-MM-DD → YYYY-MM-DD 00:00:00
#     Leaves datetime untouched
#     """
#     if isinstance(value, str):
#         # Date only
#         if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
#             return f"{value} 00:00:00"

#     return value


# params = normalize_params(params)
# print("param:",params)
# access_token=generate_access_token()
# headers = {
#     "Authorization": f"Bearer {access_token}"
# }

# response = requests.get(
#     "https://ehes-qa-cmd.kimbal.io/api/HES/RequestOnDemandData",
#     params=params,
#     headers=headers
# )

# print(response.status_code)
# print(json.dumps(response.json(), indent=4))

# interval_seconds=1
# import time
# # if response:
# requestsId = response.json().get("requestId")
# body_demo = {"requestId": requestsId}
# body_demo = normalize_params(body_demo)


# body_request_response = requests.get(
#     "https://ehes-qa-cmd.kimbal.io/api/HES/RequestOnDemandData",
#     params=body_demo,
#     headers=headers
# ).json()

# print("@@@@@@@@@@@@@ body_request_response",body_request_response)















############## displayed the data ###########


# def fetch_results_from_db(client_id, project_id, db_path="test_results.db"):
#     table_name = f"results_client_{client_id}_project_{project_id}"

#     conn = sqlite3.connect(db_path)

#     query = f"SELECT * FROM {table_name}"
#     df = pd.read_sql_query(query, conn)

#     conn.close()
#     return df



# def fetch_results_from_db(client_id, project_id, db_path="test_results.db"):
#     table_name = f"results_client_{client_id}_project_{project_id}"
#     conn = sqlite3.connect(db_path)
#     df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
#     conn.close()
#     return df


# def display_results_ui(client_id, project_id):
#     st.set_page_config(layout="wide")

#     st.markdown("## 📊 Test Execution Logs")

#     df = fetch_results_from_db(client_id, project_id)

#     if df.empty:
#         st.warning("No test data found.")
#         return
    
#     col1, col2, col3 = st.columns(3)
#     col1.metric("Total Tests", len(df))
#     col2.metric("Passed", len(df[df["result"] == "PASS"]))
#     col3.metric("Failed", len(df[df["result"] == "FAIL"]))

#     st.divider()

#     display_df = df.copy()

#     for col in [
#         "request_parameter",
#         "response",
#         "requestID_response",
#         "requestID_assertions",
#         "assertion_result"
#     ]:
#         if col in display_df.columns:
#             display_df[col] = display_df[col].apply(
#                 lambda x: json.dumps(json.loads(x), indent=2)[:250] + "..."
#                 if isinstance(x, str) and x.startswith("{")
#                 else str(x)
#             )

#     st.dataframe(
#         display_df,
#         use_container_width=True,
#         hide_index=True,
#         column_config={
#             "test_id": st.column_config.TextColumn("Test ID", width="small"),
#             "description": st.column_config.TextColumn("Description", width="medium"),
#             "request_parameter": st.column_config.TextColumn("Request Params", width="large"),
#             "response": st.column_config.TextColumn("Response", width="large"),
#             "expected_result": st.column_config.TextColumn("Expected", width="small"),
#             "status_code": st.column_config.NumberColumn("Status Code", width="small"),
#             "result": st.column_config.TextColumn("Result", width="small"),
#             "Taking_time_seconds": st.column_config.NumberColumn("Time (sec)", format="%.3f"),
#         }
#     )

#     st.divider()





