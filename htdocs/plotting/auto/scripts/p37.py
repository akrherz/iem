"""MOS plot"""
import datetime

import numpy as np
import pandas as pd
import matplotlib.dates as mdates
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = {
    "NAM": "NAM (9 Dec 2008 - current)",
    "GFS": "GFS (16 Dec 2003 - current)",
    "ETA": "ETA (24 Feb 2002 - 9 Dec 2008)",
    "AVN": "AVN (1 Jun 2000 - 16 Dec 2003)",
}
PDICT2 = {
    "t": "12 Hour Max/Min Air Temperature [F]",
    "tmp": "Air Temperature [F]",
    "dpt": "Dew Point Temperature [F]",
    "wsp": "10 meter Wind Speed [kts]",
}
LOOKUP = {
    "dpt": "dwpf",
    "tmp": "tmpf",
    "wsp": "sknt",
}
T_SQL = """
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
    """
SQL = """
    SELECT ftime at time zone 'UTC', min(RPL), max(RPL)
    from alldata WHERE station = %s and runtime BETWEEN %s and %s
    and model = %s GROUP by ftime ORDER by ftime
    """
T_SQL_OB = """
    SELECT date(valid),
    min(case when extract(hour from valid at time zone 'UTC') between 0 and 12
        then tmpf else null end) as morning_min,
    max(case when extract(hour from valid at time zone 'UTC') between 12 and 24
        then tmpf else null end) as afternoon_max
    from alldata WHERE station = %s and valid between %s and %s
    GROUP by date
    """
SQL_OB = """
    select date_trunc('hour',
    valid at time zone 'UTC' + '10 minutes'::interval) as datum,
    avg(RPL) from alldata where station = %s and valid between %s and %s
    and extract(minute from valid) >= 50 and RPL is not null GROUP by datum
    """


def get_description():
    """Return a dict describing how to call this plotter"""
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
        dict(
            type="month",
            name="month",
            label="Select Month:",
            default=today.month,
        ),
        dict(
            type="year",
            name="year",
            label="Select Year:",
            default=today.year,
            min=2000,
        ),
        dict(
            type="select",
            name="model",
            default="NAM",
            label="Select MOS Model:",
            options=PDICT,
        ),
        dict(
            type="select",
            options=PDICT2,
            default="t",
            label="Which MOS variable to plot:",
            name="var",
        ),
    ]
    return desc


def plot_others(varname, ax, mosdata, month1, month, obs):
    """Non-Temp logic"""
    top = []
    bottom = []
    _obs = []
    now = datetime.datetime(month1.year, month1.month, month1.day)
    x = []
    rows = []
    while now.month == month:
        x.append(now)
        bottom.append(mosdata.get(now, [np.nan, np.nan])[0])
        top.append(mosdata.get(now, [np.nan, np.nan])[1])
        _obs.append(obs.get(now, np.nan))
        rows.append(
            dict(
                valid=now,
                min=bottom[-1],
                max=top[-1],
                dpt=_obs[-1],
            )
        )
        now += datetime.timedelta(hours=6)
    df = pd.DataFrame(rows)
    if df[~pd.isna(df["min"])].empty:
        raise ValueError("No MOS data found for query.")

    bottom = np.ma.fix_invalid(bottom)
    top = np.ma.fix_invalid(top)
    _obs = np.ma.fix_invalid(_obs)

    ax.bar(
        x,
        top - bottom,
        facecolor="pink",
        width=0.25,
        bottom=bottom,
        label="Range",
        zorder=1,
        alpha=0.5,
        align="center",
    )
    ax.scatter(x, _obs, zorder=2, s=40, c="red", label="Actual")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d"))
    ax.set_ylabel(PDICT2[varname])

    return df


def plot_temps(ax, mosdata, month1, month, obs):
    """Temp logic"""
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
        lbottom.append(
            mosdata.get(now, {}).get("morning", [np.nan, np.nan])[0]
        )
        ltop.append(mosdata.get(now, {}).get("morning", [np.nan, np.nan])[1])

        hbottom.append(
            mosdata.get(now, {}).get("afternoon", [np.nan, np.nan])[0]
        )
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

    next1 = now.replace(day=1)
    days = (next1 - month1.date()).days
    ax.set_xlim(0, days + 0.5)
    ax.set_xticks(range(1, days + 1, 2))

    ax.set_ylabel(r"Temperature $^{\circ}\mathrm{F}$")

    return df


def plotter(fdict):
    """Go"""
    asos_pgconn = get_dbconn("asos")
    acursor = asos_pgconn.cursor()
    mos_pgconn = get_dbconn("mos")
    mcursor = mos_pgconn.cursor()
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
    station4 = f"K{station}" if len(station) == 3 else station
    is_temp = ctx["var"] == "t"
    mcursor.execute(
        T_SQL if is_temp else SQL.replace("RPL", ctx["var"]),
        (station4, sts, ets, model),
    )

    mosdata = {}
    for row in mcursor:
        if is_temp:
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
        else:
            mosdata[row[0]] = [row[1], row[2]]

    # Go and figure out what the observations where for this month, tricky!
    acursor.execute(
        T_SQL_OB if is_temp else SQL_OB.replace("RPL", LOOKUP[ctx["var"]]),
        (station, sts, ets),
    )

    obs = {}
    for row in acursor:
        if is_temp:
            obs[row[0]] = {
                "min": row[1] if row[1] is not None else np.nan,
                "max": row[2] if row[2] is not None else np.nan,
            }
        else:
            obs[row[0]] = row[1]

    title = (
        f"[{station}] {ctx['_nt'].sts[station]['name']} {PDICT2[ctx['var']]}\n"
        f"{model} Forecast MOS Range for {month1:%B %Y}"
    )
    (fig, ax) = figure_axes(title=title)

    if is_temp:
        df = plot_temps(ax, mosdata, month1, month, obs)
    else:
        df = plot_others(ctx["var"], ax, mosdata, month1, month, obs)
    ax.set_xlabel(f"Day of {month1:%B %Y}")

    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position(
        [box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9]
    )

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
    ax.grid()

    return fig, df


if __name__ == "__main__":
    plotter(
        {
            "var": "t",
            "network": "IA_ASOS",
            "zstation": "DSM",
            "month": 10,
            "year": 2021,
        }
    )
