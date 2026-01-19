
import json

def build_assertion_result(status_code, response, expected):
    try:
        if expected is None:
            return "No expected result provided", "FAIL"

        if isinstance(expected, str):
            expected = json.loads(expected)

        if isinstance(response, str):
            response = json.loads(response)

        if response.get("status") == 400 and expected.get("status") == 400:
            return (
                "Status code match | Expected: 400 | Actual: 400",
                "PASS"
            )

        
        exp_success = expected.get("success")
        if exp_success is True:
            expected_status = 200
        else:
            expected_status = 400

        
        if response.get("success") is True:
            actual_status = 200
        else:
            actual_status = response.get("status")

      
        if expected_status == 200 and actual_status == 200:
            request_id = response.get("requestId")
            types = type(request_id)

            if request_id and request_id > 0:
                return (
                    f"Status code match with 200 | requestId > 0 ({types}) | Message Success : True",
                    "PASS"
                )

       
        return (
            f"Status code mismatch | Expected: {expected_status} | Actual: {actual_status}",
            "FAIL"
        )

    except Exception as e:
        return f"Error: {e}", "FAIL"


def result_from_assertion_text(value):
    if not value:
        return "FAIL"

    if isinstance(value, tuple):
        value = " ".join(map(str, value))

    if isinstance(value, list):
        value = " ".join(map(str, value))

    value = str(value).lower()

    if "false" in value or "mismatch" in value or "fail" in value:
        return "FAIL"

    return "PASS"


def RequestID_Assertions(request_parameter, body_request_response):

    if not isinstance(request_parameter, dict):
        return "Invalid request parameters"

    if not isinstance(body_request_response, dict):
        return "Invalid response body"

    Request_meternumber = request_parameter.get("meterNo")
    Request_bodyMeter = body_request_response.get("MeterNo")
    RequestId = body_request_response.get("RequestId")
    RequestState = body_request_response.get("RequestState")
    commandType = request_parameter.get("commandType")

    if Request_meternumber == Request_bodyMeter:
        if body_request_response.get("Success") is True:
            return (
                f"commandType: {commandType} | "
                f"RequestId: {RequestId} | "
                f"RequestState: {RequestState} | "
                f"Success: True"
            )

    Message = body_request_response.get("Message")
    status = body_request_response.get("status")



    return (
        # f"commandType: {commandType} | "
        f" Not Applicable for status: {status}"
        # f"Message: {Message}"
    )









# def RequestID_Assertions(request_parameter,body_request_response):

#     Request_meternumber =request_parameter.get("meterNo")
#     Request_bodyMeter = body_request_response.get("MeterNo")
#     RequestId=body_request_response.get("RequestId")
#     RequestState =body_request_response.get("RequestState")
#     commandType = request_parameter.get("commandType")

#     if Request_meternumber == Request_bodyMeter :
#         if body_request_response.get("Success") is True :
#             return f"commandType: {commandType} - Connect | RequestId: {RequestId} | RequestState: {RequestState} | Success True" ##f"RequestId | {RequestId}"
#         # if body_request_response.get("RequestId"):
#         #     return f"RequestId: {RequestId}"
#         # if body_request_response.get("RequestState") :
#         #     return f"RequestState: {RequestState}"
#         # return "Meter Number Match"
     
#     else:
#         Message =body_request_response.get("Message")
#         status = body_request_response.get("status")
#         return f"commandType: {commandType} - Disconnect | status {status}"
    
    

  








# def build_assertion_result(status_code, response, expected):
#     try:
#         if expected is None:
#             return "No expected result provided", "FAIL"

#         if isinstance(expected, str):
#             try:
#                 expected = json.loads(expected)
#             except Exception:
#                 return "Expected result is not valid JSON", "FAIL"

#         if isinstance(response, str):
#             try:
#                 response = json.loads(response)
#             except Exception:
#                 return "Response is not valid JSON", "FAIL"

#         expected_status = expected.get("status", 200)
        
#         if status_code != expected_status:
#             return (
#                 f"Status code mismatch | Expected: {expected_status} | Actual: {status_code}",
#                 "FAIL"
#             )
        
#         if status_code == 200:
#             exp_success = expected.get("success")
#             act_success = response.get("success")
#             expected_requestId_id = response.get("requestId")

#             types = type(expected_requestId_id)

#             if exp_success == act_success and expected_requestId_id != 0:
#                 return (
#                     f"Status code match with 200 | requestId > 0 ({types}) | Message Success : True",
#                     "PASS"
#                 )
#             # else:
#             #     return (
#             #         "Status code match with 200 | Message Success : False",
#             #         "FAIL"
#             #     )

#         if response.get("status") and expected.get("status") == 400:               #and status_code == 400:
#             return ("Status code match with 400", "PASS")
#         else:
#             return (
#                 f"Status code mismatch | Expected: {expected_status} |","FAIL" #Actual: {status_code}
#             )

#     except Exception as e:
#         return f"Error: {e}", "FAIL"