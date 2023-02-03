"""This application generates a map showing the coverage of a given
    VTEC alert.  The tricky part here is how time is handled
    for events whereby zones/counties can be added / removed from the alert.
    If you specific an exact time, you should get the proper extent of the
    alert at that time.  If you do not specify the time, you should get the
    total inclusion of any zones/counties that were added to the alert.

    <p>This plot can be run in three special modes, those are:
    <ul>
      <li><strong>Single Event</strong>: Plots for a given WFO and event id.
      </li>
      <li><strong>Same Phen/Sig over multiple WFOs</strong>: The given single
      event is expanded in space to cover any coincident events for the given
      single event.</li>
      <li><strong>Same Phen/Sig over multiple WFOs</strong>: In this case, the
      event id is used to expand the plot.  This makes most sense for SVR + TOR
      watches along with Tropical Alerts as the same event id is used over
      multiple WFOs.</li>
    </ul>
    </p>
"""
# local
from datetime import timezone

# third party
import pandas as pd
import geopandas as gpd
from sqlalchemy import text
from pyiem.nws import vtec
from pyiem.plot.geoplot import MapPlot
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, utc
from pyiem.exceptions import NoDataFound
from pyiem.reference import Z_OVERLAY2, Z_OVERLAY2_LABEL, LATLON, Z_FILL
import pytz

