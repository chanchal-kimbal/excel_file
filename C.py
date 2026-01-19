####### New Updation with input Project id's #########
import psycopg2
import pandas as pd
import json
from collections import defaultdict
# from is_excel_header_validate import *
import os
from dotenv import load_dotenv


######## New Updation for the config file #########


load_dotenv()  # loads .env into environment

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def get_meter_data_with_last_comm_json(projectid):
    try:

        conn = psycopg2.connect(**DB_CONFIG)

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
    except Exception as e :
        return f"Error: {e}"




##################################  ******** ############################


def get_meter_ids_from_desc(desc_excel,projectid):
    
    df_desc = pd.read_excel(desc_excel)

    df_desc=align_excel_headers(df_desc)

    if "_desc" not in df_desc.columns:
        raise KeyError("Column '_desc' not found")

    json_data = get_meter_data_with_last_comm_json(projectid)

    df_map = pd.read_json(json_data)

    required_cols = {"meter_type(phase)", "meternumber", "lastcommunicatedat"}
    if not required_cols.issubset(df_map.columns):
        raise KeyError("Required columns missing")

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

    return df_desc["_desc"].apply(lambda d: pd.Series(extract_meter_and_date(d),index=["meter_id", "communication_date"]))
    
    
def get_meterid_and_time(excel_file,projectid):
    
            
    result = get_meter_ids_from_desc(excel_file,projectid)
    meter_ids = result["meter_id"].tolist()
    communication_dates = result["communication_date"].tolist()

    return meter_ids ,communication_dates
    



############## for the Set and Get commands ##########


def get_command_type_value(projectid):
    
    conn = psycopg2.connect(**DB_CONFIG)

    query = """
    SELECT commandtype, commandvalue
    FROM command_type_settings
    WHERE projectid = %s;
    """

    df = pd.read_sql(query, conn, params=[projectid])
    conn.close()

    return df


def split_set_commands(df):
    
    df["commandvalue"] = df["commandvalue"].astype(str)

    set_df = df[df["commandvalue"].str.startswith("Set")].copy()

    rest_df = df[~df["commandvalue"].str.startswith("Set")].copy()

    set_df = set_df.rename(columns={
        "commandtype": "set_commandtype",
        "commandvalue": "set_commandvalue"
    })

    return set_df, rest_df


def get_filter_data(projectid):
    df_commands = get_command_type_value(projectid)
    set_df, rest_df = split_set_commands(df_commands)
    return set_df ,rest_df




################  Final check the reason  #######################



def get_command_reason(projectid, requestid):

    conn = psycopg2.connect(**DB_CONFIG)
   
    query = """
    SELECT reason
    FROM public.commands
    WHERE projectid = %s
      AND requestid = %s;
    """

    df = pd.read_sql(query, conn, params=[projectid, requestid])
    conn.close()

    return df["reason"]