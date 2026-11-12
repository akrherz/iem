"""test iemweb.json.spcoutlook"""

from iemweb.json.spcoutlook import application


def test_simple(wsgi_client):
    """Test something simple"""
    c = wsgi_client(application)
    for fmt in ["csv", "excel", "json"]:
        res = c.get(data={"fmt": fmt})
        assert res.status_code == 200
