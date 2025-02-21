"""Dump the MADIS CSV file to LDM.

Run from RUN_5MIN.sh
"""

import os
import subprocess
import tempfile

import httpx
from pyiem.util import logger

LOG = logger()


def main():
    """Go Main Go."""
    uri = "http://iem.local/agclimate/isusm.csv"
    try:
        resp = httpx.get(uri, timeout=30)
        resp.raise_for_status()
        content = resp.content
    except Exception as exp:
        LOG.warning("Failed to fetch %s: %s", uri, exp)
        return
    # Ensure we get back a decent response
    if content.find(b".EOO") < 0:
        LOG.warning("%s failed to produce valid CSV", uri)
        return
    with tempfile.NamedTemporaryFile(delete=False) as tmpfd:
        tmpfd.write(content)
    subprocess.call(["pqinsert", "-p", "isusm.csv", tmpfd.name])
    os.unlink(tmpfd.name)


if __name__ == "__main__":
    main()
