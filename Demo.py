import pandas as pd
from collections import defaultdict
from fetch_meter_from_db import *

def get_meter_ids_from_desc(desc_excel: str):

    df_desc = pd.read_excel(desc_excel)

    if "_desc" not in df_desc.columns:
        raise KeyError("Column '_desc' not found")

    json_data = get_meter_data_with_last_comm_json()

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



def get_meterid_and_time(excel_file):
    result = get_meter_ids_from_desc(excel_file)

    meter_ids = result["meter_id"].tolist()
    communication_dates = result["communication_date"].tolist()

    return meter_ids ,communication_dates



















