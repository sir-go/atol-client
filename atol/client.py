from uuid import uuid4
import requests
from time import sleep, time, localtime, strftime
import atol.errors as err


def _log(msg: str, *args, **kwargs):
    print("{}: {}".format(strftime("%X", localtime()), msg), *args, **kwargs)


class WebClient:
    def __init__(self,
                 server_url: str,
                 get_status_delay: float = None,
                 get_status_timeout: float = None,
                 log_fn=None):
        self.__url = server_url
        self.__get_status_delay = get_status_delay or 1.0
        self.__get_status_timeout = get_status_timeout or 10.0
        self.__log = log_fn or _log

    def _new_task(self, task: dict) -> str:
        _id = uuid4().hex
        self.__log(f"new task: id {_id} : ", task)
        r = requests.post(
            url=self.__url,
            headers={"Content-Type": "application/json"},
            json={"uuid": _id, "request": task})
        self.__log(f"new task [{_id}] request sent")
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            if r.status_code == requests.codes.bad_request:
                raise err.BadRequest(e.request)
            elif r.status_code == requests.codes.conflict:
                raise err.TaskIdCollision(f"task_id: {_id}")
            else:
                raise e
        return _id

    def _get_task_status(self, task_id: str):
        r = requests.get(f"{self.__url}/{task_id}")
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            if r.status_code == requests.codes.not_found:
                raise err.TaskNotFound(f"task_id: {task_id}")
            else:
                raise e

        answer = r.json()
        self.__log("got answer", answer)

        if "results" not in answer:
            raise err.ErrorResponse("no 'results' in the server answer")
        else:
            return answer

    def _wait_task_result(self, task_id: str):
        self.__log(f"get task [{task_id}] result")
        t0 = time()
        while time() - t0 < self.__get_status_timeout:
            sleep(self.__get_status_delay)
            task_status = self._get_task_status(task_id)

            if all((
                    result["status"] not in (
                            "wait", "blocked"
                    ) for result in task_status["results"]
            )):
                return task_status["results"]

        raise err.TaskTimeout

    def _call(self, method: str, **kwargs):
        task_data = self._wait_task_result(
            self._new_task(dict(**{"type": method}, **kwargs)))
        if any((result["status"] != "ready" for result in task_data)):
            raise err.TaskError(task_data)
        return task_data

    def get_shift_status(self):
        return self._call("getShiftStatus")

    def continue_print(self):
        return self._call("continuePrint")

    def open_shift(self, **kwargs):
        return self._call("openShift", **kwargs)

    def close_shift(self, **kwargs):
        return self._call("closeShift", **kwargs)

    def sell(self, items: list, payments: list, **kwargs):
        return self._call("sell",
                          items=items, payments=payments, **kwargs)

    def buy(self, items: list, payments: list, **kwargs):
        return self._call("buy",
                          items=items, payments=payments, **kwargs)

    def sell_return(self, items: list, payments: list, **kwargs):
        return self._call("sellReturn",
                          items=items, payments=payments, **kwargs)

    def buy_return(self, items: list, payments: list, **kwargs):
        return self._call("buyReturn",
                          items=items, payments=payments, **kwargs)

    def sell_correction(self, payments: list, taxes: list, **kwargs):
        return self._call("sellCorrection",
                          payments=payments, taxes=taxes, **kwargs)

    def buy_correction(self, payments: list, taxes: list, **kwargs):
        return self._call("buyCorrection",
                          payments=payments, taxes=taxes, **kwargs)

    def non_fiscal(self, items: list):
        return self._call("nonFiscal", items=items)

    def report_x(self, **kwargs):
        return self._call("reportX", **kwargs)

    def cash_in(self, cash_sum: float):
        return self._call("cashIn", cashSum=cash_sum)

    def cash_out(self, cash_sum: float):
        return self._call("cashOut", cashSum=cash_sum)

    def report_ofd_exchange_status(self, **kwargs):
        return self._call("reportOfdExchangeStatus", **kwargs)

    def get_registration_info(self):
        return self._call("getRegistrationInfo")

    def registration(self, reason: str, **kwargs):
        return self._call("registration", reason=reason, **kwargs)

    def fn_change(self, **kwargs):
        return self._call("fnChange", **kwargs)

    def change_registration_parameters(self, **kwargs):
        return self._call("changeRegistrationParameters", **kwargs)

    def close_archive(self, **kwargs):
        return self._call("closeArchive", **kwargs)

    def get_device_info(self):
        return self._call("getDeviceInfo")

    def get_device_status(self):
        return self._call("getDeviceStatus")

    def get_fn_info(self):
        return self._call("getFnInfo")

    def ofd_exchange_status(self):
        return self._call("ofdExchangeStatus")
