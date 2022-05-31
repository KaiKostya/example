from datetime import datetime, timedelta

import pytest

from NestorBriefAutotests.tests.base_test import TestBase
from NestorBriefAutotests.utils.CommonUtils.asserts import Asserts
from NestorBriefAutotests.utils.CommonUtils.waiter import Waiter
from NestorBriefAutotests.utils.DbManagers.Orm.Mapping.local_session import DbLocalSession
from NestorBriefAutotests.utils.DbManagers.Orm.Mapping.service_settings import DbServiceSettings
from NestorBriefAutotests.utils.Variables.constants import manual_duration_thirty, initial_manual_duration
from NestorBriefAutotests.utils.Variables.services import server_service
from NestorBriefAutotests.utils.api.internal.record.record import Record
from NestorBriefAutotests.utils.api.internal.session.local_session import LocalSession
from NestorBriefAutotests.utils.api.internal.session.local_session_management import LocalSessionManagement
from NestorBriefAutotests.utils.enums.api_recording_mode import ApiRecordingMode
from NestorBriefAutotests.utils.test_logging.logger import Logger


class AutostartBase(TestBase):
    _session = None
    _hall = None
    _auth = None
    _record = None
    _delta_start = None
    _delta_finish = None
    _planned_end_time = None
    _create_session_response = None
    _planned_start_time = None
    _test_max_manual_duration = manual_duration_thirty
    _initial_max_manual_duration = initial_manual_duration

    @pytest.fixture(scope="class", autouse=True)
    def create__hall(self, create_hall, get_auth):
        AutostartBase._hall = self.hall
        AutostartBase._auth = self.auth

    @pytest.fixture(scope="class")
    def change_max_manual_duration(self, request):
        try:
            def finalizer():
                server_service.set_max_manual_duration(AutostartBase._initial_max_manual_duration)

            request.addfinalizer(finalizer)
            server_service.set_max_manual_duration(AutostartBase._test_max_manual_duration)
            max_manual_duration = DbServiceSettings.get_service_settings_by_service_id(
                server_service.get_service_id(), as_dict=True)["MaxManualRecordDuration"]
            Logger.tests_logger.debug(f"MaxManualRecordDuration in Db after changing: {max_manual_duration}")
        except Exception:
            Logger.tests_logger.error("Fixture change_max_manual_duration Exception", exc_info=True)
            pytest.skip("Fixture change_max_manual_duration failure")

    @staticmethod
    def create_planned_session(delta_start, delta_finish, hall=None):
        AutostartBase._start_mode = ApiRecordingMode.Manual
        AutostartBase._end_mode = ApiRecordingMode.Manual
        planned_start_date = None
        planned_end_date = None
        time_now = datetime.utcnow()
        session_hall = (hall, AutostartBase._hall)[hall is None]
        Logger.tests_logger.info(f"Time now: {time_now}")
        if delta_start is not None:
            AutostartBase._planned_start_time = time_now + timedelta(seconds=delta_start)
            Logger.tests_logger.info(f"Planned start date: {AutostartBase._planned_start_time}")
            planned_start_date = str(AutostartBase._planned_start_time)
            AutostartBase._start_mode = ApiRecordingMode.Auto
        if delta_finish is not None:
            AutostartBase._planned_end_time = time_now + timedelta(seconds=delta_finish)
            Logger.tests_logger.info(f"Planned end date: {AutostartBase._planned_end_time}")
            planned_end_date = str(AutostartBase._planned_end_time)
            AutostartBase._end_mode = ApiRecordingMode.Auto
        AutostartBase._session = LocalSession(session_hall.id, start_recording_mode=AutostartBase._start_mode,
                                              end_recording_mode=AutostartBase._end_mode,
                                              scheduled_time=planned_start_date,
                                              scheduled_end_time=planned_end_date)
        AutostartBase._create_session_response = \
            Waiter.wait_new(lambda: LocalSessionManagement.create_local_session(AutostartBase._auth,
                                                                                AutostartBase._session),
                            check_func=Asserts.check_response_not_success_new_api)
        Asserts.assert_success_new_api(AutostartBase._create_session_response)
        AutostartBase._record = Record(AutostartBase._session, session_hall, need_record_id=True)

    @staticmethod
    def wait_session_state(_session, time_to_wait: int, wait_for) -> int:
        return Waiter.wait_new(lambda: DbLocalSession.get_local_sessions_by_session_id(_session.session_id)[0].state,
                               check_func=lambda value: value != wait_for.value, timeout_value=time_to_wait)
