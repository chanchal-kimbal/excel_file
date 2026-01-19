
import streamlit as st
import pandas as pd
import json
import time
from io import BytesIO
from store_data_in_db import save_upload_metadata ,save_results_to_db ,fetch_upload_metadata ,fetch_results_from_db
from is_clientId_project_validate import is_validate
from Final_setup import run_all_tests,poll_request_id_interval,rerun_failed_tests

st.set_page_config(page_title="EHES Test Dashboard", layout="wide")
st.title("📊 EHES Automation Test Dashboard")


def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Test_Results")
    return output.getvalue()


def pretty_kv(value):
    if value is None or value == "":
        return "No data"

    if isinstance(value, str):
        try:
            value = json.loads(value)
        except Exception:
            return value

    if isinstance(value, dict):
        return "\n".join([f"{k}: {v}" for k, v in value.items()])

    return str(value)

def color_e2e_results(val):
    if val == "Pending":
        return "color: orange; font-weight: bold"
    if val == "Completed":
        return "color: green; font-weight: bold"
    if val == "Failed":
        return "color: red; font-weight: bold"
    if val == "Sent":
        return "color: goldenrod; font-weight: bold"
    return ""



if "creds_valid" not in st.session_state:
    st.session_state["creds_valid"] = False

if "test_executed" not in st.session_state:
    st.session_state["test_executed"] = False

uploaded_file = None   

st.subheader("🔐 Authentication")

left, center, right = st.columns([1, 2, 1])

with center:
    username = st.text_input("Username", placeholder="Enter Username")
    password = st.text_input(
        "Password",
        placeholder="Enter Password",
        type="password"
    )
    client_id = st.text_input("Client ID", placeholder="Enter Client ID")
    projectid = st.text_input("Project ID", placeholder="Enter Project ID")



if st.button("✅ Validate Credentials"):
    if projectid and client_id:
        if is_validate(projectid, client_id, username, password):
            st.session_state["creds_valid"] = True
            st.success("Credentials validated successfully ✅")
           
        else:
            st.session_state["creds_valid"] = False
            st.error("❌ Invalid Project ID or Client ID")
    else:
        st.warning("Please enter Credentials")

st.divider()


if st.session_state.get("creds_valid", False):
    uploaded_file = st.file_uploader(
        "📁 Upload Test Excel File",
        type=["xlsx"]
    )
    if uploaded_file is not None:
        uploaded_file_name = uploaded_file.name 
        save_upload_metadata(client_id, projectid, username, uploaded_file_name) 
        print("Uploaded File Name:", uploaded_file_name)
    start_time = time.time()

allow_set_commandtype = st.checkbox(
    "Enable SET Command Type execution",
    value=False
)


########### Database Configuration #############

st.subheader("🗄️ Database Configuration")

use_custom_db = st.checkbox("Use custom database credentials", value=False)

# Default (safe)
if "db_kwargs" not in st.session_state:
    st.session_state["db_kwargs"] = {
        "use_default_creds": True,
        "host": None,
        "port": None,
        "database": None,
        "user": None,
        "password": None,
    }

if use_custom_db:
    st.markdown("### 🔐 Enter Database Credentials")

    col1, col2 = st.columns(2)

    with col1:
        host = st.text_input("Host", key="db_host")
        database = st.text_input("Database", key="db_name")
        user = st.text_input("Username", key="db_user")

    with col2:
        port = st.number_input("Port", value=5432, key="db_port")
        password = st.text_input("Password", type="password", key="db_pass")

    if st.button("✅ Apply Database Credentials"):
        if not all([host, database, user, password]):
            st.error("❌ Please fill all database fields")
        else:
            st.session_state["db_kwargs"] = {
                "use_default_creds": False,
                "host": host,
                "port": port,
                "database": database,
                "user": user,
                "password": password,
            }
            st.success("✅ Database credentials applied successfully")

else:
    # Reset to default creds if checkbox unchecked
    st.session_state["db_kwargs"] = {
        "use_default_creds": True,
        "host": None,
        "port": None,
        "database": None,
        "user": None,
        "password": None,
    }




