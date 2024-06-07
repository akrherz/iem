"""
<p>This autoplot attempts to estimate the number of people or area
in the US
under a given NWS Watch/Warning/Advisory (WaWA).  Double-accounting is
somewhat a problem here in the case of overlapping polygons. For each
WaWA type, if there are polygons associated with the event, the
population of the polygon intersection with the 30 arc-second grid is
used.</p>

<p>While the graphic only displays the top 10, the data download provides
everything available to be computed.</p>

<p><strong>Footnote on "Active" WaWA</strong>: A more complex than it
should be nuance to explain here is the concept of what is "active" at
a given timestamp.  Let us consider a real world example.  On Monday
afternoon, the NWS issues a Winter Storm Warning for an upcoming
storm that goes "into effect" at noon on Tuesday.  You request this
plot for a timestamp of 6 PM on that Monday.  Is the Winter Storm
Warning included in this metric at that time?
<ul>
<li>Yes, if you select the option to include any WaWA that have been
created, but may have an VTEC start time in the future yet.</li>
<li>No, if you select the option to only include WaWA that have an
issuance time before the given timestamp.</li>
</ul>
<br />The default setting here is the first option, to include any events
that have been created, but not necessarily having an issuance time prior
to the given timestamp.  This is why we can't have nice things!
</p>

<p><a href="/plotting/auto/?q=247">Autoplot 247</a> is closely related to
this app and provides a map of WaWa + stats.</p>
"""

from datetime import timezone
from zoneinfo import ZoneInfo

import pandas as pd
from matplotlib.patches import Rectangle
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.nws.vtec import NWS_COLORS, get_ps_string
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, utc
from sqlalchemy import text

PDICT = {
    "active": "Include WaWA that have been created or valid at the given time",
    "within": "Include WaWA with VTEC issuance time before the given time",
}
PDICT2 = {
    "pop": "Population",
    "area": "Area",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 120}
    desc["arguments"] = [
        dict(
            type="select",
            options=PDICT2,
            name="which",
            default="pop",
            label="Aggregate Population or Area",
        ),
        dict(
            type="datetime",
            name="valid",
            default=utc().strftime("%Y/%m/%d %H%M"),
            min="2005/10/01 0000",
            label="At Valid Timestamp:",
            optional=True,
        ),
        dict(
            type="select",
            name="opt",
            default="active",
            options=PDICT,
            label="How to consider if an event is active [see footnote]",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    if "valid" not in ctx:
        ctx["valid"] = utc()
    valid = ctx["valid"].replace(tzinfo=timezone.utc)

    isscol = "issue" if ctx["opt"] == "within" else "product_issue"
    popyear = int(valid.year - (valid.year % 5))
    col = "final_pop" if ctx["which"] == "pop" else "final_area_sqkm"
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(
                f"""
            with sbwpop as (
                select phenomena ||'.'|| significance as key,
                sum(population) as pop
                from sbw w, gpw{popyear} p
                WHERE ST_Contains(w.geom, p.geom) and
                polygon_begin <= :valid and polygon_end >= :valid
                GROUP by key ORDER by pop DESC
            ), sbwevents as (
                select phenomena ||'.'|| significance as key,
                count(*),
                sum(st_area(w.geom::geography) / 1e6) as area from sbw w
                WHERE polygon_begin <= :valid and polygon_end >= :valid
                GROUP by key
            ), sbwagg as (
                select p.key, p.pop, e.count as events, e.area
                from sbwpop p JOIN sbwevents e on (p.key = e.key)
            ), cbwpop as (
                select phenomena ||'.'|| significance as key,
                array_agg(distinct substr(w.ugc, 1, 2)) as states,
                sum(area2163) as area,
                sum(gpw_population_{popyear}) as pop, count(*) as events
                from warnings w JOIN ugcs u on (w.gid = u.gid)
                WHERE {isscol} <= :valid and expire >= :valid
                GROUP by key ORDER by pop DESC
            )
            select c.key, c.pop as zone_pop, s.pop as poly_pop, c.states,
            c.area as zone_area_sqkm, s.area as poly_area_sqkm,
            c.events as zone_events, coalesce(s.events, 0) as poly_events,
            (case when s.pop is not null then s.pop else c.pop end)
                as final_pop,
            (case when s.area is not null then s.area else c.area end)
                as final_area_sqkm
            from cbwpop c LEFT JOIN sbwagg s
            on (c.key = s.key) ORDER by {col} DESC
                """
            ),
            conn,
            params={"valid": valid},
            index_col="key",
        )
    if df.empty:
        raise NoDataFound("No WaWA data found at the given timestamp!")
    df["label"] = df.index.to_series().apply(
        lambda x: get_ps_string(*x.split("."))
    )
    df["states"] = df["states"].apply(" ".join)
    dt = valid.astimezone(ZoneInfo("America/Chicago")).strftime(
        "%Y-%m-%d %-I:%M %p %Z"
    )
    qualifier = "Active" if ctx["opt"] == "within" else "Created/Active"
    title = (
        f"{PDICT2[ctx['which']]} under {qualifier} "
        f"NWS Watch/Warning/Advisory @ {dt}"
    )
    subtitle = "Unofficial IEM Warning/Watch/Advisory data"
    if ctx["which"] == "pop":
        subtitle = f"Based on GPW {popyear} Population and {subtitle}"
    else:
        title = title.replace(" under ", "[sq km] under ")

    fig = figure(title=title, subtitle=subtitle, apctx=ctx)
    # add axes without any markups
    ax = fig.add_axes([0.0, 0.0, 1, 1], frame_on=False)
    ypos = 0.8
    xbarstart = 0.26
    xbarend = 0.85
    maxval = df[col].max()

    fig.text(xbarend + 0.03, ypos + 0.09, "Cnty/Zone\nEvents", ha="center")
    fig.text(xbarend + 0.07, ypos + 0.09, "Polygons")

    for key, row in df.head(10).iterrows():
        # A box around the entry
        rect = Rectangle((0.02, ypos - 0.001), 0.94, 0.08, ec="k", fc="w")
        ax.add_patch(rect)
        # Draw a rectange for each of the top 5
        color = NWS_COLORS.get(key, "#EEEEEE")
        # A simple abbrevation to start
        fig.text(0.03, ypos + 0.01, key, color=color, fontsize="xx-large")
        # A lablel above the top
        fig.text(0.03, ypos + 0.05, row["label"], fontsize="large")
        # The population number with commas
        fig.text(
            0.25,
            ypos + 0.01,
            f"{int(row[col]):,}",
            fontsize="x-large",
            ha="right",
        )
        # A bar in the color of the event
        xlen = row[col] / maxval * (xbarend - xbarstart)
        rect = Rectangle((xbarstart, ypos + 0.01), xlen, 0.03, facecolor=color)
        ax.add_patch(rect)

        # The states affected
        fig.text(
            xbarstart,
            ypos + 0.05,
            row["states"],
        )

        # Add columns for Zones
        fig.text(
            xbarend + 0.04,
            ypos + 0.01,
            f"{int(row['zone_events']):,}",
            ha="right",
        )
        fig.text(
            xbarend + 0.09,
            ypos + 0.01,
            f"{int(row['poly_events']):,}",
            ha="right",
        )

        ypos -= 0.08

    return fig, df


if __name__ == "__main__":
    plotter({})
