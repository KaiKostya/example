import sys
import time
from typing import Callable

from NestorBriefAutotests.utils.CommonUtils.check_functions import CheckFunctions
from NestorBriefAutotests.utils.Variables.constants import waiter_exception
from NestorBriefAutotests.utils.exceptions.test_exception import TestWaiterException
from NestorBriefAutotests.utils.test_logging.logger import Logger


class Waiter:

    @staticmethod
    def wait_many_args(func, **kwargs):
        param1 = kwargs.pop("param1", None)
        param2 = kwargs.pop("param2", None)
        check_func = kwargs.pop("check_func", CheckFunctions.check_empty)
        timeout_value = kwargs.pop("timeout_value", 20)
        extract = kwargs.pop("extract", False)
        timeout_interval = kwargs.pop("timeout_interval", 1)

        Logger.utils_logger.debug(f"wait(func = {func.__name__}, param1 ={param1}, param2 = {param2}, "
                                  f"check_func = {check_func.__name__}, timeout_value = {timeout_value}, "
                                  f"extract = {extract})")
        exc_raise_if_fail = TestWaiterException()
        timeout = 0
        in_while = True
        while in_while:
            try:
                if param1 is None and param2 is None:
                    value = func()
                elif param2 is None:
                    value = func(param1)
                else:
                    value = func(param1, param2)
            except Exception as ex:
                if timeout == timeout_value:
                    exc_raise_if_fail.with_traceback(sys.exc_info()[2])
                    exc_raise_if_fail.txt += ": " + ex.args[0]
                    in_while = False
                value = None
            if not ((timeout <= timeout_value) and (check_func(value))):
                in_while = False
            time.sleep(timeout_interval)
            timeout += timeout_interval
        if value is None and check_func != CheckFunctions.check_is_not_none:
            Logger.utils_logger.critical(f"{exc_raise_if_fail.txt}")
            raise exc_raise_if_fail
        else:
            Logger.utils_logger.debug(f"Waiter completed in {timeout} sec")
        if extract:
            return value[0][0]
        else:
            return value

    @staticmethod
    def wait_and_check(func, param1=None, param2=None, check_func=CheckFunctions.check_empty,
                       timeout_value=20, extract=False):
        return Waiter.wait_many_args(func=func, param1=param1, param2=param2, check_func=check_func,
                                     timeout_value=timeout_value,
                                     extract=extract, timeout_interval=1)

    # Extract - не нужен. Вместо передачи true можно успешно в лямбду это втыкать. Нужен будет - добавим.
    @staticmethod
    def wait_new(func: Callable, check_func: Callable = CheckFunctions.check_empty, timeout_value: int = 20,
                 timeout_interval: int = 1, error_message: str = ""):
        value = waiter_exception
        exc_raise_if_fail = TestWaiterException()
        timeout = 0
        in_while = True
        Logger.utils_logger.debug(f"timeout_value = {timeout_value}, timeout_interval = {timeout_interval})")
        while in_while:
            try:
                value = func()
            except Exception as ex:
                if timeout == timeout_value:
                    exc_raise_if_fail.with_traceback(sys.exc_info()[2])
                    exc_raise_if_fail.txt += ": " + ex.args[0]
                    in_while = False
                value = waiter_exception
                Logger.utils_logger.debug(f"Exception", exc_info=True)
            finally:
                Logger.utils_logger.debug(f"Current value: {value}")
                if (timeout > timeout_value) or (value != waiter_exception and not check_func(value)):
                    break
                else:
                    timeout += timeout_interval
                    time.sleep(timeout_interval)
        if value == waiter_exception:
            Logger.utils_logger.critical(f"{exc_raise_if_fail.txt}, {error_message}")
            raise exc_raise_if_fail
        return value