TFORMAT = "%b %-d %Y %-I:%M %p %Z"
PDICT = {
    "single": "Plot just this single VTEC Event",
    "expand": "Plot same VTEC Phenom/Sig from any WFO coincident with event",
    "etn": "Plot same VTEC Phenom/Sig + Event ID from any WFO",
}
PDICT3 = {
    "on": "Overlay NEXRAD Mosaic",
    "auto": "Let autoplot decide when to include NEXRAD overlay",
    "off": "No NEXRAD Mosaic Please",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "cache": 300, "data": True}
    desc["defaults"] = {"_r": "t"}
    now = utc()
    desc["arguments"] = [
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
        dict(
            type="select",
            default="single",
            name="opt",
            options=PDICT,
            label="Special Plot Options / Modes",
        ),
        dict(
            type="select",
            options=PDICT3,
            default="auto",
            name="n",
            label="Should a NEXRAD Mosaic be overlain:",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    utcvalid = ctx.get("valid")
    wfo = ctx["wfo"]
    if wfo == "NHC":
        ctx["opt"] = "expand"
    tzname = ctx["_nt"].sts[wfo]["tzname"]
    p1 = ctx["phenomenav"][:2]
    s1 = ctx["significancev"][:1]
    etn = int(ctx["etn"])
    year = int(ctx["year"])
    params = {
        "wfo": wfo[-3:],
        "etn": etn,
        "s1": s1,
        "p1": p1,
    }
    with get_sqlalchemy_conn("postgis") as conn:
        wfolim = "w.wfo = :wfo and" if wfo != "NHC" else ""
        df = gpd.read_postgis(
            text(
                f"""
            SELECT w.ugc, simple_geom, u.name,
            issue at time zone 'UTC' as issue,
            expire at time zone 'UTC' as expire,
            init_expire at time zone 'UTC' as init_expire,
            1 as val,
            status, is_emergency, is_pds, w.wfo
            from warnings_{year} w JOIN ugcs u on (w.gid = u.gid)
            WHERE {wfolim} eventid = :etn and significance = :s1 and
            phenomena = :p1 ORDER by issue ASC
        """
            ),
            conn,
            params=params,
            index_col="ugc",
            geom_col="simple_geom",
        )
    if df.empty:
        raise NoDataFound("VTEC Event was not found, sorry.")
    if ctx["opt"] == "expand":
        # Get all phenomena coincident with the above alert
        with get_sqlalchemy_conn("postgis") as conn:
            df = gpd.read_postgis(
                f"""
                SELECT w.ugc, simple_geom, u.name,
                issue at time zone 'UTC' as issue,
                expire at time zone 'UTC' as expire,
                init_expire at time zone 'UTC' as init_expire,
                status, is_emergency, is_pds, w.wfo
                from warnings_{year} w JOIN ugcs u on (w.gid = u.gid)
                WHERE significance = %s and
                phenomena = %s and issue < %s and expire > %s
                ORDER by issue ASC
            """,
                conn,
                params=(s1, p1, df["expire"].min(), df["issue"].min()),
                index_col="ugc",
                geom_col="simple_geom",
            )
    elif ctx["opt"] == "etn":
        # Get all phenomena coincident with the above alert
        with get_sqlalchemy_conn("postgis") as conn:
            df = gpd.read_postgis(
                f"""
                SELECT w.ugc, simple_geom, u.name,
                issue at time zone 'UTC' as issue,
                expire at time zone 'UTC' as expire,
                init_expire at time zone 'UTC' as init_expire,
                status, is_emergency, is_pds, w.wfo
                from warnings_{year} w JOIN ugcs u on (w.gid = u.gid)
                WHERE significance = %s and
                phenomena = %s and eventid = %s
                ORDER by issue ASC
            """,
                conn,
                params=(s1, p1, etn),
                index_col="ugc",
                geom_col="simple_geom",
            )
    if df.empty:
        raise NoDataFound("VTEC Event was not found, sorry.")
    with get_sqlalchemy_conn("postgis") as conn:
        sbwdf = gpd.read_postgis(
            f"""
            SELECT status, geom, wfo,
            polygon_begin at time zone 'UTC' as polygon_begin,
            polygon_end at time zone 'UTC' as polygon_end from sbw_{year}
            WHERE wfo = %s and eventid = %s and significance = %s and
            phenomena = %s ORDER by polygon_begin ASC
        """,
            conn,
            params=(wfo[-3:], etn, s1, p1),
            geom_col="geom",
        )
    if not sbwdf.empty and ctx["opt"] == "expand":
        # Get all phenomena coincident with the above alert
        with get_sqlalchemy_conn("postgis") as conn:
            sbwdf = gpd.read_postgis(
                f"""
                SELECT status, geom, wfo,
                polygon_begin at time zone 'UTC' as polygon_begin,
                polygon_end at time zone 'UTC' as polygon_end from sbw_{year}
                WHERE status = 'NEW' and significance = %s and
                phenomena = %s and issue < %s and expire > %s
                ORDER by polygon_begin ASC
            """,
                conn,
                params=(s1, p1, df["expire"].min(), df["issue"].min()),
                geom_col="geom",
            )
    elif not sbwdf.empty and ctx["opt"] == "etn":
        # Get all phenomena coincident with the above alert
        with get_sqlalchemy_conn("postgis") as conn:
            sbwdf = gpd.read_postgis(
                f"""
                SELECT status, geom, wfo,
                polygon_begin at time zone 'UTC' as polygon_begin,
                polygon_end at time zone 'UTC' as polygon_end from sbw_{year}
                WHERE status = 'NEW' and significance = %s and
                phenomena = %s and eventid = %s
                ORDER by polygon_begin ASC
            """,
                conn,
                params=(s1, p1, etn),
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

    df["color"] = vtec.NWS_COLORS.get(f"{p1}.{s1}", "#FF0000") + "D0"
    if not sbwdf.empty:
        df["color"] = "#D2B48CD0"
    if len(df["wfo"].unique()) == 1:
        bounds = df["simple_geom"].total_bounds
        if not sbwdf.empty:
            bounds = sbwdf["geom"].total_bounds
    else:
        df2 = df[~df["wfo"].isin(["AJK", "AFC", "AFG", "HFO", "JSJ"])]
        bounds = df2["simple_geom"].total_bounds
    buffer = 0.4
    _pds = " (PDS) " if True in df["is_pds"].values else ""
    _tt = (
        "Emergency"
        if True in df["is_emergency"].values
        else vtec.VTEC_SIGNIFICANCE.get(s1, s1)
    )
    title = (
        f"{year} {wfo} {vtec.VTEC_PHENOMENA.get(p1, p1)}{_pds} {_tt} "
        f"({p1}.{s1}) #{etn}"
    )
    if ctx["opt"] in ["expand", "etn"]:
        title = (
            f"{year} NWS {vtec.VTEC_PHENOMENA.get(p1, p1)} "
            f"{vtec.VTEC_SIGNIFICANCE.get(s1, s1)} ({p1}.{s1})"
        )
        if ctx["opt"] == "etn":
            title += f" #{etn}"
    mp = MapPlot(
        apctx=ctx,
        subtitle=(
            f"Map Valid: {m(utcvalid)}, Event: {m(df['issue'].min())} "
            f"to {m(df['expire'].max())}"
        ),
        title=title,
        sector="spherical_mercator",
        west=bounds[0] - buffer,
        south=bounds[1] - buffer,
        east=bounds[2] + buffer,
        north=bounds[3] + buffer,
        nocaption=True,
    )
    if len(df["wfo"].unique()) == 1 and wfo not in ["PHEB", "PAAQ"]:
        mp.sector = "cwa"
        mp.cwa = wfo[-3:]
    # CAN statements come here with time == expire :/
    if ctx["opt"] == "single":
        df2 = df[(df["issue"] <= utcvalid) & (df["expire"] > utcvalid)]
    else:
        df2 = df
    if df2.empty:
        mp.ax.text(
            0.5,
            0.5,
            "Event No Longer Active",
            zorder=1000,
            transform=mp.ax.transAxes,
            fontsize=24,
            bbox=dict(color="white"),
            ha="center",
        )
    else:
        # We have the geometries already, so can't we just use them?
        # The issue is that pyiem doesn't really support zones changes
        (
            df2.to_crs(mp.panels[0].crs).plot(
                ax=mp.panels[0].ax,
                aspect=None,
                ec="white",
                fc=df2["color"].values,
                zorder=Z_FILL,
            )
        )

    if not sbwdf.empty:
        color = vtec.NWS_COLORS.get(f"{p1}.{s1}", "#FF0000")
        poly = sbwdf.iloc[0]["geom"]
        df2 = sbwdf[
            (sbwdf["polygon_begin"] <= utcvalid)
            & (sbwdf["polygon_end"] > utcvalid)
        ]
        if not df2.empty:
            # draw new
            mp.panels[0].add_geometries(
                [poly],
                LATLON,
                facecolor="None",
                edgecolor="k",
                zorder=Z_OVERLAY2,
            )
            poly = df2.iloc[0]["geom"]
            mp.panels[0].add_geometries(
                [poly],
                LATLON,
                facecolor=color,
                alpha=0.5,
                edgecolor="k",
                zorder=Z_OVERLAY2,
            )
    if ctx["n"] != "off":
        if (p1 in ["SV", "TO", "FF", "MA"] and s1 == "W") or ctx["n"] == "on":
            radval = mp.overlay_nexrad(
                utcvalid.to_pydatetime().replace(tzinfo=timezone.utc),
                caxpos=(0.02, 0.07, 0.3, 0.005),
            )
            if radval is not None:
                tstamp = radval.astimezone(pytz.timezone(tzname)).strftime(
                    "%-I:%M %p"
                )
                mp.ax.text(
                    0.01,
                    0.99,
                    f"NEXRAD: {tstamp}",
                    transform=mp.ax.transAxes,
                    bbox=dict(color="white"),
                    va="top",
                    zorder=Z_OVERLAY2_LABEL + 100,
                )
    mp.fill_cwas(
        {"HFO": 0},
        ec="green",
        fc="None",
        plotmissing=True,
        draw_colorbar=False,
        lw=2,
    )
    return mp.fig, df.drop("simple_geom", axis=1)


if __name__ == "__main__":
    plotter(
        dict(
            phenomenav="TO",
            significancev="W",
            wfo="PAH",
            year=2019,
            etn=1,
            valid="2021-12-11 0339",
            network="WFO",
            opt="expand",
            n="auto",
        )
    )
