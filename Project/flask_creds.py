from fetch_meter_from_db import get_meter_data_with_last_comm_json
from user_creds import generate_access_token


def is_validate(projectid,client_id,username,password):

    is_projectId_validate=get_meter_data_with_last_comm_json(projectid)
    is_creds=generate_access_token(client_id,username,password)

    if is_projectId_validate and is_creds :
        return True
    else :
        return False
    


    