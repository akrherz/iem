"""IEM Website Python Library."""

import socket

from pyiem.util import LOG

__version__ = "0.1.0"
# Established via akrherz/infra-ansible as a side-door socket to avoid
# the systemd managed /bin/logger , which pollutes the journal/httpd logs
RSYSLOG_SIDEDOOR_SOCKET = "/run/rsyslog/iemweb.sock"


def emit_to_sidedoor(payload: bytes) -> None:
    """Send the given payload to the rsyslog sidedoor."""
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as sock:
            sock.setblocking(False)
            sock.sendto(payload, RSYSLOG_SIDEDOOR_SOCKET)
    except OSError:
        LOG.exception("Failed to send telemetry payload")


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
    # 141 is local1.notice
    payload = (f"<141>iemwebErrorLog client: `{client_addr}` `{msg}`").encode()
    emit_to_sidedoor(payload)
