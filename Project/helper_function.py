import json
from fetch_meter_from_db import get_filter_data

def parse_test_data(raw_body: str) -> dict:
    result = {}
    for line in raw_body.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.isdigit():
                value = int(value)

            result[key] = value
    return result

def get_commandType_only(data, allow_set_commandtype,projectid):

    if "filtered_data" not in data:
        print("Invalid JSON structure")
        return None

    for item in data["filtered_data"]:
        raw_body = item.get("_Test Data", "")
        parsed_json = parse_test_data(raw_body)

        get_commandType = parsed_json.get("commandType")

        set_df, _ = get_filter_data(projectid)
        set_values = set_df["set_commandtype"].values

        if not allow_set_commandtype:
            if get_commandType in set_values:
                return None
            return parsed_json

        return parsed_json







# def get_commandType_only(data, allow_set_commandtype):
#     # data = json.loads(data) if isinstance(data, str) else data

#     if "filtered_data" not in data:
#         print("Invalid JSON structure")
#         return None

#     for item in data["filtered_data"]:
#         raw_body = item.get("_Test Data", "")
#         parsed_json = parse_test_data(raw_body)

#         get_commandType = parsed_json.get("commandType")

#         set_df, _ = get_filter_data(1)
#         set_values = set_df["set_commandtype"].values

#         if not allow_set_commandtype:
#             if get_commandType in set_values:
#                 return None
#             return parsed_json

#         else:
#             if get_commandType in set_values:
#                 return parsed_json
#             return None



# print(get_commandType_only(data,allow_set_commandtype=False))