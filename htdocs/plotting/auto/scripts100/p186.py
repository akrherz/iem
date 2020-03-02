"""USDM Filled Time Series"""
import datetime
import calendar

import numpy as np
import requests
import pandas as pd
from scipy.interpolate import interp1d
from pyiem import util
from pyiem.plot.use_agg import plt
from pyiem.reference import state_names, state_fips
from pyiem.exceptions import NoDataFound

SERVICE = (
    "https://droughtmonitor.unl.edu"
    "/Ajax2018.aspx/ReturnTabularDMAreaPercent_state"
)
COLORS = ["#ffff00", "#fcd37f", "#ffaa00", "#e60000", "#730000"]


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This plot shows the weekly change in drought
    monitor intensity expressed in terms of category change over the area
    of the selected state.  For example, an arrow of length one pointing
    up would indicate a one category improvement in drought over the area
    of the state. This
    plot uses a JSON data service provided by the
    <a href="http://droughtmonitor.unl.edu">Drought Monitor</a> website.
    """
    thisyear = datetime.date.today().year
    desc["arguments"] = [
        dict(type="state", name="state", default="IA", label="Select State:"),
        dict(
            type="year",
            name="syear",
            min=2000,
            default=2000,
            label="Start year for plot",
        ),
        dict(
            type="year",
            name="eyear",
            max=thisyear,
            default=thisyear,
            label="End year (inclusive) for plot",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    ctx = util.get_autoplot_context(fdict, get_description())
    state = ctx["state"]
    syear = ctx["syear"]
    eyear = ctx["eyear"]

    fips = ""
    for key in state_fips:
        if state_fips[key] == state:
            fips = key
    payload = "{'area':'%s', 'type':'state', 'statstype':'2'}" % (fips,)
    headers = {}
    headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
    headers["Content-Type"] = "application/json; charset=UTF-8"
    req = util.exponential_backoff(
        requests.post, SERVICE, payload, headers=headers
    )
    if req is None:
        raise NoDataFound("Drought Web Service failed to deliver data.")
    jdata = req.json()
    if "d" not in jdata:
        raise NoDataFound("Data Not Found.")
    df = pd.DataFrame(jdata["d"])
    df["Date"] = pd.to_datetime(df["ReleaseDate"])
    df.sort_values("Date", ascending=True, inplace=True)
    df["x"] = df["Date"] + datetime.timedelta(hours=(3.5 * 24))

    fig = plt.figure(figsize=(7, 9))
    ax = fig.add_axes([0.1, 0.1, 0.87, 0.84])
    lastrow = None
    for year, gdf in df.groupby(df.Date.dt.year):
        if year < syear or year > eyear:
            continue
        xs = []
        ys = []
        for _, row in gdf.iterrows():
            if lastrow is None:
                lastrow = row
            delta = (
                (lastrow["D4"] - row["D4"]) * 5.0
                + (lastrow["D3"] - row["D3"]) * 4.0
                + (lastrow["D2"] - row["D2"]) * 3.0
                + (lastrow["D1"] - row["D1"]) * 2.0
                + (lastrow["D0"] - row["D0"])
            )
            xs.append(int(row["Date"].strftime("%j")))
            ys.append(year + (0 - delta) / 100.0)
            lastrow = row
        if len(xs) < 4:
            continue
        fcube = interp1d(xs, ys, kind="cubic")
        xnew = np.arange(xs[0], xs[-1])
        yval = np.ones(len(xnew)) * year
        ynew = fcube(xnew)
        ax.fill_between(
            xnew,
            yval,
            ynew,
            where=(ynew < yval),
            facecolor="blue",
            interpolate=True,
        )
        ax.fill_between(
            xnew,
            yval,
            ynew,
            where=(ynew >= yval),
            facecolor="red",
            interpolate=True,
        )

    ax.set_ylim(eyear + 1, syear - 1)
    ax.set_xlim(0, 366)
    ax.set_xlabel(
        (
            "curve height of 1 year is 1 effective drought category "
            "change over area of %s"
        )
        % (state_names[state],)
    )
    ax.set_ylabel("Year, thru %s" % (df.Date.max().strftime("%d %b %Y"),))
    ax.set_title(
        (
            "%.0f-%.0f US Drought Monitor Weekly Change for %s\n"
            "curve height represents change in intensity + coverage"
        )
        % (syear, eyear, state_names[state])
    )

    ax.grid(True)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 365))
    ax.set_xticklabels(calendar.month_abbr[1:])

    ax.set_yticks(
        np.arange(ax.get_ylim()[0] - 1, ax.get_ylim()[1], -1, dtype="i")
    )
    fig.text(0.02, 0.03, "Blue areas are improving conditions", color="b")
    fig.text(0.4, 0.03, "Red areas are degrading conditions", color="r")

    return fig, df[["Date", "NONE", "D0", "D1", "D2", "D3", "D4"]]


if __name__ == "__main__":
    plotter(dict())
