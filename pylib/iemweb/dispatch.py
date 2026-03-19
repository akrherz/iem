"""Shared dispatch logic for /json and /geojson endpoints."""

import re
from importlib import import_module
from urllib.parse import parse_qsl, urlencode

from iemweb import error_log

SPECIAL_ROUTES = {
    "json": [
        (
            re.compile(
                r"^/raob/(?P<ts>[0-9]{12})/(?P<station>[A-Z0-9]{3,4})$"
            ),
            "raob",
            lambda match, environ: add_query(
                environ,
                ts=match.group("ts"),
                station=match.group("station"),
            ),
        ),
        (
            re.compile(
                r"^/stage4/(?P<lon>[-+]?([0-9]*[\.])?[0-9]+)/"
                r"(?P<lat>[-+]?([0-9]*[\.])?[0-9]+)/"
                r"(?P<date>[0-9\-]+)$"
            ),
            "stage4",
            lambda match, environ: add_query(
                environ,
                lon=match.group("lon"),
                lat=match.group("lat"),
                valid=match.group("date"),
            ),
        ),
    ],
    "geojson": [
        (
            re.compile(r"^/7am"),
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
    ],
}

REDIRECTS = {
    "/network_obs.php": "/api/1/currents.geojson",
}

SUFFIXES = {
    "json": (".json", ".php", ".py"),
    "geojson": (".geojson", ".php", ".py"),
}

MODULE_PREFIXES = {
    "json": "iemweb.json",
    "geojson": "iemweb.geojson",
}

# Single-endpoint modules served directly without sub-path routing.
DIRECT_ROUTES = {
    "search": "iemweb.search",
    "agclimate/ames_precip.py": "iemweb.agclimate.ames_precip",
    "agclimate/isusm.py": "iemweb.agclimate.isusm",
    "agclimate/nmp_csv.py": "iemweb.agclimate.nmp_csv",
}


def add_query(environ: dict, **params) -> None:
    """Add content into environ before passing it along."""
    current = dict(
        parse_qsl(environ.get("QUERY_STRING", ""), keep_blank_values=True)
    )
    current.update(params)
    environ["QUERY_STRING"] = urlencode(current)


def not_found(
    environ: dict, start_response: callable, namespace: str, what: str
) -> list[bytes]:
    """Redirect missing content to the API docs page."""
    error_log(environ, f"{namespace} failed {what}")
    start_response("301 Found", [("Location", "/api/")])
    return []


def normalize_path(path: str, suffixes: tuple[str, ...]) -> str | None:
    """Clean the path attempting to figure out what to import."""
    if not path:
        return None

    value = path.lstrip("/")
    for suffix in suffixes:
        if value.endswith(suffix):
            value = value[: -len(suffix)]
            break

    if not re.fullmatch(r"[a-z_0-9]+", value):
        return None
    return value


def detect_namespace(environ: dict) -> str | None:
    """Determine which namespace or direct route should handle this request."""
    all_routes = {**MODULE_PREFIXES, **DIRECT_ROUTES}
    script_name: str = environ.get("SCRIPT_NAME", "")
    for key in all_routes:
        prefix = f"/{key}"
        if script_name == prefix or script_name.endswith(prefix):
            return key

    path: str = environ.get("PATH_INFO", "")
    for key in all_routes:
        prefix = f"/{key}"
        if path == prefix:
            environ["PATH_INFO"] = ""
            return key
        if path.startswith(f"{prefix}/"):
            environ["PATH_INFO"] = path[len(prefix) :]
            return key
    return None


def dispatch_namespace(
    namespace: str, environ: dict, start_response: callable
):
    """Dispatch a request for one namespace."""
    path: str = environ.get("PATH_INFO", "")
    if path.startswith("/index"):
        return not_found(environ, start_response, namespace, path)

    for regex, module_name, transform in SPECIAL_ROUTES[namespace]:
        match = regex.match(path)
        if match:
            if transform is not None:
                transform(match, environ)
            handler = import_module(
                f"{MODULE_PREFIXES[namespace]}.{module_name}"
            )
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

    endpoint = normalize_path(path, SUFFIXES[namespace])
    if endpoint is None:
        return not_found(environ, start_response, namespace, path)

    try:
        handler = import_module(f"{MODULE_PREFIXES[namespace]}.{endpoint}")
    except ModuleNotFoundError:
        return not_found(environ, start_response, namespace, path)

    return handler.application(environ, start_response)


def application(environ: dict, start_response: callable):
    """WSGI entry point for the consolidated dispatcher."""
    namespace = detect_namespace(environ)
    if namespace is None:
        return not_found(
            environ,
            start_response,
            "dispatch",
            environ.get("PATH_INFO", ""),
        )
    if namespace in DIRECT_ROUTES:
        handler = import_module(DIRECT_ROUTES[namespace])
        return handler.application(environ, start_response)
    return dispatch_namespace(namespace, environ, start_response)
