"""This chart displays the combination of
    Model Output Statistics (MOS) forecasts and actual observations
    by the automated station the MOS forecast is for.  MOS is forecasting
    high and low temperatures over 12 hours periods, so these values are not
    actual calendar day high and low temperatures.

<p>The bars represent the ensemble of previously made forecasts valid for the
given time.

<p><strong>Updated 9 Feb 2023</strong> The data download columns names were
changed to be more explicit about what is being presented.
"""
import datetime

import numpy as np
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.ticker import AutoMinorLocator, MaxNLocator
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn

PDICT = {
    "NAM": "NAM (9 Dec 2008 - current)",
    "GFS": "GFS (16 Dec 2003 - current)",
    "LAV": "GFS LAMP (23 Jul 2020 - current)",
    "MEX": "GFS Extended (12 Jul 2020 - current)",
    "NBE": "NBE (23 Jul 2020 - current)",
    "NBS": "NBS (23 Jul 2020 - current)",
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
        then coalesce(n_x, txn) else null end) as min_morning,
    max(case when
        extract(hour from ftime at time zone 'UTC') = 12
        then coalesce(n_x, txn) else null end) as max_morning,
    min(case when
        extract(hour from ftime at time zone 'UTC') = 0
        then coalesce(n_x, txn) else null end) as min_afternoon,
    max(case when
        extract(hour from ftime at time zone 'UTC') = 0
        then coalesce(n_x, txn) else null end) as max_afternoon
    from alldata WHERE station = %s and runtime BETWEEN %s and %s
    and model = %s and (txn is null or txn > -98) GROUP by date
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
    RPL from alldata where station = %s and valid between %s and %s
    and (extract(minute from valid) >= 50 or
         extract(minute from valid) < 10) and RPL is not null
    and report_type in (3, 4)
    """


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 3600}
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
    x = []
    now = datetime.datetime(month1.year, month1.month, month1.day)
    while now.month == month:
        x.append(now)
        bottom.append(mosdata.get(now, [np.nan, np.nan])[0])
        top.append(mosdata.get(now, [np.nan, np.nan])[1])
        _obs.append(obs.get(now, np.nan))
        now += datetime.timedelta(hours=6)
    df = pd.DataFrame(
        {
            "valid": pd.to_datetime(x),
            f"mos_min_{varname}": bottom,
            f"mos_max_{varname}": top,
            f"ob_{varname}": _obs,
        }
    )
    df["mos_delta"] = df[f"mos_max_{varname}"] - df[f"mos_min_{varname}"]
    if df[f"mos_min_{varname}"].isna().sum() == len(df.index):
        raise ValueError("No MOS data found for query.")

    ax.bar(
        df["valid"].values,
        df["mos_delta"].values,
        facecolor="pink",
        width=0.25,
        bottom=df[f"mos_min_{varname}"].values,
        label="Range",
        zorder=1,
        alpha=0.5,
        align="center",
    )
    ax.scatter(
        df["valid"],
        df[f"ob_{varname}"],
        zorder=2,
        s=40,
        c="red",
        label="Actual",
    )
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
    valid = []
    while now.month == month:
        valid.append(now)
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
        now += datetime.timedelta(days=1)
    df = pd.DataFrame(
        {
            "valid": pd.to_datetime(valid),
            "low_min": lbottom,
            "low_max": ltop,
            "high_min": hbottom,
            "high_max": htop,
            "high": hobs,
            "low": lobs,
        }
    )
    df["high_delta"] = df["high_max"] - df["high_min"]
    df["low_delta"] = df["low_max"] - df["low_min"]
    ax.bar(
        df["valid"].dt.day + 0.1,
        df["high_delta"],
        facecolor="pink",
        width=0.7,
        bottom=df["high_min"],
        zorder=1,
        alpha=0.5,
        label="Daytime High",
        align="center",
    )
    ax.bar(
        df["valid"].dt.day - 0.1,
        df["low_delta"],
        facecolor="blue",
        width=0.7,
        bottom=df["low_min"],
        zorder=1,
        alpha=0.3,
        label="Morning Low",
        align="center",
    )

    ax.scatter(
        df["valid"].dt.day + 0.1,
        df["high"],
        zorder=2,
        s=40,
        c="red",
        label="Actual High",
    )
    ax.scatter(
        df["valid"].dt.day - 0.1,
        df["low"],
        zorder=2,
        s=40,
        c="blue",
        label="Actual Low",
    )

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
    sts = month1 - datetime.timedelta(days=10)
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

    mlabel = PDICT[model][: PDICT[model].find(" (")]
    title = (
        f"{ctx['_sname']} :: {PDICT2[ctx['var']]}\n"
        f"{mlabel} Forecast MOS Range for {month1:%B %Y}"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)

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
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.tick_params(which="minor", color="tan")
    ax.grid(which="minor", axis="y", color="tan", linestyle="-.")

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
