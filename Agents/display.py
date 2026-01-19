import streamlit as st
import pandas as pd
import json
import time
from io import BytesIO
from execution_agent import generate_access_token 
from data_fetching_Agents import get_meter_data_with_last_comm_json
from test_graph import build_graph
import tempfile

graph=build_graph()

def is_validate(projectid,client_id,username,password):

    is_projectId_validate=get_meter_data_with_last_comm_json(projectid)
    is_creds=generate_access_token(client_id,username,password)

    if is_projectId_validate and is_creds :
        return True
    else :
        return False

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
    start_time = time.time()



if uploaded_file and st.button("🚀 Run Test Suite"):
    with st.spinner("Executing tests..."):
        start_time = time.time()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(uploaded_file.getbuffer())
            excel_path = tmp.name

        final_state = graph.invoke({
            "excel_file": excel_path,
            "projectid": projectid,
            "client_id": client_id,
            "username": username,
            "password": password
        })

        st.session_state["final_state"] = final_state
        st.session_state["report_metrics"] = final_state.get("report_metrics", {})

        end_time = time.time()
        st.success(f"✅ Test Suite Completed in {round(end_time - start_time, 2)} sec")

st.divider()


        



