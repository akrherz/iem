"""This application generates time series charts using data from the
    ISU Soil Moisture Network."""
# pylint: disable=no-member,too-many-lines
import datetime

import numpy as np
import psycopg2
import pytz
import pandas as pd
import matplotlib.dates as mdates
import matplotlib.colors as mpcolors
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from pyiem import meteorology
from pyiem.plot import figure, figure_axes, get_cmap
from pyiem.util import (
    convert_value,
    get_autoplot_context,
    get_dbconn,
    c2f,
    get_sqlalchemy_conn,
)
from pyiem.exceptions import NoDataFound

CENTRAL = pytz.timezone("America/Chicago")
PLOTTYPES = {
    "1": "3 Panel Plot",
    "at": "One Minute Timeseries",
    "2": "Just Soil Temps",
    "sm": "Just Soil Moisture",
    "3": "Daily Max/Min 4 Inch Soil Temps",
    "4": "Daily Solar Radiation",
    "5": "Daily Potential Evapotranspiration",
    "6": "Histogram of Volumetric Soil Moisture",
    "7": "Daily Soil Water + Change",
    "8": "Battery Voltage",
    "9": "Daily Rainfall, 4 inch Soil Temp, and RH",
    "10": "Inversion Diagnostic Plot (BOOI4, CAMI4, CRFI4)",
    "11": "Inversion Daily Timing (BOOI4, CAMI4, CRFI4)",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["frontend"] = "/agclimate/smts.php"
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


def make_inversion_timing(ctx):
    """Generate an inversion plot"""
    # Rectify the start date to midnight
    ctx["sts"] = ctx["sts"].replace(hour=0, minute=0)
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            "SELECT valid at time zone 'UTC' as utc_valid, "
            "tair_10_c_avg_qc, tair_15_c_avg_qc "
            "from sm_inversion where station = %s and "
            "valid >= %s and valid < %s and tair_10_c_avg_qc is not null and "
            "tair_15_c_avg_qc is not null ORDER by valid ASC",
            conn,
            params=(ctx["station"], ctx["sts"], ctx["ets"]),
        )
    if df.empty:
        raise NoDataFound("No inversion data found for station!")
    df = df.assign(
        utc_valid=lambda df_: df_.utc_valid.dt.tz_localize(pytz.UTC),
        valid=lambda df_: df_.utc_valid.dt.tz_convert(CENTRAL),
        delta=lambda df_: (
            c2f(df_.tair_10_c_avg_qc) - c2f(df_.tair_15_c_avg_qc)
        ),
    )

    grid = np.ones(((ctx["ets"] - ctx["sts"]).days + 1, 1440)) * np.nan
    df["minute"] = df["valid"].dt.hour * 60 + df["valid"].dt.minute
    # F
    df["day"] = (df["valid"] - df["valid"].iloc[0]).dt.days
    for _, row in df.iterrows():
        grid[row["day"], row["minute"]] = float(row["delta"])
    title = f"ISUSM Station: {ctx['_sname']} :: Inversion Timeseries"
    subtitle = "10 Foot Air Temperature minus 1.5 Foot Air Temperature (F)"
    fig, ax = figure_axes(apctx=ctx, title=title, subtitle=subtitle)
    clevs = np.arange(-2, 2.1, 0.2)
    cmap = get_cmap("bwr")
    cmap.set_bad("tan")
    norm = mpcolors.BoundaryNorm(clevs, cmap.N)
    res = ax.imshow(
        grid, aspect="auto", interpolation="none", cmap=cmap, norm=norm
    )
    fig.colorbar(res).set_label(
        "<< Less Likely           Inversion            More Likely >>"
    )
    ax.set_xticks(np.arange(0, 1441, 120))
    # hours of the day
    ax.set_xticklabels(
        [
            "Mid",
            "2 AM",
            "4 AM",
            "6 AM",
            "8 AM",
            "10 AM",
            "Noon",
            "2 PM",
            "4 PM",
            "6 PM",
            "8 PM",
            "10 PM",
            "Mid",
        ]
    )
    ax.grid(True)
    ax.set_xlabel(f"{ctx['sts'].year} Local Time (US Central)")

    def custom(x, _pos=None):
        dt = ctx["sts"] + datetime.timedelta(days=x)
        return dt.strftime("%-d %b")

    ax.yaxis.set_major_formatter(custom)

    return fig, df


