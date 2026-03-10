"""Dispatch /json requests."""

import re
from importlib import import_module
from urllib.parse import parse_qsl, urlencode

from iemweb import error_log

SPECIAL_ROUTES = [
    (
        re.compile(r"^/raob/(?P<ts>[0-9]{12})/(?P<station>[A-Z0-9]{3,4})$"),
        "raob",
        lambda match, environ: add_query(
            environ, ts=match.group("ts"), station=match.group("station")
        ),
    ),
    (
        re.compile(
            r"^/stage4/(?P<lon>[-+]?([0-9]*[\.])?[0-9]+)/"
            r"(?P<lat>[-+]?([0-9]*[\.])?[0-9]+)/(?P<date>[0-9\-]+)$"
        ),
        "stage4",
        lambda match, environ: add_query(
            environ,
            lon=match.group("lon"),
            lat=match.group("lat"),
            valid=match.group("date"),
        ),
    ),
]

REDIRECTS = {
    "/network_obs.php": "/api/1/currents.geojson",
}


def add_query(environ: dict, **params) -> None:
    """Add content into environ, before passing it along."""
    current = dict(
        parse_qsl(environ.get("QUERY_STRING", ""), keep_blank_values=True)
    )
    current.update(params)
    environ["QUERY_STRING"] = urlencode(current)


def not_found(
    environ: dict, start_response: callable, what: str
) -> list[bytes]:
    """Redirect to the docs..."""
    error_log(environ, f"json failed {what}")
    start_response("301 Found", [("Location", "/api/")])
    return []


def normalize_path(path: str) -> str | None:
    """Clean the path attempting to figure out what to import."""
    if not path:
        return None

    value = path.lstrip("/")
    for suffix in (".json", ".php", ".py"):
        if value.endswith(suffix):
            value = value[: -len(suffix)]
            break

    if not re.fullmatch(r"[a-z_0-9]+", value):
        return None
    return value


def application(environ: dict, start_response: callable):
    """WSGI application entry point."""
    path: str = environ.get("PATH_INFO", "")
    if path.startswith("/index"):
        return not_found(environ, start_response, path)

    for regex, module_name, transform in SPECIAL_ROUTES:
        match = regex.match(path)
        if match:
            if transform is not None:
                transform(match, environ)
            # Assume daryl did not misconfigure the special route above :/
            handler = import_module(f"iemweb.json.{module_name}")
            return handler.application(environ, start_response)

    if path in REDIRECTS:
        start_response(
            "302 Found",
            [
                (
                    "Location",
                    f"{REDIRECTS[path]}?{environ.get('QUERY_STRING', '')}",
                )
            ],
        )
        return []

    endpoint = normalize_path(path)
    if endpoint is None:
        return not_found(environ, start_response, path)

    try:
        handler = import_module(f"iemweb.json.{endpoint}")
    except ModuleNotFoundError:
        return not_found(environ, start_response, path)

    return handler.application(environ, start_response)
