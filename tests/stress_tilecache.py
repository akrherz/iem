"""
Generate some sequential load to watch what happens to IEM's backend processing
"""

import random
import sys
from datetime import datetime

import requests


def main():
    """Do stressfull things"""
    now = datetime(2012, 1, 23)
    cnt = 0
    start = datetime.now()
    istart = start
    for _ in range(10000):
        uri = now.strftime(
            "http://iem.local/cache/tile.py/1.0.0/ridge::USCOMP-N0R-"
            "%Y%m%d%H%M/"
            + str(random.randint(0, 10))
            + "/"
            + str(random.randint(0, 10))
            + "/"
            + str(random.randint(0, 10))
            + ".png"
        )
        resp = requests.get(uri, timeout=5)
        if resp.status_code != 200:
            print(f"Bad response code {resp.status_code} for {uri}")
            sys.exit(1)
        cnt += 1
        if cnt % 100 == 0:
            delta = datetime.now() - start
            delta2 = datetime.now() - istart
            print(
                ("%6i %9.5f req/s %9.5f req/s")
                % (
                    cnt,
                    100.0 / delta2.total_seconds(),
                    (float(cnt) / delta.total_seconds()),
                )
            )
            istart = datetime.now()


if __name__ == "__main__":
    main()
