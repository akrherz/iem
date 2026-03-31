"""Minimal dispatcher for TileCache endpoints /c and /cache.

These are thread-safe and served by a dedicated Gunicorn backend for maximum
tile throughput.
"""

from iemweb.c.tile import application as c_application
from iemweb.cache.tile import application as cache_application

# Keys are the full SCRIPT_NAME that Apache would normally set, i.e. the path
# up to and including the .py script.  The dispatcher strips this prefix from
# PATH_INFO and sets SCRIPT_NAME so TileCache's wsgiHandler sees the same
# environ layout it gets when served directly by the main Apache.
_ROUTES = {
    "/c/tile.py": c_application,
    "/c/c.py": c_application,
    "/cache/tile.py": cache_application,
}


def application(environ: dict, start_response: callable):
    """WSGI entry point for TileCache requests.

    Injects `Cache-Control` and `Expires` headers for the `/c` and
    `/cache` endpoints so Apache-level Expires configuration is mirrored
    when served from the sidecar.
    """
    import time
    from wsgiref.handlers import format_date_time

    path_info: str = environ.get("PATH_INFO", "")
    for script_name, handler in _ROUTES.items():
        if path_info == script_name or path_info.startswith(f"{script_name}/"):
            environ["SCRIPT_NAME"] = script_name
            environ["PATH_INFO"] = path_info[len(script_name) :]

            # Determine cache TTL based on the script namespace
            ttl = 5 * 60  # 5 minutes
            if (
                script_name.startswith("/c/")
                or script_name == "/c/tile.py"
                or script_name == "/c/c.py"
            ):
                ttl = 14 * 24 * 60 * 60  # 14 days

            def header_wrapper(status, headers, exc_info=None, _ttl=ttl):
                # Capture ttl in a default argument to avoid late-binding
                # loop-variable issues flagged by linters.
                hdr_names = {k.lower() for k, _ in headers}
                if "cache-control" not in hdr_names:
                    headers.append(
                        ("Cache-Control", f"public, max-age={_ttl}")
                    )
                if "expires" not in hdr_names:
                    expires = format_date_time(time.time() + _ttl)
                    headers.append(("Expires", expires))
                return start_response(status, headers, exc_info)

            return handler(environ, header_wrapper)

    # We will do something better, someday...
    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b"OK\n"]
