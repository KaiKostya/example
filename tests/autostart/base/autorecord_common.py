from NestorBriefAutotests.utils.CommonUtils.waiter import Waiter
from NestorBriefAutotests.utils.DbManagers.Orm.Mapping.audio_stream_info import DbAudioStreamInfo
from NestorBriefAutotests.utils.DbManagers.Orm.Mapping.session_records import DbSessionRecords
from NestorBriefAutotests.utils.enums.api_recording_mode import ApiRecordingMode
from NestorBriefAutotests.utils.enums.session_state import SessionState
from NestorBriefAutotests.utils.enums.stream_info_state import StreamInfoState


class AutoRecordCommon:

    @staticmethod
    def check_session_planned(_state):
        assert SessionState(_state) == SessionState.Planned, \
            f"expected session state: {SessionState.Planned}, actual state: " \
            f"{SessionState(_state)}"

    @staticmethod
    def check_session_recording(_state):
        assert SessionState(_state) == SessionState.Recording, \
            f"expected session state: {SessionState.Recording}, actual state: " \
            f"{SessionState(_state)}"

    @staticmethod
    def check_session_finished(_state):
        assert SessionState(_state) == SessionState.Finished, \
            f"expected session state: {SessionState.Finished}, actual state: " \
            f"{SessionState(_state)}"

    @staticmethod
    def check_record_duration(_session, _start, _end, record_id=None):
        if record_id is None:
            record_id = DbSessionRecords.get_session_records_by_session_id(_session.session_id)[0].id
        expected_duration = _end - _start

        def check_function(value):
            if len(value) < 1:
                return True
            else:
                return abs((value[0].end_date - value[0].start_date).total_seconds() - expected_duration) > 10

        audio_stream = Waiter.wait_new(lambda: DbAudioStreamInfo.get_audio_stream_info_by_record_id(record_id),
                                       check_func=check_function, timeout_value=60)
        actual_duration = (audio_stream[0].end_date - audio_stream[0].start_date).total_seconds()
        assert abs(expected_duration - actual_duration) < 10, f"Expected duration: {expected_duration}, " \
                                                              f"actual_duration: {actual_duration}, " \
                                                              f"audio_stream_start_date: " \
                                                              f"{audio_stream[0].start_date}, " \
                                                              f"audio_stream_end_date: {audio_stream[0].end_date}"

    @staticmethod
    def check_record_mode_manual(_key, _result, _session):
        _recording_mode = _result[_key]
        assert _recording_mode == ApiRecordingMode.Manual.name, f"session_id: {_session.session_id}, session_name: " \
                                                                f"{_session.name}, expected {_key}: {ApiRecordingMode.Manual.name}, actual {_key}: {_recording_mode}"

    @staticmethod
    def check_stream_recording(_stream_state):
        assert StreamInfoState(_stream_state) == StreamInfoState.RECORDING, \
            f"actual stream_info_state: {StreamInfoState(_stream_state)}, expected state: {StreamInfoState.RECORDING}"
