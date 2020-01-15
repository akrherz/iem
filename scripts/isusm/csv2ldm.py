"""Dump the MADIS CSV file to LDM.

Run from RUN_5MIN.sh
"""
import tempfile
import os
import subprocess

import requests
from pyiem.util import logger

LOG = logger()


def main():
    """Go Main Go."""
    uri = "http://iem.local/agclimate/isusm.csv"
    req = requests.get(uri, timeout=30)
    content = req.content
    # Ensure we get back a decent response
    if content.find(b".EOO") < 0:
        LOG.info("%s failed to produce valid CSV", uri)
        return
    tmpfd = tempfile.NamedTemporaryFile(delete=False)
    tmpfd.write(req.content)
    tmpfd.close()
    subprocess.call("pqinsert -p 'isusm.csv' %s" % (tmpfd.name,), shell=True)
    os.unlink(tmpfd.name)


if __name__ == "__main__":
    main()
