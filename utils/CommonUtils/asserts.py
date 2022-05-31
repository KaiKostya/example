import json
from typing import Optional

from NestorBriefAutotests.utils.CommonUtils.validation import Validation
from NestorBriefAutotests.utils.api.api_helpers.pretty_prints import Printer
from NestorBriefAutotests.utils.api.api_helpers.response_schemas import ResponseSchemas
from NestorBriefAutotests.utils.models.status_code import StatusCode
from NestorBriefAutotests.utils.test_logging.logger import Logger
from requests.models import Response


class Asserts:
    @staticmethod
    def assert_success(response: Optional[Response]):
        Asserts.print_response(response)
        if response.status_code == StatusCode.NoContent:
            assert True
        else:
            assert response.status_code == StatusCode.Success
            assert response.json()["errorMessage"] is None
            assert response.json()["isSuccess"] is True
            assert type(response.json()["serverTime"]) is ResponseSchemas().get_schema(response)["serverTime"]

    @staticmethod
    def assert_success_new_api(response: Optional[Response], status_code="any"):
        assert response is not None
        Asserts.print_response(response)
        if status_code != "any":
            assert response.status_code == status_code
        if response.status_code == StatusCode.Success:
            response_body = json.loads(response.text)
            if type(response_body) is dict:
                assert response_body != {}, "Success response with empty dict! Response: {}"
                if "isSuccess" in response_body.keys():
                    assert response.json()["isSuccess"] is True
                if "errorMessage" in response_body.keys():
                    assert response.json()["errorMessage"] is None
            elif type(response_body) is str:
                assert response_body != "", "Success response with empty string! Response: \"\""
            elif type(response_body) is bytes:
                assert response_body != b''
            elif type(response_body) is bool:
                assert True
            elif type(response_body) is int:
                assert True
            else:
                Logger.tests_logger.info(f"Type of response body: {type(response_body)}")
                assert type(response_body) is list
        elif response.status_code == StatusCode.NoContent:
            assert response.text == '', f"NoContent response with content: {response.text}"
        elif response.status_code == StatusCode.Created:
            assert response.text == '', f"Created response with content: {response.text}"
        else:
            assert response.status_code == StatusCode.Success

    @staticmethod
    def check_response_not_success_new_api(response: Optional[Response], status_code="any"):
        try:
            Asserts.assert_success_new_api(response, status_code)
            return False
        except Exception:
            return True

    @staticmethod
    def assert_fail(response: Optional[Response]):
        Asserts.print_response(response)
        assert response.status_code == StatusCode.Success
        assert response.json()["isSuccess"] is False
        assert type(response.json()["errorMessage"]) is ResponseSchemas().get_schema(response)["errorMessage"]
        assert type(response.json()["serverTime"]) is ResponseSchemas().get_schema(response)["serverTime"]

    @staticmethod
    def assert_fail_new_api(response: Optional[Response], status_code="any"):
        Asserts.print_response(response)
        assert response is not None
        if status_code != "any":
            assert response.status_code == status_code, f"Status code was {response.status_code}, expected {status_code}"
        if response.status_code == StatusCode.NoContent:
            assert False, f"Status code was {response.status_code}, expected {status_code}"
        response_body = json.loads(response.text)
        if response.status_code == StatusCode.Success:
            assert response_body["isSuccess"] is False
            assert response_body["errorMessage"] is not None
        elif response.status_code == StatusCode.NotFound:
            for _key in response_body.keys():
                if _key == "traceId":
                    Validation.check_trace_id(response_body["traceId"])
                elif _key == "detail":
                    assert type(response_body[_key]) is ResponseSchemas.not_found()[_key]
                elif _key == "type":
                    assert response_body[_key] == ResponseSchemas.not_found()[_key]
                elif _key == "title":
                    assert type(response_body[_key]) == ResponseSchemas.not_found()[_key]
                else:
                    assert response_body[_key] == ResponseSchemas.not_found()[_key], \
                        f"expected: {ResponseSchemas.not_found()[_key]}, actual: {response_body[_key]}"
        elif response.status_code == StatusCode.BadRequest:
            for _key in response_body.keys():
                if _key == "traceId":
                    Validation.check_trace_id(response_body["traceId"])
                elif _key == "detail":
                    assert type(response_body[_key]) is ResponseSchemas.bad_request()[_key]
                elif _key == "type":
                    assert response_body[_key] in ResponseSchemas.bad_request()[_key]
                elif _key == "title":
                    assert type(response_body[_key]) == ResponseSchemas.bad_request()[_key]
                elif _key == "status":
                    assert response_body[_key] == ResponseSchemas.bad_request()[_key]
                elif _key == "errors":
                    assert type(response_body[_key]) in ResponseSchemas.bad_request()[_key]
                else:
                    assert response_body[_key] == ResponseSchemas.bad_request()[_key]
        elif response.status_code == response.status_code == StatusCode.Forbidden:
            for _key in response_body.keys():
                if _key == "traceId":
                    Validation.check_trace_id(response_body["traceId"])
                elif _key == "detail":
                    assert type(response_body[_key]) is ResponseSchemas.forbidden()[_key]
                else:
                    assert response_body[_key] == ResponseSchemas.forbidden()[_key]
        elif response.status_code == StatusCode.NotAllowed:
            Logger.tests_logger.info(f"Response: {response}, {response.text}")
            assert False # если упадет в этом месте, то нужно посмотреть, какое тело ответа при 405 коде и добавить
            # поля для проверки

    @staticmethod
    def print_response(response: Optional[Response]):
        Printer().pretty_print_request(response.request)
        assert response is not None
        Printer().pretty_print_response(response)
