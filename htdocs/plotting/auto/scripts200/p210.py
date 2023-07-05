"""
This application generates a map of the per WFO office usage of a
given text product identifier based on unofficial IEM archives of NWS
Text Product data.  The three character IDs presented here are sometimes
called the AWIPS ID or AFOS ID.</p>

<p>If you pick the "Year of First/Last Issuance",
please be careful with the
start datetime setting as it will floor the time period that products
are searched for.</p>

<p>The IEM Archives are generally reliable back to 2001, so please note
that any 2001 values plotted on the map as the first year would be a false
positive.</p>

<p>Running a plot for multiple years of data will be somewhat slow
(30+ seconds), so please be patient with it!</p>

<p><a href="?q=235">Autoplot 235</a> presents a monthly/yearly chart of
issuance counts for a single Weather Forecast Offices.</p>
"""
import datetime

import numpy as np
import pandas as pd
import pytz
from pyiem.exceptions import NoDataFound
from pyiem.plot.geoplot import MapPlot
from pyiem.reference import prodDefinitions
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, utc

PDICT = {
    "count": "Issuance Count",
    "last": "Year of Last Issuance",
    "first": "Year of First Issuance",
}
PDICT2 = {
    "cwsu": "Center Weather Service Unit (CWSU)",
    "rfc": "River Forecast Center (RFC)",
    "cwa": "Weather Forecast Office (WFO) / CWA",
}


def fix():
    """muck with the prodDefinitions to get the key included"""
    for key, val in prodDefinitions.items():
        if val.startswith("["):
            continue
        prodDefinitions[key] = f"[{key}] {prodDefinitions[key]}"


def get_description():
    """Return a dict describing how to call this plotter"""
    fix()
    desc = {"description": __doc__, "cache": 300, "data": True}
    now = utc() + datetime.timedelta(days=1)
    desc["arguments"] = [
        dict(
            type="select",
            name="pil",
            default="AFD",
            label="Select 3 Character Product ID (AWIPS ID / AFOS)",
            options=prodDefinitions,
        ),
        dict(
            type="select",
            name="var",
            options=PDICT,
            label="Statistic to Plot",
            default="count",
        ),
        {
            "type": "select",
            "name": "w",
            "options": PDICT2,
            "label": "Summarize by:",
            "default": "cwa",
        },
        dict(
            type="datetime",
            name="sts",
            default=now.strftime("%Y/01/01 0000"),
            label="Search archive starting at (UTC Timestamp):",
            min="2001/01/01 0000",
        ),
        dict(
            type="datetime",
            name="ets",
            default=now.strftime("%Y/%m/%d 0000"),
            label="Search archive ending at (UTC Timestamp):",
            min="2001/01/01 0000",
            max=now.strftime("%Y/%m/%d 2359"),
        ),
        dict(type="cmap", name="cmap", default="jet", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    fix()
    ctx = get_autoplot_context(fdict, get_description())
    pil = ctx["pil"][:3]
    if ctx["ets"].astimezone(pytz.UTC) > utc():
        ctx["ets"] = utc()

    with get_sqlalchemy_conn("afos") as conn:
        df = pd.read_sql(
            "SELECT source, pil, min(entered at time zone 'UTC') as first, "
            "max(entered at time zone 'UTC') as last, count(*) from products "
            "WHERE substr(pil, 1, 3) = %s and entered >= %s and entered < %s "
            "GROUP by source, pil ORDER by source, pil ASC",
            conn,
            params=(pil, ctx["sts"], ctx["ets"]),
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No text products found for query, sorry.")

    data = {}
    if ctx["var"] == "count":
        gdf = df.groupby("source").sum(numeric_only=True)  # dt makes no sense
    elif ctx["var"] == "last":
        gdf = df.groupby("source").max()
    else:  # first
        gdf = df.groupby("source").min()
    minval = 1
    maxval = gdf["count"].max()
    if ctx["var"] in ["last", "first"]:
        minval = gdf[ctx["var"]].min().year
        maxval = gdf[ctx["var"]].max().year
    if (maxval - minval) < 10:
        bins = range(minval - 1, maxval + 2)
    else:
        bins = np.linspace(minval, maxval + 2, 10, dtype="i")
    for source, row in gdf.iterrows():
        if source == "PABR":
            continue
        key = source[1:]
        if key == "JSJ":
            key = "SJU"
        if ctx["var"] == "count":
            data[key] = row["count"]
        else:
            data[key] = row[ctx["var"]].year

    mp = MapPlot(
        apctx=ctx,
        title=f"NWS {PDICT[ctx['var']]} of {prodDefinitions[pil]}",
        subtitle=(
            f"Plot valid between {ctx['sts']:%d %b %Y %H:%M} UTC "
            f"and {ctx['ets']:%d %b %Y %H:%M} UTC, "
            "based on unofficial IEM Archives"
        ),
        sector="nws",
        nocaption=True,
    )
    func = {
        "cwa": mp.fill_cwas,
        "cwsu": mp.fill_cwsu,
        "rfc": mp.fill_rfc,
    }
    func[ctx["w"]](
        data,
        ilabel=True,
        lblformat="%.0f",
        cmap=ctx["cmap"],
        extend="neither",
        bins=bins,
        units="count" if ctx["var"] == "count" else "year",
        labelbuffer=0,
    )
    return mp.fig, df


if __name__ == "__main__":
    plotter({})
