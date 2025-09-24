"""Test things with iemweb.onsite.features"""

from iemweb.onsite.features.content import application as content_app
from iemweb.onsite.features.vote import application as vote_app
from werkzeug.test import Client


def test_invalid_request():
    """Test request without a URL set."""
    client = Client(content_app, response_wrapper=None)
    response = client.get("")
    assert response.status_code == 422
    assert "Missing parameters" in response.text


def test_content_nofile():
    """Test the generated image placeholder."""
    client = Client(content_app, response_wrapper=None)
    response = client.get("/onsite/features/2000/03/220325.png")
    assert response.status_code == 404


def test_content_hasfile():
    """Test the image returned."""
    client = Client(content_app, response_wrapper=None)
    response = client.get("/onsite/features/2022/03/220325.png")
    assert response.status_code == 200


def test_http_range_bytes_request():
    """Test the image returned."""
    client = Client(content_app, response_wrapper=None)
    response = client.get(
        "/onsite/features/2022/03/220325.png",
        headers={"Range": "bytes=0-100"},
    )
    assert response.status_code == 206
    assert response.headers["Content-Range"] == "bytes 0-100/59811"
    assert response.headers["Content-Length"] == "101"


def test_vote():
    """Test that we can vote."""
    client = Client(vote_app, response_wrapper=None)
    response = client.get("/onsite/features/vote.py?vote=good")
    assert response.status_code == 200


def test_novote():
    """Test when we don't vote at all."""
    client = Client(vote_app, response_wrapper=None)
    response = client.get("/onsite/features/vote.py")
    assert response.status_code == 200
