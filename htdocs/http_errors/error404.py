"""Our custom 404 handler."""
import sys

from pyiem.util import get_dbconn
from pyiem.templates.iem import TEMPLATE


def log_request(uri, environ):
    """Do some logging work."""
    sys.stderr.write(
        f"IEM 404 {uri} remote: {environ.get('REMOTE_ADDR')} "
        f"referer: {environ.get('HTTP_REFERER')}\n"
    )
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute(
        """
        INSERT into weblog(client_addr, uri, referer, http_status)
        VALUES (%s, %s, %s, %s)
    """,
        (
            environ.get("REMOTE_ADDR"),
            uri,
            environ.get("HTTP_REFERER"),
            404,
        ),
    )
    cursor.close()
    pgconn.commit()


def application(environ, start_response):
    """mod-wsgi handler."""
    uri = environ.get("REQUEST_URI", "")
    # Special handling of ancient broken windrose behaviour
    if uri.startswith("/onsite/windrose/climate"):
        start_response("410 Gone", [("Content-type", "text/plain")])
        return [b"Resource is no longer available."]

    # We should re-assert the HTTP status code that brought us here :/
    start_response("404 Not Found", [("Content-type", "text/html")])
    content = """
<h3>Requested file was not found</h3>
<img src="/images/cow404.jpg" class="img img-responsive" alt="404 Cow" />
    """
    ctx = {"title": "File Not Found (404)", "content": content}
    try:
        log_request(uri, environ)
    except Exception as exp:
        sys.stderr.write(str(exp) + "\n")

    return [TEMPLATE.render(ctx).encode("utf-8")]
