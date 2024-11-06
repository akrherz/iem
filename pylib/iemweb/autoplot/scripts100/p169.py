"""
This chart presents the largest change in some observed variable
over a given number of hours.  This is based on available
reports.  There are two options for how to compute the
change over a given window.</p>

<p><table class="table table-striped">
<thead><tr><th>Label</th><th>Description</th></tr></thead>
<tbody>
<tr><td>Compute at ends of time window</td><td>This requires an exact
match between the starting timestamp and ending timestamp of the given
window of time.  For example, computing a 12 hour change between exactly
6:53 AM and 6:53 PM.</td></tr>
<tr><td>Compute over time window</td><td>This is more forgiving and
considers the observation at the start of the window and then any
subsequent observation over the window of time.  The end of the
window is inclusive as well.</td></tr>
</tbody>
</table></p>

<p><strong>Note:</strong>  This app is very effective at finding bad data
points as the spark-line plot of the data for the given period will look
flakey.</p>

<p><a href="/plotting/auto/?q=139">Autoplot 139</a> is similar to this
plot, but only considers a calendar day.</p>
"""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context
from sqlalchemy import text

MDICT = {"warm": "Rise", "cool": "Drop"}
MDICT2 = {
    "all": "No Month/Time Limit",
    "spring": "Spring (MAM)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}
PDICT = {
    "exact": "Compute at ends of time window",
    "over": "Compute over time window",
}
PDICT2 = {
    "tmpf": "Air Temperature",
    "dwpf": "Dew Point Temperature",
    "feel": "Feels Like Temperature",
    "alti": "Pressure Altimeter",
    "mslp": "Sea Level Pressure",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            label="Select Station:",
            network="IA_ASOS",
        ),
        {
            "type": "select",
            "options": PDICT2,
            "default": "tmpf",
            "label": "Select Variable",
            "name": "v",
        },
        dict(type="int", name="hours", label="Number of Hours:", default=24),
        dict(
            type="select",
            name="month",
            default="all",
            label="Month Limiter",
            options=MDICT2,
        ),
        dict(
            type="select",
            name="dir",
            default="warm",
            label="Direction:",
            options=MDICT,
        ),
        dict(
            type="select",
            name="how",
            default="exact",
            label="How to compute change over given time window:",
            options=PDICT,
        ),
    ]
    return desc


