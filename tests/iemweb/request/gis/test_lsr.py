"""test cgi-bin/request/gis/lsr.py"""

from iemweb.request.gis.lsr import application


def test_csv_empty(wsgi_client):
    """Test that we get back an empty CSV result."""
    c = wsgi_client(application)
    res = c.get("?sts=2024-07-18T11:58:00Z&ets=2024-07-18T11:59:00Z&fmt=csv")
    assert res.status_code == 200
    assert res.get_data(as_text=True).find("REMARK") > 0
