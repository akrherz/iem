"""Attempt to rerun all feature plots to see what I broke."""
import datetime
import sys
from multiprocessing import Pool

from bs4 import BeautifulSoup
import requests
import pandas as pd
from pyiem.util import get_dbconn, logger

LOG = logger()


def run_plot(uri):
    """Run this plot"""
    uri = "http://iem.local/%s" % (uri,)
    try:
        res = requests.get(uri, timeout=600)
        soup = BeautifulSoup(res.content, "html.parser")
        img = soup.find_all(id="theimage")
        if not img:
            return True
        uri = "http://iem.local%s" % (img[0]["src"],)
        res = requests.get(uri, timeout=600)
    except requests.exceptions.ReadTimeout:
        print("%s -> Read Timeout" % (uri[16:],))
        return False
    # Known failures likely due to missing data
    if res.status_code == 400:
        return True
    if res.status_code == 504:
        print("%s -> HTTP: %s (timeout)" % (uri, res.status_code))
        return False
    if res.status_code != 200 or res.content == "":
        print(
            "%s -> HTTP: %s len(content): %s"
            % (uri[16:], res.status_code, len(res.content))
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
    queue = []
    for row in cursor:
        queue.append(row)
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
    df = pd.DataFrame(timing)
    df.set_index("i", inplace=True)
    df.sort_values("secs", ascending=False, inplace=True)
    print(df.head(5))
    if failed:
        print("Failures:")
        for f in failed:
            print("%s %s" % (f["i"], f["fmt"]))
        sys.exit(1)


if __name__ == "__main__":
    main()
