"""Dispatch /geojson requests."""

import re
from importlib import import_module
from urllib.parse import parse_qsl, urlencode

SPECIAL_ROUTES = [
    (
        re.compile(r"^7am"),
        "seven_am",
        None,
    ),
    (
        re.compile(r"^/network/(?P<network>[^/]+)\.geojson$"),
        "network",
        lambda match, environ: add_query(
            environ, network=match.group("network")
        ),
    ),
    (
        re.compile(r"^/nexrad_attr\.csv$"),
        "nexrad_attr",
        lambda _match, environ: add_query(environ, fmt="csv"),
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


def not_found(start_response: callable) -> list[bytes]:
    """Redirect to the docs..."""
    start_response("301 Found", [("Location", "/api/")])
    return []


def normalize_path(path: str) -> str | None:
    """Clean the path attempting to figure out what to import."""
    if not path:
        return None

    value = path.lstrip("/")
    for suffix in (".geojson", ".php", ".py"):
        if value.endswith(suffix):
            value = value[: -len(suffix)]
            break

    if not re.fullmatch(r"[a-z_]+", value):
        return None
    return value


def application(environ: dict, start_response: callable):
    """WSGI application entry point."""
    path = environ.get("PATH_INFO", "")

    for regex, module_name, transform in SPECIAL_ROUTES:
        match = regex.match(path)
        if match:
            if transform is not None:
                transform(match, environ)
            # Assume daryl did not misconfigure the special route above :/
            handler = import_module(f"iemweb.geojson.{module_name}")
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
        return not_found(start_response)

    try:
        handler = import_module(f"iemweb.geojson.{endpoint}")
    except ModuleNotFoundError:
        return not_found(start_response)

    return handler.application(environ, start_response)
