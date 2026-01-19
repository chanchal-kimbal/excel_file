
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









