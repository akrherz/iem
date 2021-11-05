"""Watches"""
import datetime

from pandas.io.sql import read_sql
import matplotlib.ticker as ticker
from pyiem import util
from pyiem.plot import figure
from pyiem.reference import state_names
from pyiem.exceptions import NoDataFound

MDICT = {
    "ytd": "Limit Plot to Year to Date",
    "year": "Plot Entire Year of Data",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This plot presents a summary of the number of year
    to date watches issued by the Storm Prediction Center and the percentage
    of those watches that at least touched the given state.
    """
    desc["arguments"] = [
        dict(type="state", name="state", default="IA", label="Select State:"),
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
    pgconn = util.get_dbconn("postgis")
    ctx = util.get_autoplot_context(fdict, get_description())
    state = ctx["state"][:2].upper()
    limit = ctx["limit"]

    sqllimit = ""
    ets = "31 December"
    if limit == "ytd":
        ets = datetime.date.today().strftime("%-d %B")
        sqllimit = "extract(doy from issued) <= extract(doy from now()) and "

    # Get total issued
    df = read_sql(
        f"""
        Select extract(year from issued)::int as year,
        count(*) as national_count from watches
        where {sqllimit} num < 3000 GROUP by year ORDER by year ASC
    """,
        pgconn,
        index_col="year",
    )
    if df.empty:
        raise NoDataFound("No data was found.")

    # Get total issued
    odf = read_sql(
        f"""
        select extract(year from issued)::int as year, count(*) as state_count
        from watches w, states s where w.geom && s.the_geom and
        ST_Intersects(w.geom, s.the_geom) and {sqllimit} s.state_abbr = %s
        GROUP by year ORDER by year ASC
    """,
        pgconn,
        params=(state,),
        index_col="year",
    )
    df["state_count"] = odf["state_count"]
    df["state_percent"] = df["state_count"] / df["national_count"] * 100.0
    df.fillna(0, inplace=True)

    fig = figure(apctx=ctx)
    ax = fig.subplots(3, 1, sharex=True)

    ax[0].bar(df.index.values, df["national_count"].values, align="center")
    for year, row in df.iterrows():
        ax[0].text(
            year,
            row["national_count"],
            " %.0f" % (row["national_count"],),
            ha="center",
            rotation=90,
            va="bottom",
            color="k",
        )
    ax[0].grid(True)
    ax[0].set_title(
        (
            "Storm Prediction Center Issued Tornado / "
            "Svr T'Storm Watches\n"
            "1 January to %s, Watch Outlines touching %s"
        )
        % (ets, state_names[state])
    )
    ax[0].set_ylabel("National Count")
    ax[0].set_ylim(0, df["national_count"].max() * 1.3)

    ax[1].bar(df.index.values, df["state_count"].values, align="center")
    for year, row in df.iterrows():
        ax[1].text(
            year,
            row["state_count"],
            " %.0f" % (row["state_count"],),
            ha="center",
            rotation=90,
            va="bottom",
            color="k",
        )
    ax[1].grid(True)
    ax[1].set_ylabel("State Count")
    ax[1].set_ylim(0, df["state_count"].max() * 1.3)

    ax[2].bar(df.index.values, df["state_percent"].values, align="center")
    for year, row in df.iterrows():
        ax[2].text(
            year,
            row["state_percent"],
            " %.1f%%" % (row["state_percent"],),
            ha="center",
            rotation=90,
            va="bottom",
            color="k",
        )
    ax[2].grid(True)
    ax[2].set_ylabel("% Touching State")
    ax[2].set_ylim(0, df["state_percent"].max() * 1.3)

    ax[0].set_xlim(df.index.values[0] - 1, df.index.values[-1] + 1)
    ax[0].xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    return fig, df


if __name__ == "__main__":
    plotter(dict())
