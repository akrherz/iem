"""
Presents the simple daily climatology as
computed by period of record data.
"""
import datetime

import pandas as pd
import requests
from matplotlib.dates import DateFormatter, DayLocator
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context
from sqlalchemy import text

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
            label="Which variable? (only Daily Max/Min is plottable attm)",
        ),
        {
            "type": "year",
            "optional": True,
            "name": "year1",
            "default": datetime.date.today().year,
            "label": "Show observed values for year:",
        },
        {
            "type": "year",
            "optional": True,
            "name": "year2",
            "default": datetime.date.today().year - 1,
            "label": "Show observed values for year:",
        },
        {
            "type": "sday",
            "default": "0101",
            "name": "sday",
            "label": "Start Plot on Day of Year:",
        },
        {
            "type": "sday",
            "default": "1231",
            "name": "eday",
            "label": "End Plot on Day of Year:",
        },
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

    title = f"{ctx['_sname']}:: Daily High/Low Temperature Climatology"
    subtitle = ""
    if ctx.get("year1") is not None:
        subtitle = f"Observed High/Low for {ctx['year1']}"
        if ctx.get("year2") is not None:
            subtitle += f" and {ctx['year2']}"
    fig = figure(title=title, subtitle=subtitle, apctx=ctx)
    ax = fig.add_axes([0.08, 0.1, 0.9, 0.8])
    x = df.index.date
    ax.fill_between(
        x,
        df["avg_high"].values,
        df["max_high"].values,
        color="#f2c2a7",
        step="post",
    )
    ax.fill_between(
        x,
        df["avg_low"].values,
        df["min_low"].values,
        color="#bbbbe2",
        step="post",
    )
    ax.fill_between(
        x,
        df["avg_low"].values,
        df["avg_high"].values,
        color="#b4dab3",
        step="post",
        label="Range of Ave High/Low",
    )
    ax.plot(
        x,
        df["max_high"].values,
        color="#dc300b",
        label="Record High",
        lw=1,
        drawstyle="steps-post",
    )
    ax.plot(
        x,
        df["min_low"].values,
        color="#444e9f",
        label="Record Low",
        lw=1,
        drawstyle="steps-post",
    )

    if ctx.get("year1") is not None:
        years = [ctx["year1"]]
        if ctx.get("year2") is not None:
            years.append(ctx["year2"])
        with get_sqlalchemy_conn("coop") as conn:
            obs = pd.read_sql(
                text(
                    """select day, year, high, low from alldata
                WHERE station = :station and year = ANY(:years)
                     order by day ASC"""
                ),
                conn,
                parse_dates="day",
                params={"station": station, "years": years},
            )
        if not obs.empty:
            obs["day"] = obs["day"].map(lambda x: x.replace(year=2000))
            colors = ["#593700", "#49aaf0"]
            for i, year in enumerate(years):
                obs2 = obs[obs["year"] == year]
                ax.bar(
                    obs2["day"].values,
                    obs2["high"] - obs2["low"],
                    bottom=obs2["low"],
                    color=colors[i],
                    align="edge",
                    label=f"Observed {year}",
                    width=0.8,
                    alpha=0.8 if len(years) > 1 else 1.0,
                )

    ax.grid(True)
    ax.legend(ncol=5)
    ax.set_ylabel(r"Temperature $^\circ$F")
    ax.set_xlim(
        ctx["sday"] - datetime.timedelta(days=1),
        ctx["eday"] + datetime.timedelta(days=1),
    )
    days = 1
    if ctx["eday"] - ctx["sday"] < datetime.timedelta(days=71):
        days = [1, 8, 15, 22, 29]
    elif ctx["eday"] - ctx["sday"] < datetime.timedelta(days=121):
        days = [1, 15]
    ax.xaxis.set_major_locator(DayLocator(bymonthday=days))
    ax.xaxis.set_major_formatter(DateFormatter("%b %-d"))

    return fig, df, res


if __name__ == "__main__":
    plotter({})
