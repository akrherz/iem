"""test iemweb.json.spcoutlook"""

from iemweb.json.spcoutlook import application
from werkzeug.test import Client


def test_simple():
    """Test something simple"""
    c = Client(application)
    for fmt in ["csv", "excel", "json"]:
        res = c.get(data={"fmt": fmt})
        assert res.status_code == 200
