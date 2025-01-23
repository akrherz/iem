"""
Generate some sequential load to watch what happens to IEM's backend processing
"""

import random
from datetime import datetime, timedelta

import httpx


def main():
    """Do stressfull things"""
    sts = datetime(2012, 1, 23)
    ets = datetime(2012, 1, 24)
    interval = timedelta(minutes=5)
    now = sts

    cnt = 0
    start = datetime.now()
    istart = start
    while now < ets:
        for _ in range(1000):
            uri = now.strftime(
                "http://iem.local/c/tile.py/1.0.0/ridge::USCOMP-N0R-"
                "%Y%m%d%H%M/"
                + str(random.randint(0, 10))
                + "/"
                + str(random.randint(0, 10))
                + "/"
                + str(random.randint(0, 10))
                + ".png"
            )
            httpx.get(uri, timeout=5)
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

        now += interval


if __name__ == "__main__":
    main()
