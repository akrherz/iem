"""MOS plot"""
import datetime

import psycopg2.extras
import numpy as np
import pandas as pd
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = {
    "NAM": "NAM (9 Dec 2008 - current)",
    "GFS": "GFS (16 Dec 2003 - current)",
    "ETA": "ETA (24 Feb 2002 - 9 Dec 2008)",
    "AVN": "AVN (1 Jun 2000 - 16 Dec 2003)",
}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This chart displays the combination of
    Model Output Statistics (MOS) forecasts and actual observations
    by the automated station the MOS forecast is for.  MOS is forecasting
    high and low temperatures over 12 hours periods, so these values are not
    actual calendar day high and low temperatures."""
    today = datetime.date.today()
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            label="Select Station:",
            network="IA_ASOS",
        ),
        dict(type="month", name="month", label="Select Month:", default=today.month),
        dict(
            type="year", name="year", label="Select Year:", default=today.year, min=2000
        ),
        dict(
            type="select",
            name="model",
            default="NAM",
            label="Select MOS Model:",
            options=PDICT,
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    asos_pgconn = get_dbconn("asos")
    acursor = asos_pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    mos_pgconn = get_dbconn("mos")
    mcursor = mos_pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["zstation"]
    year = ctx["year"]
    month = ctx["month"]
    model = ctx["model"]

    # Extract the range of forecasts for each day for approximately
    # the given month
    month1 = datetime.datetime(year, month, 1)
    sts = month1 - datetime.timedelta(days=7)
    ets = month1 + datetime.timedelta(days=32)
    mcursor.execute(
        """
    SELECT date(ftime),
    min(case when
        extract(hour from ftime at time zone 'UTC') = 12
        then n_x else null end) as min_morning,
    max(case when
        extract(hour from ftime at time zone 'UTC') = 12
        then n_x else null end) as max_morning,
    min(case when
        extract(hour from ftime at time zone 'UTC') = 0
        then n_x else null end) as min_afternoon,
    max(case when
        extract(hour from ftime at time zone 'UTC') = 0
        then n_x else null end) as max_afternoon
    from alldata WHERE station = %s and runtime BETWEEN %s and %s
    and model = %s GROUP by date
    """,
        ("K" + station, sts, ets, model),
    )

    mosdata = {}
    for row in mcursor:
        mosdata[row[0]] = {
            "morning": [
                row[1] if row[1] is not None else np.nan,
                row[2] if row[2] is not None else np.nan,
            ],
            "afternoon": [
                row[3] if row[3] is not None else np.nan,
                row[4] if row[4] is not None else np.nan,
            ],
        }

    # Go and figure out what the observations where for this month, tricky!
    acursor.execute(
        """
    SELECT date(valid),
    min(case when extract(hour from valid at time zone 'UTC') between 0 and 12
        then tmpf else null end) as morning_min,
    max(case when extract(hour from valid at time zone 'UTC') between 12 and 24
        then tmpf else null end) as afternoon_max
    from alldata WHERE station = %s and valid between %s and %s
    GROUP by date
    """,
        (station, sts, ets),
    )

    obs = {}
    for row in acursor:
        obs[row[0]] = {
            "min": row[1] if row[1] is not None else np.nan,
            "max": row[2] if row[2] is not None else np.nan,
        }
    htop = []
    hbottom = []
    ltop = []
    lbottom = []
    hobs = []
    lobs = []
    now = month1.date()
    days = []
    rows = []
    while now.month == month:
        days.append(now.day)
        lbottom.append(mosdata.get(now, {}).get("morning", [np.nan, np.nan])[0])
        ltop.append(mosdata.get(now, {}).get("morning", [np.nan, np.nan])[1])

        hbottom.append(mosdata.get(now, {}).get("afternoon", [np.nan, np.nan])[0])
        htop.append(mosdata.get(now, {}).get("afternoon", [np.nan, np.nan])[1])

        hobs.append(obs.get(now, {}).get("max", np.nan))
        lobs.append(obs.get(now, {}).get("min", np.nan))
        rows.append(
            dict(
                day=now,
                low_min=lbottom[-1],
                low_max=ltop[-1],
                high_min=hbottom[-1],
                high_max=htop[-1],
                high=hobs[-1],
                low=lobs[-1],
            )
        )
        now += datetime.timedelta(days=1)
    df = pd.DataFrame(rows)
    days = np.array(days)

    hbottom = np.ma.fix_invalid(hbottom)

    hobs = np.ma.fix_invalid(hobs)
    lobs = np.ma.fix_invalid(lobs)

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))

    ax.set_title(
        "[%s] %s Daily Temperatures\n%s Forecast MOS Range for %s"
        % (station, ctx["_nt"].sts[station]["name"], model, month1.strftime("%B %Y"))
    )
    arr = (df["high_max"] - df["high_min"]).values
    ax.bar(
        days + 0.1,
        arr,
        facecolor="pink",
        width=0.7,
        bottom=hbottom,
        zorder=1,
        alpha=0.5,
        label="Daytime High",
        align="center",
    )
    arr = (df["low_max"] - df["low_min"]).values
    ax.bar(
        days - 0.1,
        arr,
        facecolor="blue",
        width=0.7,
        bottom=df["low_min"].values,
        zorder=1,
        alpha=0.3,
        label="Morning Low",
        align="center",
    )

    ax.scatter(days + 0.1, hobs, zorder=2, s=40, c="red", label="Actual High")
    ax.scatter(days - 0.1, lobs, zorder=2, s=40, c="blue", label="Actual Low")

    ax.set_ylabel(r"Temperature $^{\circ}\mathrm{F}$")
    ax.grid(True)

    next1 = ets.replace(day=1)
    days = (next1 - month1).days
    ax.set_xlim(0, days + 0.5)
    ax.set_xticks(range(1, days + 1, 2))
    ax.set_xlabel("Day of %s" % (month1.strftime("%B %Y")))

    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])

    # Put a legend below current axis
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        fancybox=True,
        shadow=True,
        ncol=4,
        scatterpoints=1,
        fontsize=12,
    )

    return fig, df


if __name__ == "__main__":
    plotter(dict(network="TX_ASOS", zstation="AUS", month=1, year=2018))
