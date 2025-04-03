"""IEM Website Python Library."""

__version__ = "0.1.0"


def error_log(environ: dict, msg: str) -> None:
    """Properly send an error log message.

    Args:
      environ (dict): The mod_wsgi environment
      msg (str): The message to log
    """
    # For whatever reason, when this error message is logged, Apache does not
    # have the headers to include with the message, so we need to include them
    # ourselves.
    client_addr = environ.get(
        "HTTP_X_FORWARDED_FOR", environ.get("REMOTE_ADDR")
    )
    print(f"client: `{client_addr}` `{msg}`", file=environ["wsgi.errors"])
