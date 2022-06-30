"""Farm Progress Show App."""
# stdlib

# third party
from paste.request import parse_formvars


def generate(_fdict, _headers):
    """Return a dict of things for the template engine."""
    return """
    <html>
    <head>
        <link rel="stylesheet" type="text/css" href="fps.css"/ >
    </head>
    <body>
    <h3>Hello World.</h3>
    </body>
    </html>
    """


def application(environ, start_response):
    """mod-wsgi handler."""
    fdict = parse_formvars(environ)
    headers = [("Content-type", "text/html")]
    html = generate(fdict, headers)
    start_response("200 OK", headers)
    return [html.encode("utf-8")]
