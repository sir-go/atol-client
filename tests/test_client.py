import io
import re
import sys

import pytest
import responses
import requests

from atol.client import _log, WebClient
import atol.errors as err

fake_url = 'http://localhost'
re_uuid = re.compile(r"([a-z0-9]){32}")
re_uuid_url = re.compile(fake_url + r'/([a-z0-9]){32}')


def test__log():
    captured_out = io.StringIO()
    sys.stdout = captured_out
    _log('test')
    sys.stdout = sys.__stdout__
    assert re.match(r'(\d{2}:){3}\stest\n', captured_out.getvalue())


@pytest.fixture
def client():
    return WebClient(fake_url, 0.05, 0.1, lambda *args, **kwargs: None)


@pytest.fixture
def resp():
    with responses.RequestsMock() as r:
        yield r


def test__new_task(client, resp):
    resp.post(fake_url, status=200)
    assert re_uuid.match(client._new_task({"type": "test"}))

    resp.post(fake_url, status=400)
    with pytest.raises(err.BadRequest):
        client._new_task({"type": "bad"})

    resp.post(fake_url, status=409)
    with pytest.raises(err.TaskIdCollision):
        client._new_task({"type": "collision"})

    resp.post(fake_url, status=501)
    with pytest.raises(requests.HTTPError):
        client._new_task({"type": "error"})


def test__get_task_status(client, resp):
    resp.get(f"{fake_url}/some-valid-uuid", status=200, json={"results": []})
    assert client._get_task_status(
        task_id="some-valid-uuid") == {"results": []}

    resp.get(f"{fake_url}/some-unknown-uuid", status=404)
    with pytest.raises(err.TaskNotFound):
        client._get_task_status(task_id="some-unknown-uuid")

    resp.get(f"{fake_url}/some-bad-uuid", status=409)
    with pytest.raises(requests.HTTPError):
        client._get_task_status(task_id="some-bad-uuid")

    resp.get(f"{fake_url}/some-valid-uuid-bad-resp", status=200,
             json={"uuid": "some-valid-uuid-bad-resp"})
    with pytest.raises(err.ErrorResponse):
        client._get_task_status(task_id="some-valid-uuid-bad-resp")


def test__wait_task_result(client, resp):
    url = f"{fake_url}/uuid"
    resp.get(url, status=200, json={"results": [{"status": "ready"}]})
    assert client._wait_task_result(task_id="uuid") == [{"status": "ready"}]

    for case in [
        {"results": [{"status": "wait"}]},
        {"results": [{"status": "blocked"}]},
        {"results": [{"status": "wait"}, {"status": "ready"}]},
        {"results": [{"status": "blocked"}, {"status": "done"}]},
    ]:
        resp.get(url, status=200, json=case)
        with pytest.raises(err.TaskTimeout):
            client._wait_task_result(task_id="uuid")


def test__call(client, resp):
    resp.post(fake_url, status=200)
    resp.get(re_uuid_url, status=200,
             json={"results": [{"status": "ready", "res": 1}]})
    assert client._call(
        'methodName', p0=1, p1="v") == [{"status": "ready", "res": 1}]

    resp.get(re_uuid_url, status=200,
             json={"results": [{"status": "hold", "res": 1}]})
    with pytest.raises(err.TaskError):
        client._call('methodName', p0=1, p1="v")
