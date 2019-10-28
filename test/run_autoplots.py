"""Attempt to call each autoplot and whine about API calls that error"""
from __future__ import print_function
import datetime
import sys
from multiprocessing import Pool

import requests
import pandas as pd


def get_formats(i):
    """Figure out which formats this script supports"""
    uri = "http://iem.local/plotting/auto/meta/%s.json" % (i,)
    try:
        res = requests.get(uri, timeout=10)
    except requests.exceptions.ReadTimeout:
        print("%s. %s -> Read Timeout" % (i, uri[16:]))
    if res.status_code == 404:
        print("scanning metadata got 404 at i=%s, proceeding" % (i,))
        return False
    if res.status_code != 200:
        print("%s. %s -> HTTP: %s" % (i, uri, res.status_code))
        print(res.text)
    try:
        json = res.json()
    except Exception as exp:
        print("%s %s -> json failed\n%s" % (i, res.content, exp))
        return
    fmts = ["png"]
    if "report" in json and json["report"]:
        fmts.append("txt")
    if "highcharts" in json and json["highcharts"]:
        fmts.append("js")
    if json.get("data", False):
        fmts.append("csv")
        fmts.append("xlsx")
    return fmts


def run_plot(i, fmt):
    """Run this plot"""
    uri = "http://iem.local/plotting/auto/plot/%s/dpi:100::_cb:1.%s" % (i, fmt)
    try:
        res = requests.get(uri, timeout=600)
    except requests.exceptions.ReadTimeout:
        print("%s. %s -> Read Timeout" % (i, uri[16:]))
    # Known failures likely due to missing data
    if res.status_code == 400:
        return True
    if res.status_code == 504:
        print("%s. %s -> HTTP: %s (timeout)" % (i, uri, res.status_code))
        return False
    if res.status_code != 200 or res.content == "":
        print(
            "%s. %s -> HTTP: %s len(content): %s"
            % (i, uri[16:], res.status_code, len(res.content))
        )
        if res.content and fmt not in ["svg", "png", "pdf"]:
            print(res.text)
        return False

    return True


def workflow(entry):
    """Run our queued entry of id and format"""
    sts = datetime.datetime.now()
    res = run_plot(*entry)
    if res is False:
        return [entry[0], entry[1], False]
    ets = datetime.datetime.now()
    return [entry[0], entry[1], (ets - sts).total_seconds()]


def main(argv):
    """Do Something"""
    # autoplot starts at 1 and not 0
    i = 0 if len(argv) == 1 else int(argv[1])
    queue = []
    while True:
        i += 1
        fmts = get_formats(i)
        if not fmts:
            break
        for fmt in fmts:
            queue.append([i, fmt])

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
    main(sys.argv)
