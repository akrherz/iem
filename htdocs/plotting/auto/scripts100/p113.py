"""daily records"""
from calendar import month_abbr
import datetime

from pyiem.util import get_autoplot_context
from pyiem.plot import figure_axes
from pyiem.exceptions import NoDataFound
import pandas as pd
import requests

PDICT = {
    "maxmin": "Daily Maximum / Minimums",
    "precip": "Daily Maximum Precipitation",
    "range": "Daily Maximum Range between High and Low",
    "means": "Daily Average High and Lows",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = dict()
    desc["data"] = True
    desc["report"] = True
    desc[
        "description"
    ] = """Presents the simple daily climatology as
    computed by period of record data."""
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            name="var",
            default="maxmin",
            options=PDICT,
            label="Which variable?",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    varname = ctx["var"]

    bs = ctx["_nt"].sts[station]["archive_begin"]
    if bs is None:
        raise NoDataFound("No Metadata found.")
    res = (
        "# IEM Climodat https://mesonet.agron.iastate.edu/climodat/\n"
        "# Report Generated: %s\n"
        "# Climate Record: %s -> %s\n"
        "# Site Information: [%s] %s\n"
        "# Contact Information: "
        "Daryl Herzmann akrherz@iastate.edu 515.294.5978\n"
    ) % (
        datetime.date.today().strftime("%d %b %Y"),
        bs.date(),
        datetime.date.today(),
        station,
        ctx["_nt"].sts[station]["name"],
    )
    df = pd.DataFrame(
        requests.get(
            f"http://iem.local/json/climodat_stclimo.py?station={station}",
            timeout=10,
        ).json()["climatology"]
    )
    if df.empty:
        raise NoDataFound("Climatology was not found.")
    df["valid"] = pd.to_datetime(
        {"year": 2000, "month": df["month"], "day": df["day"]}
    )
    for col in df.columns:
        if col.find("_years") == -1:
            continue
        df[col] = df[col].apply(lambda x: " ".join([str(i) for i in x]))
    if varname == "maxmin":
        res += (
            "# DAILY RECORD HIGHS AND LOWS OCCURRING DURING %s-%s FOR "
            "STATION NUMBER  %s\n"
            "     JAN     FEB     MAR     APR     MAY     JUN     JUL     "
            "AUG     SEP     OCT     NOV     DEC\n"
            " DY  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  "
            "MN  MX  MN  MX  MN  MX  MN  MX  MN\n"
        ) % (bs.year, datetime.date.today().year, station)
    elif varname == "means":
        res += (
            "# DAILY MEAN HIGHS AND LOWS FOR STATION NUMBER  %s\n"
            "     JAN     FEB     MAR     APR     MAY     JUN     JUL     "
            "AUG     SEP     OCT     NOV     DEC\n"
            " DY  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  "
            "MX  MN  MX  MN  MX  MN  MX  MN  MX  MN\n"
        ) % (station,)
    elif varname == "range":
        res += (
            "# RECORD LARGEST AND SMALLEST DAILY RANGES (MAX-MIN) "
            "FOR STATION NUMBER  %s\n"
            "     JAN     FEB     MAR     APR     MAY     JUN     JUL     "
            "AUG     SEP     OCT     NOV     DEC\n"
            " DY  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  "
            "MX  MN  MX  MN  MX  MN  MX  MN  MX  MN\n"
        ) % (station,)
    else:
        res += (
            f"# DAILY MAXIMUM PRECIPITATION FOR STATION NUMBER {station}\n"
            "     JAN   FEB   MAR   APR   MAY   JUN   JUL   "
            "AUG   SEP   OCT   NOV   DEC\n"
        )

    bad = "  ****" if varname == "precip" else " *** ***"
    for day in range(1, 32):
        res += "%3i" % (day,)
        for mo in range(1, 13):
            try:
                ts = datetime.date(2000, mo, day)
                if ts not in df.index:
                    res += bad
                    continue
            except Exception:
                res += bad
                continue
            row = df.loc[ts]
            if row["max_high"] is None or row["min_low"] is None:
                res += bad
                continue
            if varname == "maxmin":
                res += "%4i%4i" % (row["max_high"], row["min_low"])
            elif varname == "range":
                res += "%4i%4i" % (row["max_range"], row["min_range"])
            elif varname == "means":
                res += "%4i%4i" % (row["avg_high"], row["avg_low"])
            else:
                res += "%6.2f" % (row["max_precip"],)
        res += "\n"

    title = "[%s] %s Daily Climatology" % (
        station,
        ctx["_nt"].sts[station]["name"],
    )
    (fig, ax) = figure_axes(title=title)
    x = df["valid"].values
    ax.plot(range(len(x)), df["avg_high"].values, color="r", label="High")
    ax.plot(range(len(x)), df["avg_low"].values, color="b", label="Low")
    ax.grid(True)
    ax.legend()
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(month_abbr[1:])
    ax.set_xlim(0, 366)

    return fig, df, res


if __name__ == "__main__":
    plotter({})
