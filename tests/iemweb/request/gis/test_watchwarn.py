"""test cgi-bin/request/gis/watchwarn.py"""

import xml.etree.ElementTree as ET

from iemweb.request.gis.watchwarn import application
from werkzeug.test import Client


def test_valid_kml():
    """Test that we get back an empty CSV result."""
    c = Client(application)
    res = c.get(
        "?accept=kml&at=2024-05-21T21:20Z&timeopt=2&limitps=1"
        "&phenomena=TO&significance=W"
    )
    assert res.status_code == 200
    doc = ET.fromstring(res.data)
    assert doc.tag == "{http://www.opengis.net/kml/2.2}kml"
