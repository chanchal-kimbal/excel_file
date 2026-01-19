import streamlit as st
import pandas as pd
import json
import time
from io import BytesIO

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


def report_agents(state):
    
    df = state.get("final_results_df")

    if not isinstance(df, pd.DataFrame):
        raise RuntimeError("❌ final_results_df missing or invalid in report agent")

    
    total = len(df)
    passed = len(df[df["result"] == "PASS"])
    failed = len(df[df["result"] == "FAIL"])
    pass_pct = round((passed / total) * 100, 2) if total else 0

    
    st.markdown("## 📊 Test Execution Summary")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Tests", total)
    m2.metric("🟢 Passed", passed)
    m3.metric("🔴 Failed", failed)
    m4.metric("Pass %", f"{pass_pct}%")

    st.divider()

   
    st.markdown("### 🔍 Filter Results")

    status_filter = st.multiselect(
        "",
        options=df["result"].unique().tolist(),
        default=df["result"].unique().tolist(),
        label_visibility="collapsed"
    )

    filtered_df = df[df["result"].isin(status_filter)]

    
    display_df = filtered_df.copy()

    display_df["Request Body"] = display_df["request_parameter"].apply(pretty_kv)
    display_df["Response"] = display_df["response"].apply(pretty_kv)
    display_df["Expected Result"] = display_df["expected_result"].apply(pretty_kv)

    display_df = display_df[
        [
            "test_id",
            "description",
            "Request Body",
            "Response",
            "Expected Result",
            "assertion_result",
            "result",
            "Taking_time(seconds)"
        ]
    ]

    display_df["result"] = display_df["result"].map({
        "PASS": "🟢 PASS",
        "FAIL": "🔴 FAIL"
    })


    st.markdown("### 📋 Detailed Test Results")

    st.dataframe(
        display_df,
        width="stretch",
        height=700,
        column_config={
            "test_id": st.column_config.TextColumn("Test ID", width="small"),
            "description": st.column_config.TextColumn("Description", width="large"),
            "Request Body": st.column_config.TextColumn("Request Body", width="large"),
            "Response": st.column_config.TextColumn("Response", width="large"),
            "Expected Result": st.column_config.TextColumn("Expected Result", width="large"),
            "assertion_result": st.column_config.TextColumn("Assertion", width="medium"),
            "result": st.column_config.TextColumn("Result", width="small"),
            "Taking_time(seconds)": st.column_config.NumberColumn(
                "Time (s)", format="%.3f", width="small"
            ),
        }
    )

    st.divider()


    excel_data = to_excel(display_df)

    st.download_button(
        "📥 Download Results as Excel",
        data=excel_data,
        file_name="EHES_Test_Results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


    state["report_metrics"] = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_pct": pass_pct
    }

    return state

