def make_inversion_plot(ctx):
    """Generate an inversion plot"""
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            "SELECT * from sm_inversion where station = %s and "
            "valid >= %s and valid < %s ORDER by valid ASC",
            conn,
            params=(ctx["station"], ctx["sts"], ctx["ets"]),
        )
    if df.empty:
        raise NoDataFound("No inversion data found for station!")

    axwidth = 0.88
    axheight = 0.25
    fig = figure(apctx=ctx)
    axes = fig.subplots(3, 1, sharex=True)
    ax = axes[0]
    ax.set_position([0.07, 0.7, axwidth, axheight])
    ax.plot(df["valid"], c2f(df["tair_15_c_avg_qc"].values), label="1.5 feet")
    ax.plot(df["valid"], c2f(df["tair_5_c_avg_qc"].values), label="5 feet")
    ax.plot(df["valid"], c2f(df["tair_10_c_avg_qc"].values), label="10 feet")
    ax.grid(True)
    ax.set_ylabel(r"Air Temperature $^\circ$F")
    ax.set_title(f"ISUSM Station: {ctx['_sname']} :: Inversion Timeseries")
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%-I:%M %p\n%-d %b", tz=CENTRAL)
    )
    ax.legend(loc="best", ncol=3, fontsize=10)

    ax = axes[1]
    ax.set_position([0.07, 0.4, axwidth, axheight])
    ax.plot(
        df["valid"],
        (
            c2f(df["tair_10_c_avg_qc"].values)
            - c2f(df["tair_15_c_avg_qc"].values)
        ),
    )
    ax.grid(True)
    ax.set_title("10 Foot Temperature minus 1.5 Foot Temperature")
    ax.set_ylabel(r"Air Temperature Diff $^\circ$F")
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%-I:%M %p\n%-d %b", tz=CENTRAL)
    )

    ax = axes[2]
    ax.set_position([0.07, 0.1, axwidth, axheight])
    ax.bar(
        df["valid"],
        convert_value(
            df["ws_ms_max_qc"].values, "meter / second", "mile / hour"
        ),
        zorder=2,
        color="red",
        width=1 / 1440.0,
        label="5 Second Gust",
    )
    ax.bar(
        df["valid"],
        convert_value(
            df["ws_ms_avg_qc"].values, "meter / second", "mile / hour"
        ),
        zorder=3,
        color="lightblue",
        label="1 Minute Speed",
        width=1 / 1440.0,
    )
    ax.set_title("10 Foot Wind Speed")
    ax.grid(True)
    ax.set_ylabel("Wind Speed/Gust [MPH]")
    ax.legend(ncol=2)

    return fig, df


def make_daily_pet_plot(ctx):
    """Generate a daily PET plot"""
    icursor = ctx["pgconn"].cursor(cursor_factory=psycopg2.extras.DictCursor)
    icursor.execute(
        """WITH climo as (
        select to_char(valid, 'mmdd') as mmdd, avg(c70) as  et
        from daily where station = 'A130209' GROUP by mmdd
    ), obs as (
        SELECT valid, dailyet_qc / 25.4 as et, to_char(valid, 'mmdd') as mmdd
        from sm_daily WHERE station = %s and valid >= %s and valid <= %s
    )

    select o.valid, o.et, c.et from obs o
    JOIN climo c on (c.mmdd = o.mmdd) ORDER by o.valid ASC
    """,
        (
            ctx["station"],
            ctx["sts"].strftime("%Y-%m-%d"),
            ctx["ets"].strftime("%Y-%m-%d"),
        ),
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

    title = (
        f"ISUSM Station: {ctx['_sname']} Timeseries\n"
        "Potential Evapotranspiration, Climatology from Ames 1986-2014"
    )
    (fig, ax) = figure_axes(apctx=ctx, title=title)
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
        "SELECT valid, slrkj_tot_qc / 1000. from sm_daily where station = %s "
        "and valid >= %s and valid <= %s and slrkj_tot_qc > 0 and "
        "slrkj_tot_qc < 40000 ORDER by valid ASC",
        (
            ctx["station"],
            ctx["sts"].strftime("%Y-%m-%d"),
            ctx["ets"].strftime("%Y-%m-%d"),
        ),
    )
    dates = []
    vals = []
    tmax = []
    if icursor.rowcount == 0:
        raise NoDataFound("No Data Found, sorry")
    for row in icursor:
        dates.append(row[0])
        vals.append(row[1])
        jday = min(int(row[0].strftime("%j")), 364)
        tmax.append(theory[jday])

    df = pd.DataFrame(dict(dates=dates, vals=vals, jday=jday, tmax=tmax))

    title = (
        f"ISUSM Station: {ctx['_sname']} Timeseries\n" "Daily Solar Radiation"
    )
    (fig, ax) = figure_axes(apctx=ctx, title=title)
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
    ax.set_ylim(0, 38)
    ax.legend(loc=1, ncol=2, fontsize=10)
    return fig, df


