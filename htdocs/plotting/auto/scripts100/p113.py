"""
Presents the simple daily climatology as
computed by period of record data.
"""
import datetime
from calendar import month_abbr

import pandas as pd
import requests
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context

PDICT = {
    "maxmin": "Daily Maximum / Minimums",
    "precip": "Daily Maximum Precipitation",
    "range": "Daily Maximum Range between High and Low",
    "means": "Daily Average High and Lows",
}


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
        f"# Report Generated: {datetime.date.today():%d %b %Y}\n"
        f"# Climate Record: {bs} -> {datetime.date.today()}\n"
        f"# Site Information: [{station}] {ctx['_nt'].sts[station]['name']}\n"
        "# Contact Information: "
        "Daryl Herzmann akrherz@iastate.edu 515.294.5978\n"
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
    df = df.set_index("valid")
    for col in df.columns:
        if col.find("_years") == -1:
            continue
        df[col] = df[col].apply(lambda x: " ".join([str(i) for i in x]))
    if varname == "maxmin":
        res += (
            f"# DAILY RECORD HIGHS AND LOWS OCCURRING DURING {bs.year}-"
            f"{datetime.date.today().year} FOR "
            f"STATION NUMBER  {station}\n"
            "     JAN     FEB     MAR     APR     MAY     JUN     JUL     "
            "AUG     SEP     OCT     NOV     DEC\n"
            " DY  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  "
            "MN  MX  MN  MX  MN  MX  MN  MX  MN\n"
        )
    elif varname == "means":
        res += (
            f"# DAILY MEAN HIGHS AND LOWS FOR STATION NUMBER  {station}\n"
            "     JAN     FEB     MAR     APR     MAY     JUN     JUL     "
            "AUG     SEP     OCT     NOV     DEC\n"
            " DY  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  "
            "MX  MN  MX  MN  MX  MN  MX  MN  MX  MN\n"
        )
    elif varname == "range":
        res += (
            "# RECORD LARGEST AND SMALLEST DAILY RANGES (MAX-MIN) "
            f"FOR STATION NUMBER  {station}\n"
            "     JAN     FEB     MAR     APR     MAY     JUN     JUL     "
            "AUG     SEP     OCT     NOV     DEC\n"
            " DY  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  MX  MN  "
            "MX  MN  MX  MN  MX  MN  MX  MN  MX  MN\n"
        )
    else:
        res += (
            f"# DAILY MAXIMUM PRECIPITATION FOR STATION NUMBER {station}\n"
            "     JAN   FEB   MAR   APR   MAY   JUN   JUL   "
            "AUG   SEP   OCT   NOV   DEC\n"
        )

    bad = "  ****" if varname == "precip" else " *** ***"
    for day in range(1, 32):
        res += f"{day:3.0f}"
        for mo in range(1, 13):
            try:
                ts = datetime.datetime(2000, mo, day)
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
                res += f"{row['max_high']:4.0f}{row['min_low']:4.0f}"
            elif varname == "range":
                res += f"{row['max_range']:4.0f}{row['min_range']:4.0f}"
            elif varname == "means":
                res += f"{row['avg_high']:4.0f}{row['avg_low']:4.0f}"
            else:
                res += f"{row['max_precip']:6.2f}"
        res += "\n"

    title = f"[{station}] {ctx['_nt'].sts[station]['name']} Daily Climatology"
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    x = df.index.values
    ax.plot(range(len(x)), df["avg_high"].values, color="r", label="High")
    ax.plot(range(len(x)), df["avg_low"].values, color="b", label="Low")
    ax.grid(True)
    ax.legend()
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(month_abbr[1:])
    ax.set_xlim(0, 366)

    return fig, df, res


if __name__ == "__main__":
    plotter({"var": "range"})
