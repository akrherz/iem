#!/usr/bin/env python
"""
Generate a PNG windrose based on the CGI parameters, called from

    htdocs/sites/dyn_windrose.phtml
    htdocs/sites/windrose.phtml
"""
import datetime
import cgi
import sys

import numpy
from pyiem.windrose_utils import windrose
from pyiem.network import Table as NetworkTable
from pyiem.util import ssw


def send_error(form, msg):
    """Abort, abort"""
    fmt = form.getfirst("fmt", "png")
    if fmt == "png":
        ct = "image/png"
    elif fmt == "pdf":
        ct = "application/pdf"
    elif fmt == "svg":
        ct = "image/svg+xml"
    else:
        ssw("Content-type: text/plain\n\n")
        ssw(msg)
        sys.exit(0)
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 1)
    ax.text(0.5, 0.5, msg, ha="center")
    ssw("Content-type: %s\n\n" % (ct,))
    fig.savefig(getattr(sys.stdout, "buffer", sys.stdout), format=fmt)


def get_times(form):
    """get the times of interest"""
    if (
        "year1" in form
        and "year2" in form
        and "month1" in form
        and "month2" in form
        and "day1" in form
        and "day2" in form
        and "hour1" in form
        and "hour2" in form
        and "minute1" in form
        and "minute2" in form
    ):
        sts = datetime.datetime(
            int(form["year1"].value),
            int(form["month1"].value),
            int(form["day1"].value),
            int(form["hour1"].value),
            int(form["minute1"].value),
        )
        ets = datetime.datetime(
            int(form["year2"].value),
            int(form["month2"].value),
            int(form["day2"].value),
            int(form["hour2"].value),
            int(form["minute2"].value),
        )
    else:
        sts = datetime.datetime(1900, 1, 1)
        ets = datetime.datetime(2050, 1, 1)

    return sts, ets


def main():
    """ Query out the CGI variables"""
    form = cgi.FieldStorage()
    try:
        sts, ets = get_times(form)
    except Exception:
        send_error(form, "Invalid Times Selected, please try again")
        return

    if "hour1" in form and "hourlimit" in form:
        hours = numpy.array((int(form["hour1"].value),))
    elif "hour1" in form and "hour2" in form and "hourrangelimit" in form:
        if sts.hour > ets.hour:  # over midnight
            hours = numpy.arange(sts.hour, 24)
            hours = numpy.append(hours, numpy.arange(0, ets.hour))
        else:
            if sts.hour == ets.hour:
                ets += datetime.timedelta(hours=1)
            hours = numpy.arange(sts.hour, ets.hour)
    else:
        hours = numpy.arange(0, 24)

    if "units" in form and form["units"].value in ["mph", "kts", "mps", "kph"]:
        units = form["units"].value
    else:
        units = "mph"

    if "month1" in form and "monthlimit" in form:
        months = numpy.array((int(form["month1"].value),))
    else:
        months = numpy.arange(1, 13)

    database = "asos"
    if form["network"].value in ("KCCI", "KELO", "KIMT"):
        database = "snet"
    elif form["network"].value in ("IA_RWIS",):
        database = "rwis"
    elif form["network"].value in ("ISUSM",):
        database = "isuag"
    elif form["network"].value in ("RAOB",):
        database = "postgis"
    elif form["network"].value.find("_DCP") > 0:
        database = "hads"

    try:
        nsector = int(form["nsector"].value)
    except Exception:
        nsector = 36

    rmax = None
    if "staticrange" in form and form["staticrange"].value == "1":
        rmax = 100

    nt = NetworkTable(form["network"].value, only_online=False)
    bins = []
    if "bins" in form:
        bins = [float(v) for v in form.getfirst("bins").split(",")]
        bins.insert(0, 0)
    res = windrose(
        form["station"].value,
        database=database,
        sts=sts,
        ets=ets,
        months=months,
        hours=hours,
        units=units,
        nsector=nsector,
        justdata=("justdata" in form),
        rmax=rmax,
        sname=nt.sts[form["station"].value]["name"],
        level=form.getfirst("level", None),
        bins=bins,
    )
    if "justdata" in form:
        # We want text
        ssw("Content-type: text/plain\n\n")
        ssw(res)
    else:
        fmt = form.getfirst("fmt", "png")
        if fmt == "png":
            ct = "image/png"
        elif fmt == "pdf":
            ct = "application/pdf"
        elif fmt == "svg":
            ct = "image/svg+xml"
        else:
            ssw("Content-type: text/plain\n\n")
            ssw("Invalid fmt set")
            sys.exit(0)
        ssw("Content-type: %s\n\n" % (ct,))
        res.savefig(
            getattr(sys.stdout, "buffer", sys.stdout),
            format=fmt,
            dpi=int(form.getfirst("dpi", 100)),
        )


if __name__ == "__main__":
    main()
