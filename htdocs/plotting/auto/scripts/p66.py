"""
This chart presents the daily frequency of the
given date having the prescribed number of previous days above or below
some provided treshold. <a href="/plotting/auto/?q=216">Autoplot 216</a>
provides actual streaks and yearly maximum values.
"""
import calendar

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

PDICT = {
    "above": "Temperature At or Above (AOA) Threshold",
    "below": "Temperature Below Threshold",
}
PDICT2 = {"high": "High Temperature", "low": "Low Temperature"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            name="var",
            default="high",
            options=PDICT2,
            label="Select which daily variable",
        ),
        dict(
            type="select",
            name="dir",
            default="above",
            options=PDICT,
            label="Select temperature direction",
        ),
        dict(
            type="int",
            name="threshold",
            default="60",
            label="Temperature Threshold (F):",
        ),
        dict(type="int", name="days", default="7", label="Number of Days:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    days = ctx["days"]
    threshold = ctx["threshold"]
    varname = ctx["var"]
    mydir = ctx["dir"]

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            f"select day, sday, {varname} from alldata where station = %s "
            "ORDER by day ASC",
            conn,
            params=(station,),
            index_col="day",
            parse_dates="day",
        )
    if df.empty:
        raise NoDataFound("No data found for station / threshold.")
    syear = df.index[0].year
    eyear = df.index[-1].year
    years = eyear - syear + 1
    df["trail"] = (
        df[varname]
        .rolling(window=f"{days}D")
        .agg("min" if mydir == "above" else "max")
    )
    if mydir == "above":
        df = df.loc[df["trail"] >= threshold]
    else:
        df = df.loc[df["trail"] < threshold]
    if df.empty:
        raise NoDataFound("No events found for threshold.")

    freq = df.drop(columns="trail").groupby("sday").count() / years * 100.0
    freq = freq.reindex(
        pd.date_range("2000-01-01", "2000-12-31").strftime("%m%d")
    ).fillna(0)

    label = "AOA" if mydir == "above" else "below"
    title = (
        f"{ctx['_sname']} [{syear}-{eyear}] ::"
        f"Frequency of {days} Consec Days "
        f"with {varname.capitalize()} {label} {threshold}"
        r"$^\circ$F "
    )
    fig, ax = figure_axes(apctx=ctx, title=title)
    ax.set_position([0.1, 0.1, 0.75, 0.8])
    ax.set_ylabel("Frequency of Streak Including Day of Year [%]")
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.grid(True)
    ax.bar(range(366), freq[varname], width=1)

    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 366)

    df = df.sort_values("sday")
    ypos = 0.85
    xpos = 0.87
    fig.text(xpos, ypos + 0.03, "End Date of Streak")
    fig.text(xpos - 0.015, ypos, "Earliest Dates   ", rotation=90, va="top")
    for day, row in df.head(10).iterrows():
        ypos -= 0.03
        fig.text(
            xpos, ypos, f"{day.strftime('%-2d %b %Y')} {row['trail']:.0f}"
        )

    ypos -= 0.1
    fig.text(xpos - 0.015, ypos, "Latest Dates   ", rotation=90, va="top")
    for day, row in df.tail(10).iloc[::-1].iterrows():
        ypos -= 0.03
        fig.text(
            xpos, ypos, f"{day.strftime('%-2d %b %Y')} {row['trail']:.0f}"
        )

    return fig, freq


if __name__ == "__main__":
    plotter({})
