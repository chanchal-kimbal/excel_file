from typing import List, Union
import pandas as pd
import re
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent 
from langchain_core.messages import HumanMessage # Ensure HumanMessage is imported here
from ollama_setup import *
from langchain_core.tools import tool
import json
import psycopg2
from collections import defaultdict



def get_meter_data_with_last_comm_json(projectid):
    conn = psycopg2.connect(
        host="52.66.27.228",
        port=5432,
        database="ehesdev",
        user="ehes",
        password="Ehes@123"
    )

    routing_query = """
    SELECT nodeid, MAX(lastcommunicatedat) AS lastcommunicatedat
    FROM meter_latestrouting
    WHERE projectid = %s
    GROUP BY nodeid;
    """
    df_routing = pd.read_sql(routing_query, conn, params=[projectid])

    nameplate_query = """
    SELECT nodeid, meternumber, metercategory
    FROM meter_nameplate
    WHERE projectid = %s;
    """
    df_nameplate = pd.read_sql(nameplate_query, conn, params=[projectid])

    if df_nameplate.empty:
        conn.close()
        return None

    df = pd.merge(df_nameplate, df_routing, on="nodeid", how="inner")

    category_map = {
        "D1": "single",
        "D2": "three",
        "D3": "LTCT",
        "D4": "HTCT"
    }
    df["meter_type(phase)"] = df["metercategory"].map(category_map)

    result_df = df[["meternumber", "meter_type(phase)", "lastcommunicatedat"]]

    conn.close()

    return json.dumps(
        result_df.to_dict(orient="records"),
        indent=2,
        default=str
    )


def get_meter_ids_from_desc(aligned_df: pd.DataFrame, projectid: str):
    # STRICT RULE: headers must already be normalized
    if "_desc" not in aligned_df.columns:
        raise KeyError("Required column '_desc' not found in aligned_df")

    json_data = get_meter_data_with_last_comm_json(projectid)
    if json_data is None:
        raise RuntimeError("No meter data found for given projectid")

    df_map = pd.read_json(json_data)

    required_cols = {"meter_type(phase)", "meternumber", "lastcommunicatedat"}
    if not required_cols.issubset(df_map.columns):
        raise KeyError("Required DB columns missing")

    df_map["lastcommunicatedat"] = (
        pd.to_datetime(df_map["lastcommunicatedat"], utc=True)
        .dt.tz_localize(None)
        .dt.strftime("%Y-%m-%d %H:%M:%S")
    )

    meter_pool = (
        df_map
        .dropna()
        .groupby("meter_type(phase)")[["meternumber", "lastcommunicatedat"]]
        .apply(lambda x: list(zip(x["meternumber"], x["lastcommunicatedat"])))
        .to_dict()
    )

    meter_index = defaultdict(int)
    meters = ["single", "three", "LTCT", "HTCT"]

    def extract_meter_and_date(desc):
        if pd.isna(desc):
            return None, None

        desc_lower = str(desc).lower()

        for meter in meters:
            if meter.lower() in desc_lower and meter in meter_pool:
                pool = meter_pool[meter]
                idx = meter_index[meter] % len(pool)
                meter_index[meter] += 1
                return pool[idx]

        return None, None

    return aligned_df["_desc"].apply(
        lambda d: pd.Series(
            extract_meter_and_date(d),
            index=["meter_id", "communication_date"]
        )
    )




@tool
def get_meterid_and_time(aligned_df: pd.DataFrame, projectid: str):
    """
    Extract meter IDs and last communication timestamps
    using DB-derived routing data and Excel descriptions
    """
    result = get_meter_ids_from_desc(aligned_df, projectid)

    meter_ids = result["meter_id"].tolist()
    communication_dates = result["communication_date"].tolist()

    return meter_ids, communication_dates




system_prompt="""

You are a Data Fetching Agent in a multi-agent test execution pipeline.

Your responsibility is to extract all required execution inputs from the shared state produced by previous agents.

You must:

Read aligned_df and projectid from the state.

Validate that aligned_df exists and is a valid dataframe-like structure.

Derive meter_ids and communication_dates strictly from aligned_df using the approved data-extraction tool.

Never infer, fabricate, or hard-code values.

Preserve data integrity and ordering.

Write only the following keys back into the state:

meter_ids

communication_dates

Do not modify, delete, or rename any other state fields.

If required inputs are missing or invalid, fail immediately with a clear runtime error.

Your output must be deterministic, structured, and ready for downstream planning and execution agents.

"""

def fetching_agent():
    llm = ChatOllama(model="llama3.1:8B",temperature=0.2)
    tools = [get_meterid_and_time]
    understanding_agent = create_react_agent(model=llm,tools=tools,name="fetching_agent",prompt=system_prompt)
    return understanding_agent



def data_fetching_agents(state):
    aligned_df = state.get("aligned_df")

    if aligned_df is None:
        raise RuntimeError("aligned_df missing for data_fetching_agents")

    meter_ids, communication_dates = get_meterid_and_time.invoke({
        "aligned_df": aligned_df,
        "projectid": state["projectid"]
    })

    state["meter_ids"] = meter_ids
    state["communication_dates"] = communication_dates
    return state











































