"""
This plot presents a summary of the number of year
to date watches issued by the Storm Prediction Center and the percentage
of those watches that at least touched the given state, county warning area,
or fema region.
"""

from datetime import date

import matplotlib.ticker as ticker
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.reference import state_names
from pyiem.util import get_autoplot_context
from sqlalchemy import text

from iemweb.autoplot import ARG_FEMA

PDICT = {
    "state": "View by State",
    "cwa": "View by NWS WFO",
    "fema": "View by FEMA Region",
}
MDICT = {
    "ytd": "Limit Plot to Year to Date",
    "year": "Plot Entire Year of Data",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"data": True, "description": __doc__}
    desc["arguments"] = [
        {
            "type": "select",
            "name": "w",
            "default": "state",
            "options": PDICT,
            "label": "View by:",
        },
        dict(type="state", name="state", default="IA", label="Select State:"),
        dict(
            type="networkselect",
            name="cwa",
            network="WFO",
            default="DMX",
            label="Select WFO (when appropriate):",
            all=True,
        ),
        ARG_FEMA,
        dict(
            type="select",
            name="limit",
            default="ytd",
            options=MDICT,
            label="Time Limit of Plot",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    state = ctx["state"][:2].upper()
    limit = ctx["limit"]

    sqllimit = ""
    ets = "31 December"
    if limit == "ytd":
        ets = date.today().strftime("%-d %B")
        sqllimit = "extract(doy from issued) <= extract(doy from now()) and "

    # Get total issued
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(f"""
            Select extract(year from issued)::int as year,
            count(*) as national_count from watches
            where {sqllimit} num < 3000 GROUP by year ORDER by year ASC
        """),
            conn,
            index_col="year",
        )
    if df.empty:
        raise NoDataFound("No data was found.")

    params = {
        "state": state,
        "fema": ctx["fema"],
        "wfo": ctx["cwa"],
    }
    if ctx["w"] == "state":
        geomcol = "the_geom"
        table = "states"
        abbrsql = " s.state_abbr = :state "
        title = f"State of {state_names[state]}"
    elif ctx["w"] == "cwa":
        geomcol = "the_geom"
        table = "cwa"
        abbrsql = " s.cwa = :wfo "
        title = f"NWS Weather Forecast Office {ctx['_sname']}"
    else:  # fema
        geomcol = "geom"
        table = "fema_regions"
        abbrsql = " s.region = :fema "
        title = f"FEMA Region {ctx['fema']}"
    # Get total issued
    with get_sqlalchemy_conn("postgis") as conn:
        odf = pd.read_sql(
            text(f"""
            select extract(year from issued)::int as year,
            count(*) as datum_count
            from watches w, {table} s where w.geom && s.{geomcol} and
            ST_Intersects(w.geom, s.{geomcol}) and {sqllimit} {abbrsql}
            GROUP by year ORDER by year ASC
        """),
            conn,
            params=params,
            index_col="year",
        )
    df["datum_count"] = odf["datum_count"]
    df["datum_percent"] = df["datum_count"] / df["national_count"] * 100.0
    df = df.fillna(0)

    fig = figure(apctx=ctx)
    ax = fig.subplots(3, 1, sharex=True)

    ax[0].bar(df.index.values, df["national_count"].values, align="center")
    for year, row in df.iterrows():
        ax[0].text(
            year,
            row["national_count"],
            f" {row['national_count']:.0f}",
            ha="center",
            rotation=90,
            va="bottom",
            color="k",
        )
    ax[0].grid(True)
    ax[0].set_title(
        "Storm Prediction Center Issued Tornado / Svr T'Storm Watches\n"
        f"1 January to {ets}, Watch Outlines touching {title}"
    )
    ax[0].set_ylabel("National Count")
    ax[0].set_ylim(0, df["national_count"].max() * 1.3)

    ax[1].bar(df.index.values, df["datum_count"].values, align="center")
    for year, row in df.iterrows():
        ax[1].text(
            year,
            row["datum_count"],
            f" {row['datum_count']:.0f}",
            ha="center",
            rotation=90,
            va="bottom",
            color="k",
        )
    ax[1].grid(True)
    ax[1].set_ylabel("Count")
    ax[1].set_ylim(0, df["datum_count"].max() * 1.3)

    ax[2].bar(df.index.values, df["datum_percent"].values, align="center")
    for year, row in df.iterrows():
        ax[2].text(
            year,
            row["datum_percent"],
            f" {row['datum_percent']:.1f}%",
            ha="center",
            rotation=90,
            va="bottom",
            color="k",
        )
    ax[2].grid(True)
    ax[2].set_ylabel("% Touching")
    ax[2].set_ylim(0, df["datum_percent"].max() * 1.3)

    ax[0].set_xlim(df.index.values[0] - 1, df.index.values[-1] + 1)
    ax[0].xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    return fig, df