def plot_event(ax, i, df, varname):
    """plot date."""
    df["norm"] = (df[varname] - df[varname].min()) / (
        df[varname].max() - df[varname].min()
    )
    sts = df.index[0].to_pydatetime()
    df["xnorm"] = [x.total_seconds() for x in (df.index.to_pydatetime() - sts)]

    lp = ax.plot(df["xnorm"], df["norm"] + i)
    ax.text(
        df["xnorm"].values[-1],
        df["norm"].values[-1] + i,
        sts.strftime("%-d %b %Y"),
        va="center",
        color=lp[0].get_color(),
    )


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    hours = ctx["hours"]
    mydir = ctx["dir"]
    month = ctx["month"]
    varname = ctx["v"]
    if varname not in PDICT2:
        raise NoDataFound("Invalid varname")

    if month == "all":
        months = range(1, 13)
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "summer":
        months = [6, 7, 8]
    else:
        ts = datetime.strptime(f"2000-{month}-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [
            ts.month,
        ]

    tzname = ctx["_nt"].sts[station]["tzname"]
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")

    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            text(
                f"""
            SELECT valid at time zone 'UTC' as utc_valid, {varname}
            from alldata where station = :station
            and {varname} is not null
            ORDER by valid desc
        """
            ),
            conn,
            params={
                "station": station,
            },
            index_col="utc_valid",
        )
    if df.empty:
        raise NoDataFound("No database entries found for station, sorry!")
    # Filter if needed
    if len(months) < 12:
        df["month"] = df.index.month
        df = df[df["month"].isin(months)]

    # Create offset for exact aggregate
    deltacol = f"{varname}_max" if ctx["dir"] == "warm" else f"{varname}_min"
    compcol = f"{varname}_min" if ctx["dir"] == "warm" else f"{varname}_max"
    if ctx["how"] == "exact":
        df = df.reset_index()
        # Create timestamp to look for second tmpf value
        df["end_valid"] = df["utc_valid"] + timedelta(hours=hours)
        # Inner Join
        df = (
            df.merge(
                df,
                left_on="end_valid",
                right_on="utc_valid",
                how="left",
                suffixes=("", "2"),
            )
            .drop(columns=["utc_valid2", "end_valid2"])
            .rename(columns={f"{varname}2": deltacol})
            .set_index("utc_valid")
        )
        # Careful here that our delta is the right sign
        if ctx["dir"] == "warm":
            df["delta"] = df[deltacol] - df[varname]
        else:
            df["delta"] = df[varname] - df[deltacol]
        events = df.sort_values("delta", ascending=False).head(500).copy()
    else:  # "over"
        # Create aggregate
        gdf = df.rolling(f"{hours}h", closed="both").agg(["max", "min"])
        gdf.columns = ["_".join(col) for col in gdf.columns.values]
        df = df.join(gdf)
        if df.index[0] < df.index[-1]:
            df = df.iloc[::-1]
        df["delta"] = (df[varname] - df[deltacol]).abs()
        # Only consider cases when current val equals extremum
        events = (
            df[df[varname] == df[compcol]]
            .sort_values("delta", ascending=False)
            .head(100)
            .copy()
        )

    hlabel = "Over Exactly" if ctx["how"] == "exact" else "Within"
    title = (
        f"{ctx['_sname']}:: Top 10 {PDICT2[varname]} {MDICT[mydir]}\n"
        f"{hlabel} {hours} Hour Period ({ab.year}-{date.today().year}) "
        f"[{MDICT2[month]}]"
    )
    fig = figure(title=title, apctx=ctx)
    ax = fig.add_axes((0.35, 0.1, 0.25, 0.8))

    sparkax = fig.add_axes((0.65, 0.1, 0.22, 0.8))

    labels = []
    used = []
    events["use"] = 0
    # workaround dups from above
    for valid, row in events.iterrows():
        # Construct time period with data
        sts = valid
        ets = valid + timedelta(hours=hours) + timedelta(minutes=1)
        # Ensure we have no used these before
        hit = False
        for use in used:
            if use[0] <= ets and use[1] >= sts:
                hit = True
                break
        if hit:
            continue
        used.append([sts, ets])
        event = df.loc[ets:sts].iloc[::-1]
        if ctx["how"] == "over":
            # Need to figure out first row with the ob we want
            entry = event[event[varname] == row[deltacol]]
            ets = entry.index[0].to_pydatetime()
        else:
            ets -= timedelta(minutes=1)
        events.at[valid, "use"] = 1
        events.at[valid, "start_valid_utc"] = sts
        events.at[valid, "end_valid_utc"] = ets
        # Allow the output to contain more data
        if len(labels) >= 10:
            continue
        sts = sts.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo(tzname))
        ets = ets.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo(tzname))
        if varname in ["alti", "mslp"]:
            lbl = (
                f"{row[varname]:.2f} to {row[deltacol]:.2f} -> "
                f"{row['delta']:.2f}\n"
                f"{sts:%-d %b %Y %-I:%M %p} - {ets:%-d %b %Y %-I:%M %p}"
            )
        else:
            lbl = (
                f"{row[varname]:.0f} to {row[deltacol]:.0f} -> "
                f"{row['delta']:.0f}\n"
                f"{sts:%-d %b %Y %-I:%M %p} - {ets:%-d %b %Y %-I:%M %p}"
            )
        labels.append(lbl)
        ax.barh(len(labels), row["delta"], color="b", align="center")
        plot_event(sparkax, 11 - len(labels), event.copy(), varname)

    sparkax.set_ylim(1, 11)
    sparkax.axis("off")

    ax.set_yticks(range(1, len(labels) + 1))
    ax.set_yticklabels(labels)
    ax.set_ylim(10.5, 0.5)
    ax.grid(True)
    units = {
        "tmpf": "Delta Degrees Fahrenheit",
        "dwpf": "Delta Degrees Fahrenheit",
        "feel": "Delta Degrees Fahrenheit",
        "alti": "Altimeter Change [inch]",
        "mslp": "Sea Level Pressure Change [mb]",
    }
    ax.set_xlabel(units.get(varname))
    return fig, (
        events[events["use"] == 1]
        .reset_index()
        .drop(columns=["utc_valid", "end_valid", "use"], errors="ignore")
    )
