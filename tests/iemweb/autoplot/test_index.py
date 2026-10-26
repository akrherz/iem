"""Run a bunch of URLs through the autoplot system."""

from pathlib import Path

import pytest
import requests
from iemweb.autoplot.index import (
    DAT_GID_RE,
    add_content_to_res,
    add_to_plotvars,
    application,
    compute_dat_label,
    dat_handler,
    get_cookie_value,
    get_timing,
    networkselect_handler,
    numeric_handler,
    set_cookie,
)
from pyiem.exceptions import BadWebRequest
from werkzeug.test import Client


def get_test_urls():
    """yield a list of URLs to test."""
    listfn = Path(__file__).parent / "urllist_index.txt"
    with open(listfn) as fh:
        for line_in in fh:
            line = line_in.strip()
            if line == "" or line.startswith("#"):
                continue
            yield line


@pytest.mark.parametrize("url", list(get_test_urls()))
def test_urls(url):
    """Run the test."""
    c = Client(application)
    res = c.get(url)
    assert res.status_code == 200


def test_cookie_set_to_all():
    """Test handling of when cookie is set to _ALL."""
    cl = Client(application)
    cl.set_cookie("station_WFO", "_ALL")
    res = cl.get("?q=72")
    assert res.status_code == 200


def test_bad_network():
    """Test the provision of a bad network."""
    with pytest.raises(BadWebRequest):
        networkselect_handler("XXXX<script>", {"network": ""}, {"pltvars": []})


def test_cookie_values_are_encoded():
    """Cookie values cannot alter the Set-Cookie header."""
    headers = []
    set_cookie({}, headers, "state", "IA; Path=/")
    assert headers == [
        (
            "Set-Cookie",
            "state=IA%3B%20Path%3D%2F; Path=/plotting/auto/; Max-Age=8640000",
        )
    ]
    assert (
        get_cookie_value(
            {"type": "state", "name": "state"}, {"state": "IA%3B%20Path%3D%2F"}
        )
        == "IA; Path=/"
    )

    set_cookie({"state": "IA%3B%20Path%3D%2F"}, headers, "state", "IA; Path=/")
    assert len(headers) == 1


def test_plotvars_use_unescaped_scalar_values():
    """HTML escaping for the form does not alter plot variable values."""
    res = {"pltvars": []}
    add_to_plotvars(
        "A&amp;B &quot;quote&quot; &#x27;",
        {},
        {"type": "text", "name": "label"},
        res,
    )
    assert res["pltvars"] == ['label:A&B "quote" \'']


def test_multiple_plotvars_preserve_entity_text():
    """Multiple values bypass scalar form escaping."""
    res = {"pltvars": []}
    add_to_plotvars(["A&amp;B"], {}, {"type": "text", "name": "label"}, res)
    assert res["pltvars"] == ["label:A&amp;B"]


def test_plot_image_url_is_html_escaped():
    """Dynamic chart URLs are safe in HTML attributes."""
    res = {
        "imguri": '/plotting/auto/plot/1/label:A&B"quote',
        "image": "",
        "extrascripts": "",
        "headextra": "",
    }
    add_content_to_res("js", 1, res)
    assert (
        'src="/plotting/auto/plot/1/label:A&amp;B&quot;quote.js"'
        in res["extrascripts"]
    )


@pytest.mark.parametrize(
    ("global_id", "is_valid"),
    [
        ("{495DE596-B299-41FE-9C90-13C87E43FE0B}", True),
        ("{------------------------------------}", False),
        ("{495DE596B299-41FE-9C90-13C87E43FE0B}", False),
    ],
)
def test_dat_global_id_format(global_id, is_valid):
    """DAT IDs must use the canonical braced GUID format."""
    assert bool(DAT_GID_RE.fullmatch(global_id)) is is_valid


def test_dat_options_escape_api_fields(monkeypatch):
    """External DAT fields are escaped before HTML output."""
    attributes = {
        "globalid": '" onfocus="alert(1)',
        "wfo": "DMX",
        "efscale": "EF1",
        "event_id": "<script>alert(1)</script>",
        "starttime": 1761500000000,
        "length": 1.2,
    }

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"features": [{"attributes": attributes}]}

    class Session:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def get(self, *_args, **_kwargs):
            return Response()

    monkeypatch.setattr("iemweb.autoplot.index.requests.Session", Session)
    form = dat_handler({}, {"pltvars": []})

    assert "<script>alert(1)</script>" not in form
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in form
    assert "&quot; onfocus=&quot;alert(1)" in form


def test_dat_request_errors_are_reported_as_bad_requests(monkeypatch):
    """Expected external service failures become a client-facing error."""

    class Session:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def get(self, *_args, **_kwargs):
            raise requests.ConnectionError("connection failed")

    monkeypatch.setattr("iemweb.autoplot.index.requests.Session", Session)

    with pytest.raises(BadWebRequest, match="Unable to load DAT events"):
        dat_handler({}, {"pltvars": []})


def test_dat_handler_does_not_hide_programming_errors(monkeypatch):
    """Unexpected errors from the HTTP layer are not disguised."""

    class Session:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def get(self, *_args, **_kwargs):
            raise RuntimeError("unexpected failure")

    monkeypatch.setattr("iemweb.autoplot.index.requests.Session", Session)

    with pytest.raises(RuntimeError, match="unexpected failure"):
        dat_handler({}, {"pltvars": []})


@pytest.mark.parametrize(
    ("length", "starttime"),
    [
        ("nan", 1761500000000),
        ("inf", 1761500000000),
        (1, "nan"),
        (1, "inf"),
        (1, 10**1000),
    ],
)
def test_dat_label_handles_non_finite_attributes(length, starttime):
    """Invalid API measurements use safe fallback text in DAT labels."""
    label = compute_dat_label(
        {
            "event_id": "1",
            "wfo": "DMX",
            "efscale": "EF1",
            "length": length,
            "starttime": starttime,
        }
    )
    if length in ("nan", "inf"):
        assert label.endswith("0 miles")
    if starttime in ("nan", "inf") or (
        isinstance(starttime, int) and starttime > 10**20
    ):
        assert "????Z" in label


def test_get_timing_closes_connection_on_failure(monkeypatch):
    """The timing database connection closes even if fetching fails."""

    class Connection:
        closed = False

        def close(self):
            self.closed = True

    class Cursor:
        def execute(self, *_args):
            pass

        def fetchone(self):
            raise RuntimeError("fetch failed")

    connection = Connection()
    cursor = Cursor()
    monkeypatch.setattr(
        "iemweb.autoplot.index.get_dbconnc",
        lambda _database, **_kwargs: (connection, cursor),
    )

    with pytest.raises(RuntimeError):
        get_timing(1)
    assert connection.closed


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("nan", "0"),
        ("inf", "0"),
        ("-inf", "0"),
        ("not-a-number", "0"),
        ("", "0"),
        ("5", "5"),
    ],
)
def test_numeric_handler_uses_finite_default(value, expected):
    """Invalid and non-finite values fall back to the configured default."""
    result = numeric_handler(value, {"name": "value", "default": "0"})[0]
    assert result == expected


def test_numeric_handler_allows_empty_default():
    """An empty default remains usable after an invalid numeric value."""
    assert (
        numeric_handler("not-a-number", {"name": "value", "default": ""})[0]
        == ""
    )


def test_numeric_handler_rejects_non_finite_default():
    """A broken non-finite default is surfaced instead of returned."""
    with pytest.raises(ValueError, match="Numeric default"):
        numeric_handler("nan", {"name": "value", "default": "inf"})
