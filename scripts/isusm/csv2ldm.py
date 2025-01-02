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
    req = httpx.get(uri, timeout=30)
    content = req.content
    # Ensure we get back a decent response
    if content.find(b".EOO") < 0:
        LOG.info("%s failed to produce valid CSV", uri)
        return
    with tempfile.NamedTemporaryFile(delete=False) as tmpfd:
        tmpfd.write(req.content)
    subprocess.call(["pqinsert", "-p", "isusm.csv", tmpfd.name])
    os.unlink(tmpfd.name)


if __name__ == "__main__":
    main()
