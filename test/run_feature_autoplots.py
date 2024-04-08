"""Attempt to rerun all feature plots to see what I broke."""

import datetime
import sys
from multiprocessing import Pool

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pyiem.database import get_dbconn
from pyiem.util import logger

LOG = logger()


def run_plot(uri):
    """Run this plot"""
    uri = f"http://iem.local/{uri}"
    try:
        res = requests.get(uri, timeout=600)
        soup = BeautifulSoup(res.content, "html.parser")
        img = soup.find_all(id="theimage")
        if not img:
            return True
        uri = "http://iem.local{}".format(img[0]["src"])
        res = requests.get(uri, timeout=600)
    except requests.exceptions.ReadTimeout:
        print(f"{uri[16:]} -> Read Timeout")
        return False
    # Known failures likely due to missing data
    if res.status_code == 400:
        return True
    if res.status_code == 504:
        print(f"{uri} -> HTTP: {res.status_code} (timeout)")
        return False
    if res.status_code != 200 or res.content == "":
        print(
            f"{uri[16:]} -> HTTP: {res.status_code} "
            "len(content): {len(res.content)}"
        )

        return False

    return True


def workflow(entry):
    """Run our queued entry of id and format"""
    sts = datetime.datetime.now()
    res = run_plot(entry[1])
    if res is False:
        return [entry[0], entry[1], False]
    ets = datetime.datetime.now()
    return [entry[0], entry[1], (ets - sts).total_seconds()]


def main():
    """Do Something"""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute(
        """
        SELECT date(valid), appurl from feature
        WHERE appurl ~* '/plotting/auto/'
        ORDER by valid ASC
    """
    )
    queue = [row for row in cursor]
    LOG.info("found %s features", len(queue))
    timing = []
    failed = []
    pool = Pool(4)
    for res in pool.imap_unordered(workflow, queue):
        if res[2] is False:
            failed.append({"i": res[0], "fmt": res[1]})
            continue
        timing.append({"i": res[0], "fmt": res[1], "secs": res[2]})
    if not timing:
        print("WARNING: no timing results found!")
        return
    df = (
        pd.DataFrame(timing)
        .set_index("i")
        .sort_values("secs", ascending=False)
    )
    print(df.head(5))
    if failed:
        print("Failures:")
        for f in failed:
            print("{} {}".format(f["i"], f["fmt"]))
        sys.exit(1)


if __name__ == "__main__":
    main()
