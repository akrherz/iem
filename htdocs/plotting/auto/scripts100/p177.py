"""ISU Soil Moisture Network Time Series"""
import datetime

import numpy as np
import psycopg2
import pytz
import pandas as pd
from pandas.io.sql import read_sql
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from pyiem import meteorology
from pyiem.plot.use_agg import plt
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_dbconn, c2f
from pyiem.exceptions import NoDataFound


PLOTTYPES = {
    "1": "3 Panel Plot",
    "2": "Just Soil Temps",
    "3": "Daily Max/Min 4 Inch Soil Temps",
    "4": "Daily Solar Radiation",
    "5": "Daily Potential Evapotranspiration",
    "6": "Histogram of Volumetric Soil Moisture",
    "7": "Daily Soil Water + Change",
    "8": "Battery Voltage",
    "9": "Daily Rainfall, 4 inch Soil Temp, and RH",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This application generates a series of chart types
    for data from the ISU Soil Moisture Network.
    """
    ets = datetime.datetime.now().replace(minute=0)
    sts = ets - datetime.timedelta(days=7)
    desc["arguments"] = [
        dict(
            type="networkselect",
            name="station",
            default="AEEI4",
            label="Select Station:",
            network="ISUSM",
        ),
        dict(
            type="select",
            name="opt",
            default="1",
            options=PLOTTYPES,
            label="Select Plot Type:",
        ),
        dict(
            type="datetime",
            name="sts",
            default=sts.strftime("%Y/%m/%d %H%M"),
            label="Start Time (Central Time):",
            min="2012/01/01 0000",
        ),
        dict(
            type="datetime",
            name="ets",
            default=ets.strftime("%Y/%m/%d %H%M"),
            label="End Time (Central Time):",
            min="2012/01/01 0000",
        ),
    ]
    return desc


def make_daily_pet_plot(ctx):
    """Generate a daily PET plot"""
    icursor = ctx["pgconn"].cursor(cursor_factory=psycopg2.extras.DictCursor)
    icursor.execute(
        """WITH climo as (
        select to_char(valid, 'mmdd') as mmdd, avg(c70) as  et
        from daily where station = 'A130209' GROUP by mmdd
    ), obs as (
        SELECT valid, dailyet_qc / 25.4 as et, to_char(valid, 'mmdd') as mmdd
        from sm_daily WHERE station = '%s' and valid >= '%s' and valid <= '%s'
    )

    select o.valid, o.et, c.et from obs o
    JOIN climo c on (c.mmdd = o.mmdd) ORDER by o.valid ASC
    """
        % (
            ctx["station"],
            ctx["sts"].strftime("%Y-%m-%d"),
            ctx["ets"].strftime("%Y-%m-%d"),
        )
    )
    dates = []
    o_dailyet = []
    c_et = []
    for row in icursor:
        dates.append(row[0])
        o_dailyet.append(row[1] if row[1] is not None else 0)
        c_et.append(row[2])

    df = pd.DataFrame(dict(dates=dates, dailyet=o_dailyet, climo_dailyet=c_et))
    if df.empty:
        raise NoDataFound("No Data Found!")

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(
        dates,
        o_dailyet,
        fc="brown",
        ec="brown",
        zorder=1,
        align="center",
        label="Observed",
    )
    ax.plot(dates, c_et, label="Climatology", color="k", lw=1.5, zorder=2)
    ax.grid(True)
    ax.set_ylabel("Potential Evapotranspiration [inch]")
    ax.set_title(
        (
            "ISUSM Station: %s Timeseries\n"
            "Potential Evapotranspiration, "
            "Climatology from Ames 1986-2014"
        )
        % (ctx["_nt"].sts[ctx["station"]]["name"],)
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b\n%Y"))
    interval = int(len(dates) / 7.0 + 1)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
    ax.legend(loc="best", ncol=1, fontsize=10)
    return fig, df


def make_daily_rad_plot(ctx):
    """Generate a daily radiation plot"""
    # Get clear sky theory
    theory = meteorology.clearsky_shortwave_irradiance_year(
        ctx["_nt"].sts[ctx["station"]]["lat"],
        ctx["_nt"].sts[ctx["station"]]["elevation"],
    )

    icursor = ctx["pgconn"].cursor(cursor_factory=psycopg2.extras.DictCursor)
    icursor.execute(
        """
        SELECT valid, slrkj_tot_qc / 1000. from sm_daily
        where station = '%s'
        and valid >= '%s' and valid <= '%s' and slrkj_tot_qc > 0 and
        slrkj_tot_qc < 40000 ORDER by valid ASC
    """
        % (
            ctx["station"],
            ctx["sts"].strftime("%Y-%m-%d"),
            ctx["ets"].strftime("%Y-%m-%d"),
        )
    )
    dates = []
    vals = []
    tmax = []
    if icursor.rowcount == 0:
        raise NoDataFound("No Data Found, sorry")
    for row in icursor:
        dates.append(row[0])
        vals.append(row[1])
        jday = int(row[0].strftime("%j"))
        if jday > 364:
            jday = 364
        tmax.append(theory[jday])

    df = pd.DataFrame(dict(dates=dates, vals=vals, jday=jday, tmax=tmax))

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(
        dates,
        vals,
        fc="tan",
        ec="brown",
        zorder=2,
        align="center",
        label="Observed",
    )
    ax.plot(dates, tmax, label=r"Modelled Max $\tau$ =0.75", color="k", lw=1.5)
    ax.grid(True)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b\n%Y"))
    interval = int(len(dates) / 7.0 + 1)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
    ax.set_ylabel("Solar Radiation $MJ m^{-2}$")
    ax.set_title(
        ("ISUSM Station: %s Timeseries\n" "Daily Solar Radiation")
        % (ctx["_nt"].sts[ctx["station"]]["name"],)
    )
    ax.set_ylim(0, 38)
    ax.legend(loc=1, ncol=2, fontsize=10)
    return fig, df


def make_daily_rainfall_soil_rh(ctx):
    """Give them what they want."""
    df = read_sql(
        "SELECT valid, rain_in_tot_qc, tsoil_c_avg_qc, rh_avg_qc "
        "from sm_daily where station = %s and valid >= %s and valid <= %s "
        "ORDER by valid ASC",
        ctx["pgconn"],
        params=(
            ctx["station"],
            ctx["sts"].strftime("%Y-%m-%d"),
            ctx["ets"].strftime("%Y-%m-%d"),
        ),
        index_col="valid",
    )
    if df.empty:
        raise NoDataFound("No Data Found for Query")

    title = "ISUSM Station: %s Timeseries" % (
        ctx["_nt"].sts[ctx["station"]]["name"],
    )
    subtitle = "Daily Precipitation, 4 Inch Soil Temperature, and Avg RH"

    fig = figure(title=title, subtitle=subtitle)

    def common(ax):
        """do common things."""
        ax.grid(True)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b\n%Y"))
        interval = int(len(df.index) / 7.0 + 1)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))

    ax = fig.add_axes([0.1, 0.7, 0.8, 0.2])
    ax.bar(
        df.index.values,
        df["rain_in_tot_qc"].values,
        color="blue",
        align="center",
    )
    ax.set_ylim(bottom=0)
    ax.set_ylabel("Precipitation [inch]")
    common(ax)

    ax = fig.add_axes([0.1, 0.4, 0.8, 0.2])
    vals = c2f(df["tsoil_c_avg_qc"].values)
    ax.bar(
        df.index.values,
        vals,
        color="brown",
        align="center",
    )
    ax.set_ylim(np.min(vals) - 5, np.max(vals) + 5)
    ax.set_ylabel(r"4 Inch Soil Temp [$^\circ$F]")
    common(ax)

    ax = fig.add_axes([0.1, 0.1, 0.8, 0.2])
    ax.bar(
        df.index.values,
        df["rh_avg_qc"].values,
        color="blue",
        align="center",
    )
    ax.set_ylim(0, 100)
    ax.set_ylabel("Average\nRelative Humidity [%]")
    common(ax)

    return fig, df


def make_daily_plot(ctx):
    """Generate a daily plot of max/min 4 inch soil temps"""
    df = read_sql(
        """
        SELECT date(valid), min(tsoil_c_avg_qc),
        max(tsoil_c_avg_qc), avg(tsoil_c_avg_qc) from sm_hourly
        where station = %s and valid >= %s and valid < %s
        and tsoil_c_avg is not null GROUP by date ORDER by date ASC
    """,
        ctx["pgconn"],
        params=(
            ctx["station"],
            ctx["sts"].strftime("%Y-%m-%d 00:00"),
            ctx["ets"].strftime("%Y-%m-%d 23:59"),
        ),
        index_col="date",
    )
    if df.empty:
        raise NoDataFound("No Data Found for Query")

    mins = c2f(df["min"].values)
    maxs = c2f(df["max"].values)
    avgs = c2f(df["avg"].values)
    (fig, ax) = plt.subplots(1, 1)
    ax.bar(
        df.index.values,
        maxs - mins,
        bottom=mins,
        fc="tan",
        ec="brown",
        zorder=2,
        align="center",
        label="Max/Min",
    )
    ax.scatter(
        df.index.values,
        avgs,
        marker="*",
        s=30,
        zorder=3,
        color="brown",
        label="Hourly Avg",
    )
    ax.axhline(50, lw=1.5, c="k")
    ax.grid(True)
    ax.set_ylabel(r"4 inch Soil Temperature $^\circ$F")
    ax.set_title(
        (
            "ISUSM Station: %s Timeseries\n"
            "Daily Max/Min/Avg 4 inch Soil Temperatures"
        )
        % (ctx["_nt"].sts[ctx["station"]]["name"],)
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b\n%Y"))
    interval = int(len(df.index) / 7.0 + 1)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
    ax.legend(loc="best", ncol=2, fontsize=10)
    return fig, df


def make_battery_plot(ctx):
    """Generate a plot of battery"""
    icursor = ctx["pgconn"].cursor(cursor_factory=psycopg2.extras.DictCursor)
    icursor.execute(
        """SELECT valid, battv_min_qc from sm_hourly
    where station = '%s' and valid >= '%s 00:00' and valid < '%s 23:56'
    and battv_min_qc is not null ORDER by valid ASC
    """
        % (
            ctx["station"],
            ctx["sts"].strftime("%Y-%m-%d"),
            ctx["ets"].strftime("%Y-%m-%d"),
        )
    )
    dates = []
    battv = []
    for row in icursor:
        dates.append(row[0])
        battv.append(row[1])

    df = pd.DataFrame(dict(dates=dates, battv=battv))
    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
    ax.plot(dates, battv)
    ax.grid(True)
    ax.set_ylabel("Battery Voltage [V]")
    ax.set_title(
        ("ISUSM Station: %s Timeseries\n" "Battery Voltage")
        % (ctx["_nt"].sts[ctx["station"]]["name"],)
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b\n%Y"))
    ax.legend(loc="best", ncol=2, fontsize=10)
    return fig, df


def make_vsm_histogram_plot(ctx):
    """Option 6"""
    df = read_sql(
        """
        SELECT
    CASE WHEN t12_c_avg_qc > 1 then calc_vwc_12_avg_qc else null end as v12,
    CASE WHEN t24_c_avg_qc > 1 then calc_vwc_24_avg_qc else null end as v24,
    CASE WHEN t50_c_avg_qc > 1 then calc_vwc_50_avg_qc else null end as v50
        from sm_hourly
        where station = %s and valid >= %s and valid < %s
    """,
        ctx["pgconn"],
        params=(ctx["station"], ctx["sts"], ctx["ets"]),
        index_col=None,
    )

    (fig, ax) = plt.subplots(3, 1, sharex=True)
    ax[0].set_title(
        (
            "ISUSM Station: %s VWC Histogram\n"
            "For un-frozen condition between %s and %s"
        )
        % (
            ctx["_nt"].sts[ctx["station"]]["name"],
            ctx["sts"].strftime("%-d %b %Y"),
            ctx["ets"].strftime("%-d %b %Y"),
        )
    )
    for i, col in enumerate(["v12", "v24", "v50"]):
        ax[i].hist(df[col] * 100.0, bins=50, range=(0, 50), density=True)
        ax[i].set_ylabel("Frequency")
        ax[i].grid(True)
        ax[i].text(
            0.99,
            0.99,
            "%s inches" % (col[1:],),
            transform=ax[i].transAxes,
            ha="right",
            va="top",
        )
        ax[i].set_yscale("log")

    ax[2].set_xlabel("Volumetric Water Content [%]")
    return fig, df


def make_daily_water_change_plot(ctx):
    """Option 7"""
    # Get daily precip
    pdf = read_sql(
        """
    SELECT valid, rain_in_tot_qc from sm_daily where station = %s
    and valid >= %s and valid <= %s ORDER by valid ASC
    """,
        ctx["pgconn"],
        params=(ctx["station"], ctx["sts"].date(), ctx["ets"].date()),
        index_col="valid",
    )

    df = read_sql(
        """
    WITH obs as (
        SELECT valid,
    CASE WHEN t12_c_avg_qc > 1 then calc_vwc_12_avg_qc else null end as v12,
    CASE WHEN t24_c_avg_qc > 1 then calc_vwc_24_avg_qc else null end as v24,
    CASE WHEN t50_c_avg_qc > 1 then calc_vwc_50_avg_qc else null end as v50
        from sm_daily
        where station = %s and valid >= %s and valid < %s)

    SELECT valid,
    v12, v12 - lag(v12) OVER (ORDER by valid ASC) as v12_delta,
    v24, v24 - lag(v24) OVER (ORDER by valid ASC) as v24_delta,
    v50, v50 - lag(v50) OVER (ORDER by valid ASC) as v50_delta
    from obs ORDER by valid ASC
    """,
        ctx["pgconn"],
        params=(ctx["station"], ctx["sts"], ctx["ets"]),
        index_col=None,
    )
    # df.interpolate(inplace=True, axis=1, method='nearest')
    l1 = 12.0
    l2 = 12.0
    l3 = 0.0
    df["change"] = (
        df["v12_delta"] * l1 + df["v24_delta"] * l2 + df["v50_delta"] * l3
    )
    df["depth"] = df["v12"] * l1 + df["v24"] * l2 + df["v50"] * l3

    (fig, ax) = plt.subplots(2, 1, sharex=True)
    if not df["depth"].isnull().all():
        ax[0].plot(df["valid"].values, df["depth"], color="b", lw=2)
    oneday = datetime.timedelta(days=1)
    for level in [0.15, 0.25, 0.35, 0.45]:
        ax[0].axhline((l1 + l2 + l3) * level, c="k")
        ax[0].text(
            df["valid"].values[-1] + oneday,
            (l1 + l2 + l3) * level,
            "  %.0f%%" % (level * 100.0,),
            va="center",
        )
    ax[0].grid(True)
    ax[0].set_ylabel("Water Depth [inch]")
    ax[0].set_title(
        (
            'ISUSM Station: %s Daily Soil (6-30") Water\n'
            "For un-frozen condition between %s and %s"
        )
        % (
            ctx["_nt"].sts[ctx["station"]]["name"],
            ctx["sts"].strftime("%-d %b %Y"),
            ctx["ets"].strftime("%-d %b %Y"),
        )
    )
    bars = ax[1].bar(df["valid"].values, df["change"].values, fc="b", ec="b")
    for mybar in bars:
        if mybar.get_y() < 0:
            mybar.set_facecolor("r")
            mybar.set_edgecolor("r")
    ax[1].set_ylabel("Soil Water Change [inch]")
    ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%-d %b\n%Y"))
    interval = int(len(df.index) / 7.0 + 1)
    ax[1].xaxis.set_major_locator(mdates.DayLocator(interval=interval))
    ax[1].grid(True)

    if (ctx["ets"] - ctx["sts"]).total_seconds() < (60 * 86400):
        ylim = ax[1].get_ylim()[1]
        # Attempt to place precip text above this plot
        pdf["pday"] = pdf["rain_in_tot_qc"].values
        for valid, row in pdf.iterrows():
            if row["pday"] > 0:
                ax[1].text(
                    valid,
                    ylim,
                    "%.2f" % (row["pday"],),
                    rotation=90,
                    va="bottom",
                    color="b",
                )
        ax[1].text(
            -0.01,
            1.05,
            "Rain ->",
            ha="right",
            transform=ax[1].transAxes,
            color="b",
        )
    ax[0].set_xlim(df["valid"].min() - oneday, df["valid"].max() + oneday)
    return fig, df


def plot2(ctx):
    """Just soil temps"""
    df = read_sql(
        """
        SELECT * from sm_hourly WHERE
        station = %s and valid BETWEEN %s and %s ORDER by valid ASC
    """,
        ctx["pgconn"],
        params=(ctx["station"], ctx["sts"], ctx["ets"]),
        index_col="valid",
    )
    d12t = df["t12_c_avg_qc"]
    d24t = df["t24_c_avg_qc"]
    d50t = df["t50_c_avg_qc"]
    tsoil = df["tsoil_c_avg_qc"]
    valid = df.index.values

    # maxy = max([np.max(d12sm), np.max(d24sm), np.max(d50sm)])
    # miny = min([np.min(d12sm), np.min(d24sm), np.min(d50sm)])

    (fig, ax) = plt.subplots(1, 1)
    ax.grid(True)
    ax.set_title(
        ("ISUSM Station: %s Timeseries\n" "Soil Temperature at Depth\n ")
        % (ctx["_nt"].sts[ctx["station"]]["name"],)
    )
    ax.plot(valid, c2f(tsoil), linewidth=2, color="brown", label="4 inch")
    if not d12t.isnull().any():
        ax.plot(valid, c2f(d12t), linewidth=2, color="r", label="12 inch")
    if not d24t.isnull().any():
        ax.plot(valid, c2f(d24t), linewidth=2, color="purple", label="24 inch")
    if not d50t.isnull().any():
        ax.plot(valid, c2f(d50t), linewidth=2, color="black", label="50 inch")
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width, box.height * 0.9])
    ax.legend(bbox_to_anchor=(0.5, 1.02), ncol=4, loc="center", fontsize=12)
    days = (ctx["ets"] - ctx["sts"]).days
    if days >= 3:
        interval = max(int(days / 7), 1)
        ax.xaxis.set_major_locator(
            mdates.DayLocator(
                interval=interval, tz=pytz.timezone("America/Chicago")
            )
        )
        ax.xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%-d %b\n%Y", tz=pytz.timezone("America/Chicago")
            )
        )
    else:
        ax.xaxis.set_major_locator(
            mdates.AutoDateLocator(
                maxticks=10, tz=pytz.timezone("America/Chicago")
            )
        )
        ax.xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%-I %p\n%d %b", tz=pytz.timezone("America/Chicago")
            )
        )
    if ax.get_ylim()[0] < 40:
        ax.axhline(32, linestyle="--", lw=2, color="tan")
    ax.set_ylabel(r"Temperature $^\circ$F")
    return fig, df


def plot1(ctx):
    """Do main plotting logic"""
    df = read_sql(
        "SELECT * from sm_hourly WHERE "
        "station = %s and valid BETWEEN %s and %s ORDER by valid ASC",
        ctx["pgconn"],
        params=(ctx["station"], ctx["sts"], ctx["ets"]),
        index_col="valid",
    )
    if df.empty:
        raise NoDataFound("No Data Found for This Plot.")
    solar_wm2 = df["slrkj_tot_qc"] / 3600.0 * 1000.0
    d12sm = df["calc_vwc_12_avg_qc"]
    d12t = df["t12_c_avg_qc"]
    d24t = df["t24_c_avg_qc"]
    d50t = df["t50_c_avg_qc"]
    d24sm = df["calc_vwc_24_avg_qc"]
    d50sm = df["calc_vwc_50_avg_qc"]
    rain = df["rain_in_tot_qc"]
    tair = df["tair_c_avg_qc"]
    tsoil = df["tsoil_c_avg_qc"]
    valid = df.index

    (fig, ax) = plt.subplots(3, 1, sharex=True, figsize=(8, 8))
    ax[0].grid(True)
    ax2 = ax[0].twinx()
    ax[0].set_zorder(ax2.get_zorder() + 1)
    ax[0].patch.set_visible(False)
    # arange leads to funky values
    ax2.set_yticks([-0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0])
    ax2.set_yticklabels([0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0])
    ax2.set_ylim(-0.6, 0)
    ax2.set_ylabel("Hourly Precipitation [inch]")
    ax2.bar(valid, 0 - rain, width=0.04, fc="b", ec="b", zorder=4)

    if not d12sm.isnull().all():
        ax[0].plot(valid, d12sm * 100.0, linewidth=2, color="r", zorder=5)
    if not d24sm.isnull().all():
        ax[0].plot(valid, d24sm * 100.0, linewidth=2, color="purple", zorder=5)
    if not d50sm.isnull().all():
        ax[0].plot(valid, d50sm * 100.0, linewidth=2, color="black", zorder=5)
    ax[0].set_ylabel("Volumetric Soil Water Content [%]", fontsize=10)

    ax[0].set_title(
        ("ISUSM Station: %s Timeseries")
        % (ctx["_nt"].sts[ctx["station"]]["name"],)
    )
    box = ax[0].get_position()
    ax[0].set_position(
        [box.x0, box.y0 + box.height * 0.05, box.width, box.height * 0.95]
    )
    box = ax2.get_position()
    ax2.set_position(
        [box.x0, box.y0 + box.height * 0.05, box.width, box.height * 0.95]
    )
    handles = [
        Line2D([0], [0], color="r", lw=3, label="12 inch"),
        Line2D([0], [0], color="purple", lw=3, label="24 inch"),
        Line2D([0], [0], color="black", lw=3, label="50 inch"),
        Patch(facecolor="b", edgecolor="b", label="Hourly Precip"),
    ]
    ax[0].legend(
        handles=handles,
        bbox_to_anchor=(0.5, -0.15),
        ncol=4,
        loc="center",
        fontsize=12,
    )

    # ----------------------------------------
    if not d12t.isnull().all():
        ax[1].plot(valid, c2f(d12t), linewidth=2, color="r", label="12in")
    if not d24t.isnull().all():
        ax[1].plot(valid, c2f(d24t), linewidth=2, color="purple", label="24in")
    if not d50t.isnull().all():
        ax[1].plot(valid, c2f(d50t), linewidth=2, color="black", label="50in")
    ax[1].grid(True)
    ax[1].set_ylabel(r"Soil Temperature $^\circ$F")
    box = ax[1].get_position()
    ax[1].set_position(
        [box.x0, box.y0 + box.height * 0.05, box.width, box.height * 0.95]
    )

    # ------------------------------------------------------

    ax2 = ax[2].twinx()
    (l3,) = ax2.plot(valid, solar_wm2, color="g", zorder=1, lw=2)
    ax2.set_ylabel("Solar Radiation [W/m^2]", color="g")

    (l1,) = ax[2].plot(valid, c2f(tair), linewidth=2, color="blue", zorder=2)
    (l2,) = ax[2].plot(valid, c2f(tsoil), linewidth=2, color="brown", zorder=2)
    ax[2].grid(True)
    ax[2].legend(
        [l1, l2, l3],
        ["Air", '4" Soil', "Solar Radiation"],
        bbox_to_anchor=(0.5, 1.1),
        loc="center",
        ncol=3,
    )
    ax[2].set_ylabel(r"Temperature $^\circ$F")

    ax[2].set_zorder(ax2.get_zorder() + 1)
    ax[2].patch.set_visible(False)
    ax[0].set_xlim(df.index.min(), df.index.max())

    days = (ctx["ets"] - ctx["sts"]).days
    if days >= 3:
        interval = max(int(days / 7), 1)
        ax[2].xaxis.set_major_locator(
            mdates.DayLocator(
                interval=interval, tz=pytz.timezone("America/Chicago")
            )
        )
        ax[2].xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%-d %b\n%Y", tz=pytz.timezone("America/Chicago")
            )
        )
    else:
        ax[2].xaxis.set_major_locator(
            mdates.AutoDateLocator(
                maxticks=10, tz=pytz.timezone("America/Chicago")
            )
        )
        ax[2].xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%-I %p\n%d %b", tz=pytz.timezone("America/Chicago")
            )
        )

    return fig, df


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    ctx["pgconn"] = get_dbconn("isuag")

    if ctx["opt"] == "1":
        fig, df = plot1(ctx)
    elif ctx["opt"] == "2":
        fig, df = plot2(ctx)
    elif ctx["opt"] == "3":
        fig, df = make_daily_plot(ctx)
    elif ctx["opt"] == "4":
        fig, df = make_daily_rad_plot(ctx)
    elif ctx["opt"] == "5":
        fig, df = make_daily_pet_plot(ctx)
    elif ctx["opt"] == "6":
        fig, df = make_vsm_histogram_plot(ctx)
    elif ctx["opt"] == "7":
        fig, df = make_daily_water_change_plot(ctx)
    elif ctx["opt"] == "8":
        fig, df = make_battery_plot(ctx)
    elif ctx["opt"] == "9":
        fig, df = make_daily_rainfall_soil_rh(ctx)

    # removal of timestamps, sigh
    df = df.reset_index()
    for col in [
        "valid",
        "ws_mph_tmx",
        "valid",
        "ws_mph_tmx_qc",
        "tair_c_tmn",
        "tair_c_tmx",
        "ws_mps_tmx",
        "tair_c_tmx_qc",
        "tair_c_tmn_qc",
        "ws_mps_tmx_qc",
        "ws_mph_tmx",
        "ws_mph_tmx_qc",
    ]:
        if col in df.columns:
            df[col] = df[col].apply(
                (
                    lambda x: x
                    if isinstance(x, str) or pd.isnull(x)
                    else x.strftime("%Y-%m-%d %H:%M")
                )
            )
    return fig, df


if __name__ == "__main__":
    plotter(dict())
    # fig, df = plotter(dict())
    # with pd.ExcelWriter("/tmp/ba.xlsx") as xl:
    #    df.to_excel(xl)
