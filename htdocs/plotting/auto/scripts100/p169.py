"""x-hour temp change"""
from datetime import datetime, timedelta, date

import pytz
import pandas as pd
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from sqlalchemy import text

MDICT = {"warm": "Temperature Rise", "cool": "Temperature Drop"}
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


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This chart presents the largest changes in
    temperature over a given number of hours.  This is based on available
    temperature reports.  There are two options for how to compute the
    temperature change over a given window.</p>

    <p><table class="table table-striped">
    <thead><tr><th>Label</th><th>Description</th></tr></thead>
    <tbody>
    <tr><td>Compute at ends of time window</td><td>This requires an exact
    match between the starting timestamp and ending timestamp of the given
    window of time.  For example, computing a 12 hour change between exactly
    6:53 AM and 6:53 PM.</td></tr>
    <tr><td>Compute over time window/td><td>This is more forgiving and
    considers the observation at the start of the window and then any
    subsequent observation over the window of time.  The end of the
    window is inclusive as well.</td></tr>
    </tbody>
    </table></p>

    <p><strong>Note:</strong>  This app is very effective at finding bad data
    points as the spark-line plot of the data for the given period will look
    flakey.</p>
    """
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            label="Select Station:",
            network="IA_ASOS",
        ),
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


def plot_event(ax, i, df):
    """plot date."""
    df["norm"] = (df["tmpf"] - df["tmpf"].min()) / (
        df["tmpf"].max() - df["tmpf"].min()
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
                """
            SELECT valid at time zone 'UTC' as utc_valid, tmpf from alldata
            where station = :station and tmpf between -100 and 150
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
    deltacol = "tmpf_max" if ctx["dir"] == "warm" else "tmpf_min"
    compcol = "tmpf_min" if ctx["dir"] == "warm" else "tmpf_max"
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
                suffixes=("", "2"),
            )
            .drop(columns=["utc_valid2", "end_valid2"])
            .rename(columns={"tmpf2": deltacol})
            .set_index("utc_valid")
        )
        # Careful here that our delta is the right sign
        if ctx["dir"] == "warm":
            df["delta"] = df[deltacol] - df["tmpf"]
        else:
            df["delta"] = df["tmpf"] - df[deltacol]
        events = df.sort_values("delta", ascending=False).head(100)
    elif ctx["how"] == "over":
        # Create aggregate
        gdf = df.rolling(f"{hours}h", closed="both").agg(["max", "min"])
        gdf.columns = ["_".join(col) for col in gdf.columns.values]
        df = df.join(gdf)
        df["delta"] = (df["tmpf"] - df[deltacol]).abs()
        # Only consider cases when current val equals extremum
        events = (
            df[df["tmpf"] == df[compcol]]
            .sort_values("delta", ascending=False)
            .head(100)
        )

    hlabel = "Over Exactly" if ctx["how"] == "exact" else "Within"
    title = (
        f"{ctx['_sname']}:: Top 10 {MDICT[mydir]}\n"
        f"{hlabel} {hours} Hour Period ({ab.year}-{date.today().year}) "
        f"[{MDICT2[month]}]"
    )
    fig = figure(title=title, apctx=ctx)
    ax = fig.add_axes([0.35, 0.1, 0.25, 0.8])

    sparkax = fig.add_axes([0.65, 0.1, 0.22, 0.8])

    labels = []
    used = []
    # workaround dups from above
    for valid, row in events.iterrows():
        if len(labels) >= 10:
            break
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
            entry = event[event["tmpf"] == row[deltacol]]
            ets = entry.index[0].to_pydatetime()
        else:
            ets -= timedelta(minutes=1)
        sts = sts.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone(tzname))
        ets = ets.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone(tzname))
        lbl = (
            f"{row['tmpf']:.0f} to {row[deltacol]:.0f} -> {row['delta']:.0f}\n"
            f"{sts:%-d %b %Y %-I:%M %p} - {ets:%-d %b %Y %-I:%M %p}"
        )
        labels.append(lbl)
        ax.barh(len(labels), row["delta"], color="b", align="center")
        plot_event(sparkax, 11 - len(labels), event.copy())

    sparkax.set_ylim(1, 11)
    sparkax.axis("off")

    ax.set_yticks(range(1, 11))
    ax.set_yticklabels(labels)
    ax.set_ylim(10.5, 0.5)
    ax.grid(True)
    ax.set_xlabel("Delta Degrees Fahrenheit")
    return fig, df


if __name__ == "__main__":
    plotter(
        {
            "zstation": "EST",
            "network": "IA_ASOS",
            "hours": 12,
            "dir": "warm",
            "how": "over",
            "month": "spring",
        }
    )
