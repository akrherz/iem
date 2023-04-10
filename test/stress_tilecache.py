"""
Generate some sequential load to watch what happens to IEM's backend processing
"""
import datetime
import random

import requests


def main():
    """Do stressfull things"""
    sts = datetime.datetime(2012, 1, 23)
    ets = datetime.datetime(2012, 1, 24)
    interval = datetime.timedelta(minutes=5)
    now = sts

    cnt = 0
    start = datetime.datetime.now()
    istart = start
    while now < ets:
        for _ in range(1000):
            uri = now.strftime(
                (
                    "http://iem.local/"
                    "c/tile.py/1.0.0/ridge::USCOMP-N0R-"
                    "%Y%m%d%H%M/"
                    + str(random.randint(0, 10))
                    + "/"
                    + str(random.randint(0, 10))
                    + "/"
                    + str(random.randint(0, 10))
                    + ".png"
                )
            )
            requests.get(uri, timeout=5)
            cnt += 1
            if cnt % 100 == 0:
                delta = datetime.datetime.now() - start
                delta2 = datetime.datetime.now() - istart
                print(
                    ("%6i %9.5f req/s %9.5f req/s")
                    % (
                        cnt,
                        100.0 / delta2.total_seconds(),
                        (float(cnt) / delta.total_seconds()),
                    )
                )
                istart = datetime.datetime.now()

        now += interval


if __name__ == "__main__":
    main()
