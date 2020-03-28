"""A fancy pants plot of a given VTEC headline."""

import pandas as pd
from geopandas import read_postgis
from pyiem.nws import vtec
from pyiem.plot.geoplot import MapPlot
from pyiem.util import get_autoplot_context, get_dbconn, utc
from pyiem.exceptions import NoDataFound
from pyiem.reference import Z_OVERLAY2
import cartopy.crs as ccrs
import pytz

TFORMAT = "%b %-d %Y %-I:%M %p %Z"
PDICT = {
    "twitter": "Twitter Friendly 1200x628",
    "normal": "IEM Default 640x480",
}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["cache"] = 300
    desc["data"] = True
    desc[
        "description"
    ] = """This application generates a map showing the coverage of a given
    VTEC alert for a given office.  The tricky part here is how time is handled
    for events whereby zones/counties can be added / removed from the alert.
    If you specific an exact time, you should get the proper extent of the
    alert at that time.  If you do not specify the time, you should get the
    total inclusion of any zones/counties that were added to the alert.
    """
    now = utc()
    desc["arguments"] = [
        dict(
            type="select",
            name="res",
            default="twitter",
            label="Output Image Resolution",
            options=PDICT,
        ),
        dict(
            optional=True,
            type="datetime",
            name="valid",
            default=now.strftime("%Y/%m/%d %H%M"),
            label="UTC Timestamp (inclusive) to plot the given alert at:",
            min="1986/01/01 0000",
        ),
        dict(
            type="networkselect",
            name="wfo",
            network="WFO",
            default="DMX",
            label="Select WFO:",
        ),
        dict(type="year", min=1986, default=2019, name="year", label="Year"),
        dict(
            type="vtec_ps",
            name="v",
            default="SV.W",
            label="VTEC Phenomena and Significance",
        ),
        dict(
            type="int",
            default=1,
            label="VTEC Event Identifier / Sequence Number",
            name="etn",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("postgis")
    ctx = get_autoplot_context(fdict, get_description())
    utcvalid = ctx.get("valid")
    wfo = ctx["wfo"]
    tzname = ctx["_nt"].sts[wfo]["tzname"]
    p1 = ctx["phenomenav"][:2]
    s1 = ctx["significancev"][:1]
    etn = int(ctx["etn"])
    year = int(ctx["year"])

    table = "warnings_%s" % (year,)
    df = read_postgis(
        """
        SELECT w.ugc, simple_geom, u.name,
        issue at time zone 'UTC' as issue,
        expire at time zone 'UTC' as expire,
        init_expire at time zone 'UTC' as init_expire,
        1 as val,
        status, is_emergency
        from """
        + table
        + """ w JOIN ugcs u on (w.gid = u.gid)
        WHERE w.wfo = %s and eventid = %s and significance = %s and
        phenomena = %s ORDER by issue ASC
    """,
        pgconn,
        params=(wfo[-3:], etn, s1, p1),
        index_col="ugc",
        geom_col="simple_geom",
    )
    if df.empty:
        raise NoDataFound("VTEC Event was not found, sorry.")
    table = "sbw_%s" % (year,)
    sbwdf = read_postgis(
        """
        SELECT status, geom,
        polygon_begin at time zone 'UTC' as polygon_begin,
        polygon_end at time zone 'UTC' as polygon_end
        from """
        + table
        + """
        WHERE wfo = %s and eventid = %s and significance = %s and
        phenomena = %s ORDER by polygon_begin ASC
    """,
        pgconn,
        params=(wfo[-3:], etn, s1, p1),
        geom_col="geom",
    )

    if utcvalid is None:
        utcvalid = df["issue"].max()
    else:
        # hack for an assumption below
        utcvalid = pd.Timestamp(utcvalid.replace(tzinfo=None))

    def m(valid):
        """Convert to our local timestamp."""
        return (
            valid.tz_localize(pytz.UTC)
            .astimezone(pytz.timezone(tzname))
            .strftime(TFORMAT)
        )

    df["color"] = vtec.NWS_COLORS.get("%s.%s" % (p1, s1), "#FF0000")
    if not sbwdf.empty:
        df["color"] = "tan"
    bounds = df["simple_geom"].total_bounds
    buffer = 0.4
    mp = MapPlot(
        subtitle="Map Valid: %s, Event: %s to %s"
        % (m(utcvalid), m(df["issue"].min()), m(df["expire"].max())),
        title="%s %s %s %s (%s.%s) #%s"
        % (
            year,
            wfo,
            vtec.VTEC_PHENOMENA.get(p1, p1),
            (
                "Emergency"
                if True in df["is_emergency"].values
                else vtec.VTEC_SIGNIFICANCE.get(s1, s1)
            ),
            p1,
            s1,
            etn,
        ),
        sector="custom",
        west=bounds[0] - buffer,
        south=bounds[1] - buffer,
        east=bounds[2] + buffer,
        north=bounds[3] + buffer,
        nocaption=True,
        figsize=(12.00, 6.28) if ctx["res"] == "twitter" else None,
    )
    mp.sector = "cwa"
    mp.cwa = wfo[-3:]
    # CAN statements come here with time == expire :/
    df2 = df[(df["issue"] <= utcvalid) & (df["expire"] > utcvalid)]
    if df2.empty:
        mp.ax.text(
            0.5,
            0.5,
            "Event No Longer Active",
            zorder=1000,
            transform=mp.ax.transAxes,
            fontsize=24,
            ha="center",
        )
    else:
        mp.fill_ugcs(
            df2["val"].to_dict(),
            color=df2["color"].to_dict(),
            nocbar=True,
            labels=df2["name"].to_dict(),
            missingval="",
            ilabel=(len(df2.index) <= 10),
            labelbuffer=5,
        )
    if not sbwdf.empty:
        color = vtec.NWS_COLORS.get("%s.%s" % (p1, s1), "#FF0000")
        poly = sbwdf.iloc[0]["geom"]
        df2 = sbwdf[
            (sbwdf["polygon_begin"] <= utcvalid)
            & (sbwdf["polygon_end"] > utcvalid)
        ]
        if not df2.empty:
            # draw new
            mp.ax.add_geometries(
                [poly],
                ccrs.PlateCarree(),
                facecolor="None",
                edgecolor="k",
                zorder=Z_OVERLAY2 - 1,
            )
            poly = df2.iloc[0]["geom"]
        mp.ax.add_geometries(
            [poly],
            ccrs.PlateCarree(),
            facecolor=color,
            alpha=0.5,
            edgecolor="k",
            zorder=Z_OVERLAY2,
        )
    if len(df.index) > 10:
        mp.drawcities()
    return mp.fig, df.drop("simple_geom", axis=1)


if __name__ == "__main__":
    plotter(
        dict(
            phenomenav="SV",
            significancev="W",
            wfo="DMX",
            valid="2019-04-11 0000",
            year=2019,
            etn=1,
        )
    )
