"""Test the current/live.py service."""

from io import BytesIO

import responses
from iemweb.current import live
from PIL import Image
from werkzeug.test import Client


def test_offline():
    """Test for a webcam that is offline."""
    client = Client(live.application)
    response = client.get("/current/live.py?id=KCRG-002")
    assert response.status_code == 200


@responses.activate
def test_workflow():
    """Test we can fetch an image."""
    image = Image.new("RGB", (320, 240), (73, 109, 137))
    buf = BytesIO()
    image.save(buf, format="JPEG")
    image_bytes = buf.getvalue()
    responses.add(
        responses.GET,
        "http://example.com",
        body=image_bytes,
        status=200,
    )
    client = Client(live.application)
    response = client.get("/current/live.py?id=KCRG-032")  # is_vapix
    assert response.status_code == 200


@responses.activate
def test_badauth():
    """Test that we handle bad auth."""
    responses.add(
        responses.GET,
        "http://example.com",
        status=401,
    )
    client = Client(live.application)
    response = client.get("/current/live.py?id=KCRG-003")
    assert response.status_code == 200


def test_live_webcam_image():
    client = Client(live.application)
    response = client.get("/current/live.py?id=KCCI-099")
    assert response.status_code == 200
    assert response.content_type == "image/jpeg"
