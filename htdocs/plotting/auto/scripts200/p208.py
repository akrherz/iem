"""A fancy pants plot of a given VTEC headline."""
# local
from datetime import timezone

# third party
import pandas as pd
from geopandas import read_postgis
from pyiem.nws import vtec
from pyiem.plot.geoplot import MapPlot
from pyiem.util import get_autoplot_context, get_dbconn, utc
from pyiem.exceptions import NoDataFound
from pyiem.reference import Z_OVERLAY2, Z_OVERLAY2_LABEL, LATLON
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


def proxy(mp):
    """TODO removeme once pyiem updates"""
    if hasattr(mp, "panels"):
        return mp.panels[0]
    return mp.ax


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["cache"] = 300
    desc["data"] = True
    desc[
        "description"
    ] = """This application generates a map showing the coverage of a given
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
    pgconn = get_dbconn("postgis")
    ctx = get_autoplot_context(fdict, get_description())
    utcvalid = ctx.get("valid")
    wfo = ctx["wfo"]
    tzname = ctx["_nt"].sts[wfo]["tzname"]
    p1 = ctx["phenomenav"][:2]
    s1 = ctx["significancev"][:1]
    etn = int(ctx["etn"])
    year = int(ctx["year"])

    df = read_postgis(
        f"""
        SELECT w.ugc, simple_geom, u.name,
        issue at time zone 'UTC' as issue,
        expire at time zone 'UTC' as expire,
        init_expire at time zone 'UTC' as init_expire,
        1 as val,
        status, is_emergency, is_pds, w.wfo
        from warnings_{year} w JOIN ugcs u on (w.gid = u.gid)
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
    if ctx["opt"] == "expand":
        # Get all phenomena coincident with the above alert
        df = read_postgis(
            f"""
            SELECT w.ugc, simple_geom, u.name,
            issue at time zone 'UTC' as issue,
            expire at time zone 'UTC' as expire,
            init_expire at time zone 'UTC' as init_expire,
            1 as val,
            status, is_emergency, is_pds, w.wfo
            from warnings_{year} w JOIN ugcs u on (w.gid = u.gid)
            WHERE significance = %s and
            phenomena = %s and issue < %s and expire > %s
            ORDER by issue ASC
        """,
            pgconn,
            params=(s1, p1, df["expire"].min(), df["issue"].min()),
            index_col="ugc",
            geom_col="simple_geom",
        )
    elif ctx["opt"] == "etn":
        # Get all phenomena coincident with the above alert
        df = read_postgis(
            f"""
            SELECT w.ugc, simple_geom, u.name,
            issue at time zone 'UTC' as issue,
            expire at time zone 'UTC' as expire,
            init_expire at time zone 'UTC' as init_expire,
            1 as val,
            status, is_emergency, is_pds, w.wfo
            from warnings_{year} w JOIN ugcs u on (w.gid = u.gid)
            WHERE significance = %s and
            phenomena = %s and eventid = %s
            ORDER by issue ASC
        """,
            pgconn,
            params=(s1, p1, etn),
            index_col="ugc",
            geom_col="simple_geom",
        )

    sbwdf = read_postgis(
        f"""
        SELECT status, geom, wfo,
        polygon_begin at time zone 'UTC' as polygon_begin,
        polygon_end at time zone 'UTC' as polygon_end from sbw_{year}
        WHERE wfo = %s and eventid = %s and significance = %s and
        phenomena = %s ORDER by polygon_begin ASC
    """,
        pgconn,
        params=(wfo[-3:], etn, s1, p1),
        geom_col="geom",
    )
    if not sbwdf.empty and ctx["opt"] == "expand":
        # Get all phenomena coincident with the above alert
        sbwdf = read_postgis(
            f"""
            SELECT status, geom, wfo,
            polygon_begin at time zone 'UTC' as polygon_begin,
            polygon_end at time zone 'UTC' as polygon_end from sbw_{year}
            WHERE status = 'NEW' and significance = %s and
            phenomena = %s and issue < %s and expire > %s
            ORDER by polygon_begin ASC
        """,
            pgconn,
            params=(s1, p1, df["expire"].min(), df["issue"].min()),
            geom_col="geom",
        )
    elif not sbwdf.empty and ctx["opt"] == "etn":
        # Get all phenomena coincident with the above alert
        sbwdf = read_postgis(
            f"""
            SELECT status, geom, wfo,
            polygon_begin at time zone 'UTC' as polygon_begin,
            polygon_end at time zone 'UTC' as polygon_end from sbw_{year}
            WHERE status = 'NEW' and significance = %s and
            phenomena = %s and eventid = %s
            ORDER by polygon_begin ASC
        """,
            pgconn,
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

    df["color"] = vtec.NWS_COLORS.get("%s.%s" % (p1, s1), "#FF0000")
    if not sbwdf.empty:
        df["color"] = "tan"
    if len(df["wfo"].unique()) == 1:
        bounds = df["simple_geom"].total_bounds
        if not sbwdf.empty:
            bounds = sbwdf["geom"].total_bounds
    else:
        df2 = df[~df["wfo"].isin(["AJK", "AFC", "AFG", "HFO", "JSJ"])]
        bounds = df2["simple_geom"].total_bounds
    buffer = 0.4
    title = "%s %s %s%s %s (%s.%s) #%s" % (
        year,
        wfo,
        vtec.VTEC_PHENOMENA.get(p1, p1),
        " (PDS) " if True in df["is_pds"].values else "",
        (
            "Emergency"
            if True in df["is_emergency"].values
            else vtec.VTEC_SIGNIFICANCE.get(s1, s1)
        ),
        p1,
        s1,
        etn,
    )
    if ctx["opt"] in ["expand", "etn"]:
        title = (
            f"{year} NWS {vtec.VTEC_PHENOMENA.get(p1, p1)} "
            f"{vtec.VTEC_SIGNIFICANCE.get(s1, s1)} ({p1}.{s1})"
        )
        if ctx["opt"] == "etn":
            title += f" #{etn}"
    mp = MapPlot(
        subtitle="Map Valid: %s, Event: %s to %s"
        % (m(utcvalid), m(df["issue"].min()), m(df["expire"].max())),
        title=title,
        sector="custom",
        west=bounds[0] - buffer,
        south=bounds[1] - buffer,
        east=bounds[2] + buffer,
        north=bounds[3] + buffer,
        nocaption=True,
        twitter=True,
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
        mp.fill_ugcs(
            df2["val"].to_dict(),
            color=df2["color"].to_dict(),
            nocbar=True,
            labels=df2["name"].to_dict(),
            missingval="",
            ilabel=(len(df2.index) <= 10),
            labelbuffer=5,
            is_firewx=(p1 == "FW"),
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
            proxy(mp).add_geometries(
                [poly],
                LATLON,
                facecolor="None",
                edgecolor="k",
                zorder=Z_OVERLAY2,
            )
            poly = df2.iloc[0]["geom"]
            proxy(mp).add_geometries(
                [poly],
                LATLON,
                facecolor=color,
                alpha=0.5,
                edgecolor="k",
                zorder=Z_OVERLAY2,
            )
    mp.drawcities(textsize=12, color="#fff", outlinecolor="#000")
    mp.drawcounties()
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
    return mp.fig, df.drop("simple_geom", axis=1)


if __name__ == "__main__":
    plotter(
        dict(
            phenomenav="HT",
            significancev="Y",
            wfo="HNX",
            year=2021,
            etn=10,
            valid="2021-09-08 1450",
        )
    )
