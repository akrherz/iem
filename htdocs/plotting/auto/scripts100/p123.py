"""Climodat consec days"""
import datetime

import numpy as np
import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.util import get_autoplot_context, get_dbconn


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "report": True}
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station",
            network="IACLIMATE",
        )
    ]
    return desc


def wrap(cnt, s=None):
    """Helper."""
    if cnt > 0:
        return s or cnt
    return ""


def contiguous_regions(condition):
    # http://stackoverflow.com/questions/4494404
    """Finds contiguous True regions of the boolean array "condition". Returns
    a 2D array where the first column is the start index of the region and the
    second column is the end index."""

    # Find the indicies of changes in "condition"
    # d = np.diff(condition)
    d = np.subtract(condition[1:], condition[:-1], dtype=float)
    (idx,) = d.nonzero()

    # We need to start things after the change in "condition". Therefore,
    # we'll shift the index by 1 to the right.
    idx += 1

    if condition[0]:
        # If the start of condition is True prepend a 0
        idx = np.r_[0, idx]

    if condition[-1]:
        # If the end of condition is True, append the length of the array
        idx = np.r_[idx, condition.size]  # Edit

    # Reshape the result into two columns
    idx.shape = (-1, 2)
    return idx


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]

    bs = ctx["_nt"].sts[station]["archive_begin"]
    if bs is None:
        raise NoDataFound("No Data Found.")
    res = (
        "# IEM Climodat https://mesonet.agron.iastate.edu/climodat/\n"
        "# Report Generated: %s\n"
        "# Climate Record: %s -> %s\n"
        "# Site Information: [%s] %s\n"
        "# Contact Information: Daryl Herzmann akrherz@iastate.edu "
        "515.294.5978\n"
        "# First occurance of record consecutive number of days\n"
        "# above or below a temperature threshold\n"
    ) % (
        datetime.date.today().strftime("%d %b %Y"),
        bs,
        datetime.date.today(),
        station,
        ctx["_nt"].sts[station]["name"],
    )
    res += "#   %-27s %-27s  %-27s %-27s\n" % (
        " Low Cooler Than",
        " Low Warmer Than",
        " High Cooler Than",
        " High Warmer Than",
    )
    res += "%3s %5s %10s %10s %5s %10s %10s  %5s %10s %10s %5s %10s %10s\n" % (
        "TMP",
        "DAYS",
        "BEGIN DATE",
        "END DATE",
        "DAYS",
        "BEGIN DATE",
        "END DATE",
        "DAYS",
        "BEGIN DATE",
        "END DATE",
        "DAYS",
        "BEGIN DATE",
        "END DATE",
    )

    cursor.execute(
        "SELECT high, low from alldata WHERE station = %s and "
        "day >= '1900-01-01' ORDER by day ASC",
        (station,),
    )
    highs = np.zeros((cursor.rowcount,), "f")
    lows = np.zeros((cursor.rowcount,), "f")
    for i, row in enumerate(cursor):
        highs[i] = row[0]
        lows[i] = row[1]

    startyear = max([1900, bs.year])
    rows = []
    for thres in range(-20, 101, 2):
        condition = lows < thres
        max_bl = 0
        max_bl_ts = datetime.date.today()
        for start, stop in contiguous_regions(condition):
            if (stop - start) > max_bl:
                max_bl = int(stop - start)
                max_bl_ts = datetime.date(
                    startyear, 1, 1
                ) + datetime.timedelta(days=int(stop))
        condition = lows >= thres
        max_al = 0
        max_al_ts = datetime.date.today()
        for start, stop in contiguous_regions(condition):
            if (stop - start) > max_al:
                max_al = int(stop - start)
                max_al_ts = datetime.date(
                    startyear, 1, 1
                ) + datetime.timedelta(days=int(stop))
        condition = highs < thres
        max_bh = 0
        max_bh_ts = datetime.date.today()
        for start, stop in contiguous_regions(condition):
            if (stop - start) > max_bh:
                max_bh = int(stop - start)
                max_bh_ts = datetime.date(
                    startyear, 1, 1
                ) + datetime.timedelta(days=int(stop))
        condition = highs >= thres
        max_ah = 0
        max_ah_ts = datetime.date.today()
        for start, stop in contiguous_regions(condition):
            if (stop - start) > max_ah:
                max_ah = int(stop - start)
                max_ah_ts = datetime.date(
                    startyear, 1, 1
                ) + datetime.timedelta(days=int(stop))

        max_bl_sdate = (max_bl_ts - datetime.timedelta(days=max_bl)).strftime(
            "%m/%d/%Y"
        )
        max_bl_edate = max_bl_ts.strftime("%m/%d/%Y")
        max_bh_sdate = (max_bh_ts - datetime.timedelta(days=max_bh)).strftime(
            "%m/%d/%Y"
        )
        max_bh_edate = max_bh_ts.strftime("%m/%d/%Y")
        max_al_sdate = (max_al_ts - datetime.timedelta(days=max_al)).strftime(
            "%m/%d/%Y"
        )
        max_al_edate = max_al_ts.strftime("%m/%d/%Y")
        max_ah_sdate = (max_ah_ts - datetime.timedelta(days=max_ah)).strftime(
            "%m/%d/%Y"
        )
        max_ah_edate = max_ah_ts.strftime("%m/%d/%Y")
        rows.append(
            dict(
                thres=thres,
                max_low_below=max_bl,
                max_high_below=max_bh,
                max_low_above=max_al,
                max_high_above=max_ah,
                max_low_below_sdate=max_bl_sdate,
                max_low_below_edate=max_bl_edate,
                max_low_above_sdate=max_al_sdate,
                max_low_above_edate=max_al_edate,
                max_high_below_sdate=max_bh_sdate,
                max_high_below_edate=max_bh_edate,
                max_high_above_sdate=max_ah_sdate,
                max_high_above__edate=max_ah_edate,
            )
        )
        res += (
            "%3i %5s %10s %10s %5s %10s %10s  " "%5s %10s %10s %5s %10s %10s\n"
        ) % (
            thres,
            wrap(max_bl),
            wrap(max_bl, max_bl_sdate),
            wrap(max_bl, max_bl_edate),
            wrap(max_al),
            wrap(max_al, max_al_sdate),
            wrap(max_al, max_al_edate),
            wrap(max_bh),
            wrap(max_bh, max_bh_sdate),
            wrap(max_bh, max_bh_edate),
            wrap(max_ah),
            wrap(max_ah, max_ah_sdate),
            wrap(max_ah, max_ah_edate),
        )

    df = pd.DataFrame(rows)
    df = df.set_index("thres")
    df.index.name = "threshold"
    return None, df, res


if __name__ == "__main__":
    plotter({})
