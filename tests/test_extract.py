from pipelines.extract import common


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_paged_get_reads_all_pages_and_stops_at_total(monkeypatch):
    data = [{"id": i} for i in range(5)]
    calls = []

    def fake_get(url, params, timeout):
        calls.append(params["skip"])
        page = data[params["skip"]:params["skip"] + params["limit"]]
        return FakeResponse({"users": page, "total": len(data)})

    monkeypatch.setattr(common.requests, "get", fake_get)
    out = list(common.paged_get("http://x/users", "users", limit=2, pause=0))

    assert out == data
    assert calls == [0, 2, 4]  # no extra empty request after the last page