if uploaded_file and st.button("🚀 Run Test Suite"):
    with st.spinner("Executing tests..."):
        st.session_state["results"] = run_all_tests(
            uploaded_file,
            projectid,
            client_id,
            username,
            password,
            interval_seconds=None,
            allow_set_commandtype =allow_set_commandtype
        )
        st.session_state["results"]["rerun"] = (
            st.session_state["results"]["E2E_results"] == "Failed"
        )
        st.session_state["test_executed"] = True
        # save_results_to_db(st.session_state["results"],client_id, projectid)

    

if st.session_state.get("test_executed", False):
    st.subheader("⏱ Rerun-Request ID Response")
    # interval = st.radio("Select polling interval (seconds)",options=[5, 10, 15],horizontal=True)
    interval =0.2
    if st.button("🔄 Refresh"):
        with st.spinner(f"Refresh requestID interval..."):

            # updated_df = poll_request_id_interval(st.session_state["results"],interval)
            updated_df = poll_request_id_interval(
            df=st.session_state["results"],
            interval_seconds=interval,
            client_id=client_id,
            username=username,
            password=password,
            projectid=projectid
            )

            st.session_state["results"]["requestID_response"] = (
                updated_df["requestID_response"]
            )

            st.session_state["results"]["requestID_assertions"] = (
                updated_df["requestID_assertions"]
            )

            st.session_state["results"]["E2E_results"] = (
            updated_df["E2E_results"]
            )

        st.success("Request ID polling updated successfully ✅")


st.divider()

if st.button("Execute Rerun for Failed Tests"):
    with st.spinner("Re-running failed tests..."):
        rerun_df = rerun_failed_tests(
            st.session_state["results"],
            client_id,
            username,
            password,
            projectid,
        )

        # failed_tests_count = len(st.session_state["results"][st.session_state["results"]["result"] == "FAIL"])
        # rerun_failed_tests_count = len(rerun_df[rerun_df["result"] == "FAIL"])

        st.session_state["results"].update(rerun_df)

    # st.success(f"Re-run completed! {failed_tests_count - rerun_failed_tests_count} tests passed on re-run ✅")
    st.success(f"Re-run completed!  tests passed on re-run ✅")




