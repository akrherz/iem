"""Test things with iemweb.onsite.features"""

from iemweb.onsite.features.content import application as content_app
from iemweb.onsite.features.vote import application as vote_app


def test_invalid_request(wsgi_client):
    """Test request without a URL set."""
    client = wsgi_client(content_app)
    response = client.get("")
    assert response.status_code == 422
    assert "Missing parameters" in response.text


def test_content_nofile(wsgi_client):
    """Test the generated image placeholder."""
    client = wsgi_client(content_app)
    response = client.get("/onsite/features/2000/03/220325.png")
    assert response.status_code == 404


def test_content_hasfile(wsgi_client):
    """Test the image returned."""
    client = wsgi_client(content_app)
    response = client.get("/onsite/features/2022/03/220325.png")
    assert response.status_code == 200


def test_http_range_bytes_request(wsgi_client):
    """Test the image returned."""
    client = wsgi_client(content_app)
    response = client.get(
        "/onsite/features/2022/03/220325.png",
        headers={"Range": "bytes=0-100"},
    )
    assert response.status_code == 206
    assert response.headers["Content-Range"] == "bytes 0-100/59811"
    assert response.headers["Content-Length"] == "101"


def test_vote(wsgi_client):
    """Test that we can vote."""
    client = wsgi_client(vote_app)
    response = client.get("/onsite/features/vote.py?vote=good")
    assert response.status_code == 200


def test_novote(wsgi_client):
    """Test when we don't vote at all."""
    client = wsgi_client(vote_app)
    response = client.get("/onsite/features/vote.py")
    assert response.status_code == 200
