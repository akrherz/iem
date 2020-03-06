"""Our custom 404 handler."""
import sys

from pyiem.util import get_dbconn
from pyiem.templates.iem import TEMPLATE


def log_request(environ):
    """Do some logging work."""
    sys.stderr.write(
        "IEM 404 %s remote: %s referer: %s\n"
        % (
            environ.get("REQUEST_URI"),
            environ.get("REMOTE_ADDR"),
            environ.get("HTTP_REFERER"),
        )
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
            environ.get("REQUEST_URI"),
            environ.get("HTTP_REFERER"),
            404,
        ),
    )
    cursor.close()
    pgconn.commit()


def application(environ, start_response):
    """mod-wsgi handler."""
    start_response("200 OK", [("Content-type", "text/html")])
    content = """
<h3>Requested file was not found</h3>
<img src="/images/cow404.jpg" class="img img-responsive" alt="404 Cow" />
    """
    ctx = {"title": "File Not Found (404)", "content": content}
    try:
        log_request(environ)
    except Exception as exp:
        sys.stderr.write(str(exp) + "\n")

    return [TEMPLATE.render(ctx).encode("utf-8")]