try:

    if "results" in st.session_state:
        df = st.session_state["results"]

        if "result" not in df.columns:
            st.warning("Nothing is Found because Excel file have only SetCommnad datasets , Run only to select the checkbox")
            st.stop()

        total = len(df)
        passed = len(df[df["result"] == "PASS"])
        failed = len(df[df["result"] == "FAIL"])
        pass_pct = round((passed / total) * 100, 2) if total else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Tests", total)
        col2.metric("🟢 Passed", passed)
        col3.metric("🔴 Failed", failed)
        col4.metric("Pass %", f"{pass_pct}%")

        st.divider()

        status_filter = st.multiselect(
            "Filter by Result",
            options=df["result"].unique(),
            default=df["result"].unique()
        )

        filtered_df = df[df["result"].isin(status_filter)]

        display_df = filtered_df.copy()
        display_df["request_body"] = display_df["request_parameter"].apply(pretty_kv)
        display_df["response"] = display_df["response"].apply(pretty_kv)
        display_df["expected_results"] = display_df["expected_result"].apply(pretty_kv)
        display_df["requestID_response"] = display_df["requestID_response"].apply(pretty_kv)

        display_df = display_df[
            [
                "test_id",
                "description",
                "request_body",
                "response",
                "expected_results",
                "assertion_result",
                "result",
                "Taking_time(seconds)",
                "requestID_response",
                "requestID_assertions",
                "E2E_results",
            ]
        ]

        display_df["result"] = display_df["result"].map({
            "PASS": "🟢 PASS",
            "FAIL": "🔴 FAIL"
        })
        save_results_to_db(display_df,client_id, projectid)     ##### make changes here #####
        display_df = display_df.style.applymap(
        color_e2e_results,
        subset=["E2E_results"])
        
        # st.dataframe(styled_df, use_container_width=True)


        styled_table = (
            display_df
            # .style
            .set_properties(
                **{
                    "white-space": "pre-wrap",
                    "text-align": "left",
                    "font-size": "13px"
                }
            )
        )

        st.dataframe(styled_table, width="stretch", height=700)

        st.divider()

        if "show_upload_data" not in st.session_state:st.session_state.show_upload_data = False
        button_label = ("🙈 Hide Uploaded Data" if st.session_state.show_upload_data else "📊 Show Uploaded Data")
        if st.button(button_label):st.session_state.show_upload_data = not st.session_state.show_upload_data
        if st.session_state.show_upload_data:
            df = fetch_upload_metadata()
            if df.empty:st.warning("No uploaded data found.")
            else:st.dataframe(df,use_container_width=True,hide_index=True)


    


        if "show_test_results" not in st.session_state:
            st.session_state.show_test_results = False

        button_label = ("🙈 Hide Test Results" if st.session_state.show_test_results else "📊 Show Test Results")

        if st.button(button_label): st.session_state.show_test_results = not st.session_state.show_test_results

        if st.session_state.show_test_results:
            df = fetch_results_from_db(client_id, projectid)

            if df.empty: st.warning("No test results found.")
            else:st.dataframe(df,use_container_width=True,hide_index=True)


        excel_data = to_excel(display_df)

        st.download_button(
            label="📥 Download Results as Excel",   
            data=excel_data,
            file_name=  f"EHES_Test_Results_for_{uploaded_file_name}" ,                 # "EHES_Test_Results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        total_estimate_time = round(time.time() - start_time, 3)
        st.subheader(f"⏱️ Total Execution Time : {total_estimate_time} Seconds")

except Exception as e:
    st.subheader(f"Error : {e}")
    


    


























##### working code with clickable #####

# import streamlit as st
# import pandas as pd
# import json
# import time
# from io import BytesIO
# from fetch_meter_from_db import get_command_reason
# from store_data_in_db import save_results_to_db ,display_results_ui
# from is_clientId_project_validate import is_validate
# from Final_setup import run_all_tests,poll_request_id_interval,rerun_failed_tests

# st.set_page_config(page_title="EHES Test Dashboard", layout="wide")
# st.title("📊 EHES Automation Test Dashboard")


# def to_excel(df):
#     output = BytesIO()
#     with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#         df.to_excel(writer, index=False, sheet_name="Test_Results")
#     return output.getvalue()


# def pretty_kv(value):
#     if value is None or value == "":
#         return "No data"

#     if isinstance(value, str):
#         try:
#             value = json.loads(value)
#         except Exception:
#             return value

#     if isinstance(value, dict):
#         return "\n".join([f"{k}: {v}" for k, v in value.items()])

#     return str(value)

# def color_e2e_results(val):
#     if val == "Pending":
#         return "color: orange; font-weight: bold"
#     if val == "Completed":
#         return "color: green; font-weight: bold"
#     if val == "Failed":
#         return "color: red; font-weight: bold"
#     if val == "Sent":
#         return "color: goldenrod; font-weight: bold"
#     return ""



# if "creds_valid" not in st.session_state:
#     st.session_state["creds_valid"] = False

# if "test_executed" not in st.session_state:
#     st.session_state["test_executed"] = False

# uploaded_file = None   

# st.subheader("🔐 Authentication")

# left, center, right = st.columns([1, 2, 1])

# with center:
#     username = st.text_input("Username", placeholder="Enter Username")
#     password = st.text_input(
#         "Password",
#         placeholder="Enter Password",
#         type="password"
#     )
#     client_id = st.text_input("Client ID", placeholder="Enter Client ID")
#     projectid = st.text_input("Project ID", placeholder="Enter Project ID")


# if st.button("✅ Validate Credentials"):
#     if projectid and client_id:
#         if is_validate(projectid, client_id, username, password):
#             st.session_state["creds_valid"] = True
#             st.success("Credentials validated successfully ✅")
#         else:
#             st.session_state["creds_valid"] = False
#             st.error("❌ Invalid Project ID or Client ID")
#     else:
#         st.warning("Please enter Credentials")

# st.divider()


# def map_e2e(val):
#     return {
#         "Pending": "🟠 Pending",
#         "Sent": "🟡 Sent",
#         "Completed": "🟢 Completed",
#         "Failed": "🔴 Failed",
#         "Not Applicable": "⚪ Not Applicable"
#     }.get(val, val)


# if st.session_state.get("creds_valid", False):
#     uploaded_file = st.file_uploader("📁 Upload Test Excel File", type=["xlsx"])
#     start_time = time.time()

# allow_set_commandtype = st.checkbox(
#     "Enable SET Command Type execution",
#     value=False
# )


# if uploaded_file and st.button("🚀 Run Test Suite"):
#     with st.spinner("Executing tests..."):
#         st.session_state["results"] = run_all_tests(
#             uploaded_file,
#             projectid,
#             client_id,
#             username,
#             password,
#             interval_seconds=None,
#             allow_set_commandtype=allow_set_commandtype
#         )

#         st.session_state["results"]["rerun"] = False
#         st.session_state["test_executed"] = True



# if st.session_state.get("test_executed", False):
#     st.subheader("⏱ Rerun-Request ID Response")
#     interval = 0.1

#     if st.button("🔄 Rerun"):
#         with st.spinner("Refreshing request IDs..."):
#             updated_df = poll_request_id_interval(
#                 df=st.session_state["results"],
#                 interval_seconds=interval,
#                 client_id=client_id,
#                 username=username,
#                 password=password,
#                 projectid=projectid
#             )

#             for col in ["requestID_response", "requestID_assertions", "E2E_results"]:
#                 st.session_state["results"][col] = updated_df[col]

#         st.success("Request ID polling updated successfully ✅")



# if "results" in st.session_state:
#     df = st.session_state["results"]

#     total = len(df)
#     passed = len(df[df["result"] == "PASS"])
#     failed = len(df[df["result"] == "FAIL"])
#     pass_pct = round((passed / total) * 100, 2) if total else 0

#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("Total Tests", total)
#     col2.metric("🟢 Passed", passed)
#     col3.metric("🔴 Failed", failed)
#     col4.metric("Pass %", f"{pass_pct}%")

#     st.divider()

#     display_df = df.copy()
#     display_df["request_body"] = display_df["request_parameter"].apply(pretty_kv)
#     display_df["response"] = display_df["response"].apply(pretty_kv)
#     display_df["expected_results"] = display_df["expected_result"].apply(pretty_kv)
#     display_df["requestID_response"] = display_df["requestID_response"].apply(pretty_kv)

#     display_df["E2E_results"] = display_df["E2E_results"].apply(map_e2e)

#     display_df = display_df[
#         [
#             "test_id",
#             "description",
#             "request_body",
#             "response",
#             "expected_results",
#             "assertion_result",
#             "result",
#             "Taking_time(seconds)",
#             "requestID_response",
#             "requestID_assertions",
#             "E2E_results",
#             "rerun"
#         ]
#     ]

#     display_df["result"] = display_df["result"].map({
#         "PASS": "🟢 PASS",
#         "FAIL": "🔴 FAIL"
#     })


#     edited_df = st.data_editor(
#         display_df,
#         column_config={
#             "rerun": st.column_config.CheckboxColumn(
#                 "Re-run",
#                 help="Select to re-run this test"
#             )
#         },
#         disabled=[
#             "test_id",
#             "description",
#             "request_body",
#             "response",
#             "expected_results",
#             "assertion_result",
#             "result",
#             "Taking_time(seconds)",
#             "requestID_response",
#             "requestID_assertions",
#             "E2E_results",
#         ],
#         hide_index=True,
#         height=700
#     )

#     changed_rows = edited_df[
#         (edited_df["rerun"] == True) &
#         (st.session_state["results"]["rerun"] == False)
#     ]

#     for idx, row in changed_rows.iterrows():
        
#         if "Failed" not in str(row.get("E2E_results", "")):
#             continue

#         # if "Failed" not in row["E2E_results"]:
#         #     continue

#         with st.spinner(f"Re-running {row['test_id']}..."):
#             rerun_df = rerun_failed_tests(
#                 st.session_state["results"].loc[[idx]],
#                 client_id,
#                 username,
#                 password,
#                 projectid,
#             )

#             st.session_state["results"].update(rerun_df)
#             st.session_state["results"].at[idx, "rerun"] = False

#         st.success(f"{row['test_id']} re-executed ✅")

    
#     excel_data = to_excel(display_df)

#     st.download_button(
#         label="📥 Download Results as Excel",
#         data=excel_data,
#         file_name="EHES_Test_Results.xlsx",
#         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )

#     total_estimate_time = round(time.time() - start_time, 3)
#     st.subheader(f"⏱️ Total Execution Time : {total_estimate_time} Seconds")

































# import streamlit as st
# import pandas as pd
# import json
# from io import BytesIO
# import time
# from Final_setup import run_all_tests   # your existing logic

# st.set_page_config(page_title="EHES Test Dashboard", layout="wide")
# st.title("📊 EHES Automation Test Dashboard")


# def to_excel(df):
#     output = BytesIO()
#     with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#         df.to_excel(writer, index=False, sheet_name="Test_Results")
#     return output.getvalue()


# def pretty_kv(value):

#     if value is None or value == "":
#         return "No data"

#     if isinstance(value, str):
#         try:
#             value = json.loads(value)
#         except Exception:
#             return value

#     if isinstance(value, dict):
#         return "\n".join([f"{k}: {v}" for k, v in value.items()])

#     return str(value)



# if "creds_valid" not in st.session_state:
#     st.session_state["creds_valid"] = False

# st.subheader("🔐 Authentication")

# left, center, right = st.columns([1, 2, 1])

# with center:
#     username = st.text_input(
#         "Username",
#         placeholder="Enter Username"
#     )
#     password = st.text_input(
#         "Password",
#         placeholder="Enter Password",
#         type="password" 
#     )
#     client_id = st.text_input(
#         "Client ID",
#         placeholder="Enter Client ID"
#     )
#     projectid = st.text_input(
#         "Project ID",
#         placeholder="Enter Project ID"
#     )
#     st.markdown("") 


# uploaded_file = st.file_uploader(
#     "📁 Upload Test Excel File",
#     type=["xlsx"]
# )

# try:
#     start_time = time.time()
#     if uploaded_file:
#         if st.button("🚀 Run Test Suite"):
#             with st.spinner("Executing tests..."):

#                 df = run_all_tests(uploaded_file,projectid ,client_id,username, password, interval_seconds=None)
#                 st.session_state["results"] = df

#     if "results" in st.session_state:
#         df = st.session_state["results"]

#         total = len(df)
#         passed = len(df[df["result"] == "PASS"])
#         failed = len(df[df["result"] == "FAIL"])
#         pass_pct = round((passed / total) * 100, 2) if total else 0

#         col1, col2, col3, col4 = st.columns(4)
#         col1.metric("Total Tests", total)
#         col2.metric("🟢 Passed", passed)
#         col3.metric("🔴 Failed", failed)
#         col4.metric("Pass %", f"{pass_pct}%")

#         st.divider()

#         status_filter = st.multiselect(
#             "Filter by Result",
#             options=df["result"].unique(),
#             default=df["result"].unique()
#         )

#         filtered_df = df[df["result"].isin(status_filter)]

#         display_df = filtered_df.copy()

#         display_df["request_body"] = display_df["request_parameter"].apply(pretty_kv)
#         display_df["response"] = display_df["response"].apply(pretty_kv)
#         display_df["expected_results"] = display_df["expected_result"].apply(pretty_kv)
#         display_df["requestID_response"] = display_df["requestID_response"].apply(pretty_kv)

#         display_df = display_df[
#             [
#                 "test_id",
#                 "description",
#                 "request_body",
#                 "response",
#                 "expected_results",
#                 "assertion_result",
#                 "result",
#                 "Taking_time(seconds)",
#                 "requestID_response" ,
#               "requestID_assertions"
#             ]
#         ]

#         display_df["result"] = display_df["result"].map({
#             "PASS": "🟢 PASS",
#             "FAIL": "🔴 FAIL"
#         })

#         styled_table = (
#             display_df
#             .style
#             .set_properties(**{"white-space": "pre-wrap","text-align": "left","font-size": "13px"})
#         )

#         st.dataframe(
#             styled_table,
#             width="stretch",       #### stretch
#             height=700             ### 700 
#         )
        
#         st.divider()
#         end_time = time.time()

#         excel_data = to_excel(display_df)

#         st.download_button(
#             label="📥 Download Results as Excel",
#             data=excel_data,
#             file_name="EHES_Test_Results.xlsx",
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )

#         total_estimate_time =end_time - start_time
#         total_estimate_time = total_estimate_time.__round__(3)

#         st.subheader(f"Total Execution Time : {total_estimate_time} Seconds")


#         # col1, col2 = st.columns(2)
#         # with col1:
#         #     st.bar_chart(df["result"].value_counts())

#         # with col2:
#         #     st.bar_chart(df["status_code"].value_counts())

# except Exception as e:
#     st.subheader(f"Error : {e}")