def make_daily_rainfall_soil_rh(ctx):
    """Give them what they want."""
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            "SELECT valid, rain_in_tot_qc, t4_c_avg_qc, rh_avg_qc "
            "from sm_daily where station = %s and valid >= %s and valid <= %s "
            "ORDER by valid ASC",
            conn,
            params=(
                ctx["station"],
                ctx["sts"].strftime("%Y-%m-%d"),
                ctx["ets"].strftime("%Y-%m-%d"),
            ),
            index_col="valid",
        )
    if df.empty:
        raise NoDataFound("No Data Found for Query")

    title = f"ISUSM Station: {ctx['_sname']} Timeseries"
    subtitle = "Daily Precipitation, 4 Inch Soil Temperature, and Avg RH"

    fig = figure(title=title, subtitle=subtitle, apctx=ctx)

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
    vals = c2f(df["t4_c_avg_qc"].values)
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
    if not pd.isna(df["rh_avg_qc"]).all():
        ax.bar(
            df.index.values,
            df["rh_avg_qc"].values,
            color="blue",
            align="center",
        )
    else:
        ax.text(0.5, 0.5, "Relative Humidity Missing", transform=ax.transAxes)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Average\nRelative Humidity [%]")
    common(ax)

    return fig, df


def make_daily_plot(ctx):
    """Generate a daily plot of max/min 4 inch soil temps"""
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            """
            SELECT date(valid), min(t4_c_avg_qc),
            max(t4_c_avg_qc), avg(t4_c_avg_qc) from sm_hourly
            where station = %s and valid >= %s and valid < %s
            and t4_c_avg is not null GROUP by date ORDER by date ASC
        """,
            conn,
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
    title = (
        f"ISUSM Station: {ctx['_sname']} Timeseries\n"
        "Daily Max/Min/Avg 4 inch Soil Temperatures"
    )
    (fig, ax) = figure_axes(apctx=ctx, title=title)
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
    where station = %s and valid >= %s and valid < %s
    and battv_min_qc is not null ORDER by valid ASC
    """,
        (
            ctx["station"],
            ctx["sts"].strftime("%Y-%m-%d 00:00"),
            ctx["ets"].strftime("%Y-%m-%d 23:59"),
        ),
    )
    dates = []
    battv = []
    for row in icursor:
        dates.append(row[0])
        battv.append(row[1])

    df = pd.DataFrame(dict(dates=dates, battv=battv))
    title = f"ISUSM Station: {ctx['_sname']} Timeseries\n" "Battery Voltage"
    (fig, ax) = figure_axes(apctx=ctx, title=title)
    ax.plot(dates, battv)
    ax.grid(True)
    ax.set_ylabel("Battery Voltage [V]")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b\n%Y"))
    ax.legend(loc="best", ncol=2, fontsize=10)
    return fig, df


def make_vsm_histogram_plot(ctx):
    """Option 6"""
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            """
            SELECT
            CASE WHEN t12_c_avg_qc > 1 then vwc12_qc else null end
                as v12,
            CASE WHEN t24_c_avg_qc > 1 then vwc24_qc else null end
                as v24,
            CASE WHEN t50_c_avg_qc > 1 then vwc50_qc else null end
                as v50
            from sm_hourly
            where station = %s and valid >= %s and valid < %s
        """,
            conn,
            params=(ctx["station"], ctx["sts"], ctx["ets"]),
            index_col=None,
        )
    title = (
        f"ISUSM Station: {ctx['_sname']} VWC Histogram\n"
        f"For un-frozen condition between {ctx['sts']:%-d %b %Y} "
        f"and {ctx['ets']:%-d %b %Y}"
    )
    fig = figure(apctx=ctx, title=title)
    ax = fig.subplots(3, 1, sharex=True)
    for i, col in enumerate(["v12", "v24", "v50"]):
        ax[i].hist(df[col] * 100.0, bins=50, range=(0, 50), density=True)
        ax[i].set_ylabel("Frequency")
        ax[i].grid(True)
        ax[i].text(
            0.99,
            0.99,
            f"{col[1:]} inches",
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
    with get_sqlalchemy_conn("isuag") as conn:
        pdf = pd.read_sql(
            "SELECT valid, rain_in_tot_qc from sm_daily where station = %s "
            "and valid >= %s and valid <= %s ORDER by valid ASC",
            conn,
            params=(ctx["station"], ctx["sts"].date(), ctx["ets"].date()),
            index_col="valid",
        )

        df = pd.read_sql(
            """
        WITH obs as (
            SELECT valid,
            CASE WHEN t12_c_avg_qc > 1 then vwc12_qc else null end
            as v12,
            CASE WHEN t24_c_avg_qc > 1 then vwc24_qc else null end
            as v24,
            CASE WHEN t50_c_avg_qc > 1 then vwc50_qc else null end
            as v50
            from sm_daily
            where station = %s and valid >= %s and valid < %s)

        SELECT valid,
        v12, v12 - lag(v12) OVER (ORDER by valid ASC) as v12_delta,
        v24, v24 - lag(v24) OVER (ORDER by valid ASC) as v24_delta,
        v50, v50 - lag(v50) OVER (ORDER by valid ASC) as v50_delta
        from obs ORDER by valid ASC
        """,
            conn,
            params=(ctx["station"], ctx["sts"], ctx["ets"]),
            index_col=None,
        )
    # 12inch covers 6-18 inches, 24inch covers 18-30 inches, 50inch excluded
    l1 = 12.0
    l2 = 12.0
    df["change"] = df["v12_delta"] * l1 + df["v24_delta"] * l2
    # Compute an estimate of available water capacity
    # thresholds arbitrarily chosen at 10% and 45%
    for lvl in ["v12", "v12"]:
        df[lvl] = df[lvl].clip(lower=0.1, upper=0.45)
    df["depth"] = df["v12"] * l1 + df["v24"] * l2 - (l1 + l2) * 0.1

    title = (
        f'ISUSM Station: {ctx["_sname"]} :: Daily Soil (6-30") Water\n'
        f"For un-frozen condition between {ctx['sts']:%-d %b %Y} and "
        f"{ctx['ets']:%-d %b %Y}"
    )
    fig = figure(apctx=ctx, title=title)
    ax = fig.subplots(2, 1, sharex=True)
    if not df["depth"].isnull().all():
        ax[0].bar(df["valid"].values, df["depth"], color="b", width=1)
    oneday = datetime.timedelta(days=1)
    ax[0].grid(True)
    ax[0].set_ylabel("Plant Available Soil Water [inch]")
    ax[0].set_ylim(bottom=0)

    # Second plot
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
                    f"{row['pday']:.2f}",
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


def plot_sm(ctx):
    """Just soil moisture."""
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            "SELECT * from sm_hourly WHERE station = %s and "
            "valid BETWEEN %s and %s ORDER by valid ASC",
            conn,
            params=(ctx["station"], ctx["sts"], ctx["ets"]),
            index_col="valid",
        )
    d12t = df["vwc12_qc"]
    d24t = df["vwc24_qc"]
    d50t = df["vwc50_qc"]
    d04t = df["vwc4_qc"]
    valid = df.index.values

    title = f"ISUSM Station: {ctx['_sname']} :: Soil Moisture Timeseries"
    (fig, ax) = figure_axes(apctx=ctx, title=title)
    ax.grid(True)
    svplotted = False
    for col in (
        df.filter(regex=r"sv_vwc.*_qc", axis=1)
        .sort_index(
            axis=1,
            key=lambda x: (
                x.str.replace("_qc", "")
                .str.replace("sv_vwc", " ")
                .values.astype(int)
            ),
        )
        .columns
    ):
        series = df[col]
        if series.isnull().all():
            continue
        depth = col.split("_")[1].replace("vwc", "")
        ax.plot(valid, series, linewidth=2, label=f"{depth}in")
        svplotted = True
    oplotted = False
    if not svplotted and not d04t.isnull().all():
        ax.plot(valid, d04t, linewidth=2, color="brown", label="4 inch")
        oplotted = True
    if not svplotted and not d12t.isnull().all():
        ax.plot(valid, d12t, linewidth=2, color="r", label="12 inch")
        oplotted = True
    if not svplotted and not d24t.isnull().all():
        ax.plot(valid, d24t, linewidth=2, color="purple", label="24 inch")
        oplotted = True
    if not svplotted and not d50t.isnull().all():
        ax.plot(valid, d50t, linewidth=2, color="black", label="50 inch")
        oplotted = True
    if not oplotted and not svplotted:
        raise NoDataFound("No Soil Moisture Data for this station")
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width, box.height * 0.94])
    ax.legend(
        bbox_to_anchor=(0.5, 1.0),
        ncol=10,
        loc="lower center",
        fontsize=9 if svplotted else 12,
    )
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
    ax.set_ylabel(r"Volumetric Soil Moisture $m^3/m^3$")
    return fig, df


def plot2(ctx):
    """Just soil temps"""
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            "SELECT * from sm_hourly WHERE station = %s and "
            "valid BETWEEN %s and %s ORDER by valid ASC",
            conn,
            params=(ctx["station"], ctx["sts"], ctx["ets"]),
            index_col="valid",
        )
    d12t = df["t12_c_avg_qc"]
    d24t = df["t24_c_avg_qc"]
    d50t = df["t50_c_avg_qc"]
    d04t = df["t4_c_avg_qc"]
    valid = df.index.values

    title = f"ISUSM Station: {ctx['_sname']} :: Soil Temperature Timeseries"
    (fig, ax) = figure_axes(apctx=ctx, title=title)
    ax.grid(True)
    svplotted = False
    for depth in [2, 4, 8, 12, 14, 16, 20, 24, 28, 30, 32, 36, 40, 42, 52]:
        series = df[f"sv_t{depth}_qc"]
        if series.isnull().all():
            continue
        ax.plot(valid, c2f(series), linewidth=2, label=f"{depth}in")
        svplotted = True

    if not svplotted and not d04t.isnull().all():
        ax.plot(valid, c2f(d04t), linewidth=2, color="brown", label="4 inch")
    if not svplotted and not d12t.isnull().all():
        ax.plot(valid, c2f(d12t), linewidth=2, color="r", label="12 inch")
    if not svplotted and not d24t.isnull().all():
        ax.plot(valid, c2f(d24t), linewidth=2, color="purple", label="24 inch")
    if not svplotted and not d50t.isnull().all():
        ax.plot(valid, c2f(d50t), linewidth=2, color="black", label="50 inch")
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width, box.height * 0.94])
    ax.legend(
        bbox_to_anchor=(0.5, 1.0),
        ncol=10,
        loc="lower center",
        fontsize=9 if svplotted else 12,
    )
    xaxis_magic(ctx, ax)
    if ax.get_ylim()[0] < 40:
        ax.axhline(32, linestyle="--", lw=2, color="tan")
    ax.set_ylabel(r"Temperature $^\circ$F")
    return fig, df


def plot_at(ctx):
    """One minute temperatures."""
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            """
            SELECT valid, tair_c_avg_qc, rh_avg_qc, slrkj_tot_qc,
            ws_mph_qc, ws_mph_max_qc from sm_minute WHERE
            station = %s and valid BETWEEN %s and %s ORDER by valid ASC
            """,
            conn,
            params=(ctx["station"], ctx["sts"], ctx["ets"]),
            index_col="valid",
        )
    if df.empty:
        raise NoDataFound("No Data Found for This Plot.")

    fig = figure(
        apctx=ctx,
        title=f"{ctx['_sname']}:: One Minute Interval Plot",
        subtitle=(
            f"Valid between {ctx['sts']:%-d %b %Y %-I:%M %p} and "
            f"{ctx['ets']:%-d %b %Y %-I:%M %p} Central Time"
        ),
    )
    ax = fig.subplots(2, 1, sharex=True)
    ax[0].plot(df.index, c2f(df["tair_c_avg_qc"]), color="r")
    ax[0].set_ylabel(r"Air Temperature [$^\circ$F]", color="r")
    ax[0].grid(True)
    if ax[0].get_ylim()[0] < 40:
        ax[0].axhline(32, linestyle="--", lw=2, color="tan")

    ax2 = ax[0].twinx()
    ax2.plot(df.index, df["slrkj_tot_qc"].values / 60.0 * 1000, color="k")
    ax2.set_ylabel("Solar Radiation [$W m^{-2}$]")
    xaxis_magic(ctx, ax[0])

    ax[1].bar(
        df.index,
        df["ws_mph_max_qc"],
        width=1 / 1440.0,
        zorder=3,
        color="r",
        label="Gust",
    )
    ax[1].bar(
        df.index,
        df["ws_mph_qc"],
        width=1 / 1440.0,
        zorder=4,
        color="b",
        label="Avg",
    )
    ax[1].grid(True)
    ax[1].set_ylabel("Wind Speed [MPH]")
    ax[1].legend(loc="best", ncol=2)

    return fig, df


def plot1(ctx):
    """Do main plotting logic"""
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            "SELECT * from sm_hourly WHERE "
            "station = %s and valid BETWEEN %s and %s ORDER by valid ASC",
            conn,
            params=(ctx["station"], ctx["sts"], ctx["ets"]),
            index_col="valid",
        )
    if df.empty:
        raise NoDataFound("No Data Found for This Plot.")
    solar_wm2 = df["slrkj_tot_qc"] / 3600.0 * 1000.0
    d12sm = df["vwc12_qc"]
    d12t = df["t12_c_avg_qc"]
    d24t = df["t24_c_avg_qc"]
    d50t = df["t50_c_avg_qc"]
    d24sm = df["vwc24_qc"]
    d50sm = df["vwc50_qc"]
    rain = df["rain_in_tot_qc"]
    tair = df["tair_c_avg_qc"]
    d04t = df["t4_c_avg_qc"]
    valid = df.index

    fig = figure(
        title=f"ISUSM Station: {ctx['_sname']} Timeseries",
        apctx=ctx,
    )
    ax = fig.subplots(3, 1, sharex=True)
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
    ax[0].set_ylabel("Volumetric\nSoil Water Content [%]")

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

    handles = []
    labels = []
    if not tair.isnull().all():
        (l1,) = ax[2].plot(
            valid, c2f(tair), linewidth=2, color="blue", zorder=2
        )
        handles.append(l1)
        labels.append("Air")
    if not d04t.isnull().all():
        (l2,) = ax[2].plot(
            valid, c2f(d04t), linewidth=2, color="brown", zorder=2
        )
        handles.append(l2)
        labels.append('4" Soil')
    handles.append(l3)
    labels.append("Solar Radiation")
    ax[2].grid(True)
    ax[2].legend(
        handles,
        labels,
        bbox_to_anchor=(0.5, 1.1),
        loc="center",
        ncol=3,
    )
    ax[2].set_ylabel(r"Temperature $^\circ$F")

    ax[2].set_zorder(ax2.get_zorder() + 1)
    ax[2].patch.set_visible(False)
    ax[0].set_xlim(df.index.min(), df.index.max())
    xaxis_magic(ctx, ax[2])

    return fig, df


def xaxis_magic(ctx, ax):
    """Do the xaxis magic."""
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
                "%-I %p\n%-d %b", tz=pytz.timezone("America/Chicago")
            )
        )


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    ctx["pgconn"] = get_dbconn("isuag")

    if ctx["opt"] == "1":
        fig, df = plot1(ctx)
    elif ctx["opt"] == "2":
        fig, df = plot2(ctx)
    elif ctx["opt"] == "at":
        fig, df = plot_at(ctx)
    elif ctx["opt"] == "sm":
        fig, df = plot_sm(ctx)
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
    elif ctx["opt"] == "10":
        fig, df = make_inversion_plot(ctx)
    else:  # 11
        fig, df = make_inversion_timing(ctx)

    # removal of timestamps, sigh
    df = df.reset_index()
    for col in [
        "valid",
        "ws_mph_tmx",
        "valid",
        "ws_mph_tmx_qc",
        "tair_c_tmn",
        "tair_c_tmx",
        "tair_c_tmx_qc",
        "tair_c_tmn_qc",
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
    plotter(
        {
            "station": "BOOI4",
            "opt": "9",
        }
    )
