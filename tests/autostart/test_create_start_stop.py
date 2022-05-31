import time
from datetime import datetime

import pytest
from pytest_testrail.plugin import testrail as rail

from tests.autostart.base.autorecord_common import AutoRecordCommon
from tests.autostart.base.autostart_base import AutostartBase
from utils.CommonUtils.asserts import Asserts
from utils.DbManagers.Orm.Mapping.import_process import DbImportProcess
from utils.Variables.config import markup_file_path_2mics
from utils.api.internal.import_management.manual_import import ManualImport
from utils.api.internal.session.local_session_management import LocalSessionManagement
from utils.enums.session_state import SessionState
from utils.test_logging.logger import Logger


@pytest.mark.dependency(depends=["create_session_response"], scope="class")
class TestCreateStartStop(AutostartBase):
    _delta_start = 20
    _delta_finish = 60
    _post_import_response = None
    _import_process = None

    @pytest.fixture(scope="class")
    def create_session_wait_autostart(self, add_default_emul, request):
        try:
            def finalizer():
                LocalSessionManagement.explore_active_sessions(AutostartBase._auth)

            request.addfinalizer(finalizer)
            super().create_planned_session(TestCreateStartStop._delta_start,
                                           TestCreateStartStop._delta_finish)
        except Exception:
            Logger.tests_logger.error("Fixture Exception", exc_info=True)
            pytest.skip("Fixture create_session_wait_start failure")

    @pytest.fixture(scope="class")
    def wait_auto_finish(self, create_session_wait_autostart):
        try:
            wait_to_finish = (TestCreateStartStop._planned_end_time - datetime.utcnow()).total_seconds()
            AutostartBase.wait_session_state(AutostartBase._session, wait_to_finish + 17, wait_for=SessionState.Finished)
        except Exception:
            Logger.tests_logger.error("Fixture Exception", exc_info=True)
            pytest.skip("Fixture wait_auto_finish failure")

    @pytest.fixture(scope="class")
    def try_post_import(self, wait_auto_finish):
        try:
            TestCreateStartStop._post_import_response = ManualImport.import_file(
                AutostartBase._auth, markup_file_path_2mics, AutostartBase._session, start_date=str(datetime.utcnow()))
        except Exception:
            Logger.tests_logger.error("Fixture Exception", exc_info=True)
            pytest.skip("Fixture try_post_import failure")

    @pytest.mark.dependency(name="create_session_response", scope="class")
    def test_session_created(self, create_session_wait_autostart):
        Asserts.assert_success_new_api(AutostartBase._create_session_response)

    def test_session_auto_started(self, create_session_wait_autostart):
        session_state_after_autostart = AutostartBase.wait_session_state(
            AutostartBase._session, TestCreateStartStop._delta_start + 17, wait_for=SessionState.Recording)
        AutoRecordCommon.check_session_recording(session_state_after_autostart)

    def test_session_auto_finished(self, wait_auto_finish):
        Logger.tests_logger.info(f"Record_id: {AutostartBase._record.record_id}")
        session_state_after_auto_finish = AutostartBase.wait_session_state(
            AutostartBase._session, 1, wait_for=SessionState.Finished)
        AutoRecordCommon.check_session_finished(session_state_after_auto_finish)

    def test_record_duration_as_expected(self, wait_auto_finish):
        Logger.tests_logger.info(f"Delta start: {TestCreateStartStop._delta_start}, delta_finish: "
                                 f"{TestCreateStartStop._delta_finish}, record_id: {AutostartBase._record.record_id}")
        AutoRecordCommon.check_record_duration(AutostartBase._session, TestCreateStartStop._delta_start,
                                               TestCreateStartStop._delta_finish)

    def test_fail_post_import_to_autostart_session(self, try_post_import):
        Asserts.assert_fail_new_api(TestCreateStartStop._post_import_response)

    def test_no_import_process_for_post_import(self, try_post_import):
        time.sleep(10)
        TestCreateStartStop._import_process = DbImportProcess.get_import_processes_by_record_id(
            AutostartBase._record.record_id)
        assert TestCreateStartStop._import_process == [], \
            f"ImportProcess exist! ProcessId: {TestCreateStartStop._import_process[0].id}"
