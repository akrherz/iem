"""test cgi-bin/request/gis/lsr.py"""

from iemweb.request.gis.lsr import application
from werkzeug.test import Client


def test_csv_empty():
    """Test that we get back an empty CSV result."""
    c = Client(application)
    res = c.get("?sts=2024-07-18T11:58:00Z&ets=2024-07-18T11:59:00Z&fmt=csv")
    assert res.status_code == 200
    assert res.get_data(as_text=True).find("REMARK") > 0
