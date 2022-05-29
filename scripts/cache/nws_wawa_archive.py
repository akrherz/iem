"""Archive the NWS WaWA map.

https://mesonet.agron.iastate.edu/timemachine/#59.0
"""
import subprocess
import tempfile
import os

from pyiem.util import exponential_backoff, logger, utc
import requests

LOG = logger()
SRC = "https://forecast.weather.gov/wwamap/png/US.png"


def main():
    """Go Main Go."""
    utcnow = utc()
    req = exponential_backoff(requests.get, SRC, timeout=15)
    if req is None:
        LOG.info("Failed to fetch %s", SRC)
        return
    if req.status_code != 200 or len(req.content) == 0:
        LOG.info(
            "Fail %s status_code: %s len(content): %s",
            SRC,
            req.status_code,
            len(req.content),
        )
        return
    tmpfd = tempfile.NamedTemporaryFile(delete=False)
    with open(tmpfd.name, "wb") as fh:
        fh.write(req.content)
    dstamp = utcnow.strftime("%Y%m%d%H%M")
    pqstr = f"plot a {dstamp} bogus wwa/wwa_{dstamp}.png png"
    LOG.info(pqstr)
    subprocess.call(f"pqinsert -i -p '{pqstr}' {tmpfd.name}", shell=True)
    os.unlink(tmpfd.name)


if __name__ == "__main__":
    main()
