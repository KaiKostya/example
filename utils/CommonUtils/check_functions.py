from typing import Any

from requests import Response

from NestorBriefAutotests.utils.CommonUtils.dict_list_helper import DictListHelper
from NestorBriefAutotests.utils.Variables.config import m3u8_file
from NestorBriefAutotests.utils.enums.markup.markup_state import MarkupState
from NestorBriefAutotests.utils.enums.recorder_service_state import RecorderServiceState
from NestorBriefAutotests.utils.models.sqlite_state import SqliteState
from NestorBriefAutotests.utils.services.service_status import ServiceStatus
from NestorBriefAutotests.utils.test_logging.logger import Logger


class CheckFunctions:
    """checks if the value matches the conditions"""

    @staticmethod
    def check_true(value: bool) -> bool:
        return value is True

    @staticmethod
    def check_false(value: bool) -> bool:
        return value is False

    @staticmethod
    def check_empty(value: list) -> bool:
        return value == []

    @staticmethod
    def check_is_not_empty(value: list) -> bool:
        return value != []

    @staticmethod
    def check_none(value: Any) -> bool:
        return value is None

    @staticmethod
    def check_is_not_none(value: Any) -> bool:
        return value is not None

    @staticmethod
    def check_is_not_null(value: int) -> bool:
        return value != 0

    @staticmethod
    def check_is_null(value: int) -> bool:
        return value == 0

    @staticmethod
    def check_is_not_two(value: int) -> bool:
        return value != 2

    @staticmethod
    def check_is_not_three(value: int) -> bool:
        return value != 3

    @staticmethod
    def check_api_is_success_false(value: Response) -> bool:
        return value.json()["isSuccess"] is False

    @staticmethod
    def check_is_less_three(value: Any) -> bool:
        if value is not None and value != []:
            return value < 3
        else:
            return False

    @staticmethod
    def check_is_not_running(value) -> bool:
        value = value.as_dict()["status"]
        return value != ServiceStatus.running

    @staticmethod
    def str_check_is_not_running(value: str) -> bool:
        return value != ServiceStatus.running

    @staticmethod
    def str_check_is_not_stopped(value: str) -> bool:
        return value != ServiceStatus.stopped

    @staticmethod
    def check_m3u8_file_not_in_list(value: list) -> bool:
        return m3u8_file not in value

    @staticmethod
    def check_adf_files(value: list) -> bool:
        for arr in value:
            for f in arr:
                if "adf" in f.split("\\")[-1]:
                    if f is not None:
                        return False
        return True

    @staticmethod
    def check_no_adf_files(value: list) -> bool:
        for arr in value:
            for f in arr:
                if "adf" in f.split("\\")[-1]:
                    if f is not None:
                        return True
        return False

    @staticmethod
    def check_is_not_one(value: int) -> bool:
        return value != 1

    @staticmethod
    def check_less_than_five(value: int) -> bool:
        return value < 5

    @staticmethod
    def check_len_is_not_two(value: Any) -> bool:
        return len(value) != 2

    @staticmethod
    def check_len_is_not_one(value: Any) -> bool:
        return len(value) != 1

    @staticmethod
    def check_len_is_not_null(value: Any) -> bool:
        return len(value) != 0

    @staticmethod
    def check_len_is_null(value: Any) -> bool:
        return len(value) == 0

    @staticmethod
    def check_markup_status_in_not_finished(value) -> bool:
        if value:
            return value != MarkupState.FINISHED.value
        else:
            return True

    @staticmethod
    def check_sqlite_state_not_paused(value: str) -> bool:
        return value != SqliteState.PAUSED

    @staticmethod
    def check_is_not_3599(value: int) -> bool:
        return value != 3599

    @staticmethod
    def extracted_less_two(value: list[list[Any]], ind: int) -> bool:
        """value - 2-dimensional list from Db
        ind - which index use to take element"""
        less = False
        for _el in value:
            if _el[ind] < 2:
                less = True
                break
        return less

    @staticmethod
    def check_at_least_one_rec_service_state_not_ready(value: Response) -> bool:
        try:
            return all(RecorderServiceState(_el) != RecorderServiceState.Ready for _el in
                       DictListHelper.collect_values_to_list(value.json()["result"], "state"))
        except Exception:
            return True

    @staticmethod
    def check_rec_service_state_not_paused(value: Response) -> bool:
        try:
            return RecorderServiceState(value.json()["result"]["state"]) != RecorderServiceState.Paused
        except Exception:
            return True

    @staticmethod
    def check_rec_service_state_not_recording(value: Response) -> bool:
        try:
            return RecorderServiceState(value.json()["result"]["state"]) != RecorderServiceState.Recording
        except Exception:
            return True

    @staticmethod
    def check_recording_time_less_20(value: Response) -> bool:
        try:
            _time = value.json()["result"]["recordingTime"]
            _result_time = int(_time[-8:-6])*3600 + int(_time[-5:-3])*60 + int(_time[-2:])
            Logger.utils_logger.info(f"Current time: {_result_time}")
            return _result_time < 20
        except Exception:
            Logger.utils_logger.exception(f"Exception while evaluate in check_recording_time_greater_20 func")
            return True
