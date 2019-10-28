"""Compute max/min Temp max/min Dew Point and Precipitation

But be careful about not overwritting 'better' data gleaned from CLI/DSM
"""
from __future__ import print_function
import sys
import datetime
import warnings

import numpy as np
from pyiem.util import get_dbconn

warnings.simplefilter("ignore", RuntimeWarning)


def do(ts):
    """Process this date timestamp"""
    asos = get_dbconn("asos", user="nobody")
    cursor = asos.cursor()
    iemaccess = get_dbconn("iem")
    icursor = iemaccess.cursor()
    cursor.execute(
        """
    select station, network, iemid, valid at time zone tzname,
    tmpf, dwpf, p01i from alldata d JOIN stations t on (t.id = d.station)
    where (network ~* 'ASOS' or network = 'AWOS')
    and valid between %s and %s ORDER by valid ASC
    """,
        (ts - datetime.timedelta(days=2), ts + datetime.timedelta(days=2)),
    )
    data = {}
    for row in cursor:
        if row[3].strftime("%m%d") != ts.strftime("%m%d"):
            continue
        station = "%s|%s|%s" % (row[0], row[1], row[2])
        _d = data.setdefault(
            station, {"valid": [], "tmpf": [], "dwpf": [], "p01i": []}
        )
        _d["valid"].append(row[3])
        _d["tmpf"].append(row[4] if row[4] is not None else np.nan)
        _d["dwpf"].append(row[5] if row[5] is not None else np.nan)
        _d["p01i"].append(row[6] if row[6] is not None else np.nan)

    table = "summary_%s" % (ts.year,)
    # Load up current data
    current = {}
    icursor.execute(
        """
        SELECT id, network, d.iemid, max_tmpf, min_tmpf,
        max_dwpf, min_dwpf, pday from """
        + table
        + """ d JOIN stations t
        on (t.iemid = d.iemid) WHERE day = %s and
        (network ~* 'ASOS' or network = 'AWOS')
    """,
        (ts,),
    )
    for row in icursor:
        station = "%s|%s|%s" % (row[0], row[1], row[2])
        current[station] = dict(
            max_tmpf=row[3],
            min_tmpf=row[4],
            max_dwpf=row[5],
            min_dwpf=row[6],
            pday=row[7],
        )
    for stid in data:
        # Not enough data
        if len(data[stid]["valid"]) < 4:
            continue
        # Compute the time coverage, assume we are okay if we have 18 hrs
        delta = (max(data[stid]["valid"]) - min(data[stid]["valid"])).seconds
        if delta < (18 * 60):
            continue

        station, network, iemid = stid.split("|")
        computed = dict()
        computed["max_tmpf"] = np.nanmax(data[stid]["tmpf"])
        computed["min_tmpf"] = np.nanmin(data[stid]["tmpf"])
        computed["max_dwpf"] = np.nanmax(data[stid]["dwpf"])
        computed["min_dwpf"] = np.nanmin(data[stid]["dwpf"])
        # BUG: obs that may spill over the top of the hour
        pday = [0] * 24
        for i, valid in enumerate(data[stid]["valid"]):
            p01i = data[stid]["p01i"][i]
            if p01i is not None and p01i > 0:
                hr = int(valid.strftime("%H"))
                pday[hr] = max([pday[hr], p01i])
        computed["pday"] = np.sum(pday)

        if stid not in current:
            print(
                ("compute_tp Adding %s for %s %s %s")
                % (table, station, network, ts)
            )
            icursor.execute(
                """
                INSERT into """
                + table
                + """
                (iemid, day) values (%s, %s)
            """,
                (iemid, ts),
            )
            current[stid] = dict()

        tokens = []
        for vname in ["max_tmpf", "min_tmpf", "max_dwpf", "min_dwpf", "pday"]:
            oldval = current[stid].get(vname)
            newval = computed.get(vname)
            # print vname, oldval, newval
            if newval is None or np.isnan(newval):
                continue
            if oldval is None:
                fmt = "%.2f" if vname == "pday" else "%.0f"
                tokens.append("%s = %s" % (vname, fmt % newval))

        if not tokens:
            continue

        cols = ", ".join(tokens)
        icursor.execute(
            """
            UPDATE """
            + table
            + """
            SET """
            + cols
            + """ WHERE
            iemid = %s and day = %s
        """,
            (iemid, ts),
        )

    icursor.close()
    iemaccess.commit()
    iemaccess.close()


def main(argv):
    """Go Main Go"""
    ts = datetime.date.today() - datetime.timedelta(days=1)
    if len(argv) == 4:
        ts = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    do(ts)


if __name__ == "__main__":
    main(sys.argv)
