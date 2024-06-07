"""
This autoplot is a bit of a catch-all for mapping event counts at a WFO or
CWSU map unit.  These are events that do not have VTEC.
"""

import datetime

import pandas as pd
from pyiem.plot import MapPlot, pretty_bins
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, utc
from sqlalchemy import text

PDICT = {
    "sps": "Special Weather Statements (SPS) with polygons",
    "cwa": "CWSU Center Weather Advisories (CWA)",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = utc()
    jan1 = today.replace(month=1, day=1)
    desc["arguments"] = [
        dict(
            type="datetime",
            name="sts",
            default=jan1.strftime("%Y/%m/%d 0000"),
            label="Start Timestamp (UTC):",
            min="1986/01/01 0000",
        ),
        dict(
            type="datetime",
            name="ets",
            default=today.strftime("%Y/%m/%d %H%M"),
            label="End Timestamp (UTC):",
            min="1986/01/01 0000",
            max=today.strftime("%Y/%m/%d 2359"),
        ),
        {
            "type": "select",
            "name": "w",
            "options": PDICT,
            "default": "sps",
            "label": "Which Event Type to Total",
        },
        dict(type="cmap", name="cmap", default="Greens", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    sts = ctx["sts"].replace(tzinfo=datetime.timezone.utc)
    ets = ctx["ets"].replace(tzinfo=datetime.timezone.utc)
    params = {}
    params["sts"] = sts
    params["ets"] = ets

    title = f"{PDICT[ctx['w']]} Event Count"
    subtitle = (
        f"For issuance between {sts:%Y-%m-%d %H:%M} UTC "
        f"to {ets:%Y-%m-%d %H:%M} UTC"
    )
    sql = """
    SELECT wfo as datum, count(*) from sps where issue >= :sts and issue < :ets
    and not ST_IsEmpty(geom) GROUP by datum
    """
    if ctx["w"] == "cwa":
        sql = """
        SELECT center as datum, count(*) from cwas
        WHERE issue >= :sts and issue < :ets GROUP by datum
        """
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(sql),
            conn,
            params=params,
            index_col="datum",
        )
    mp = MapPlot(
        sector="nws",
        title=title,
        subtitle=subtitle,
    )
    func = mp.fill_cwsu if ctx["w"] == "cwa" else mp.fill_cwas
    bins = list(range(0, 101, 10))
    if not df.empty:
        bins = pretty_bins(0, df["count"].max())
    func(
        df["count"],
        cmap=ctx["cmap"],
        ilabel=True,
        lblformat="%.0f",
        bins=bins,
        extend="neither",
    )
    return mp.fig, df


if __name__ == "__main__":
    plotter({})
