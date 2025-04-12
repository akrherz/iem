"""Archive the NWS WaWA map.

https://mesonet.agron.iastate.edu/timemachine/?product=59.0
"""

import os
import subprocess
import tempfile

import httpx
from pyiem.util import exponential_backoff, logger, utc

LOG = logger()
SRC = "https://forecast.weather.gov/wwamap/png/US.png"


def main():
    """Go Main Go."""
    utcnow = utc()
    resp = exponential_backoff(httpx.get, SRC, timeout=15)
    if resp is None:
        LOG.info("Failed to fetch %s", SRC)
        return
    if resp.status_code != 200 or len(resp.content) == 0:
        LOG.info(
            "Fail %s status_code: %s len(content): %s",
            SRC,
            resp.status_code,
            len(resp.content),
        )
        return
    tmpfd = tempfile.NamedTemporaryFile(delete=False)
    with open(tmpfd.name, "wb") as fh:
        fh.write(resp.content)
    dstamp = utcnow.strftime("%Y%m%d%H%M")
    pqstr = f"plot a {dstamp} bogus wwa/wwa_{dstamp}.png png"
    LOG.info(pqstr)
    subprocess.call(["pqinsert", "-i", "-p", pqstr, tmpfd.name])
    os.unlink(tmpfd.name)


if __name__ == "__main__":
    main()
