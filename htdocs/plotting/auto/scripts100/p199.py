"""
This application generates maps of daily ISU
Soil Moisture Network Data.
"""
import datetime

import pandas as pd
from metpy.units import units
from pyiem.exceptions import NoDataFound
from pyiem.network import Table as NetworkTable  # This is needed.
from pyiem.plot.geoplot import MapPlot
from pyiem.tracker import loadqc
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, mm2inch

PLOTTYPES = {
    "1": "Max/Min 4 Inch Soil Temps",
    "2": "Max/Min Air Temperature",
    "3": "Average 4 Inch Soil Temp",
    "4": "Solar Radiation",
    "5": "Potential Evapotranspiration",
    "6": "DPrecipitation",
    "7": "Peak Wind Gust",
    "8": "Average Wind Speed",
    "9": "Plant Available Soil Water (6-30 inches)",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    ets = datetime.datetime.now().replace(minute=0)
    sts = ets - datetime.timedelta(days=1)
    desc["arguments"] = [
        dict(
            type="select",
            name="opt",
            default="1",
            options=PLOTTYPES,
            label="Select Plot Type:",
        ),
        dict(
            type="date",
            name="date",
            default=sts.strftime("%Y/%m/%d"),
            label="Select Date",
            min="2012/01/01",
        ),
    ]
    return desc


def plot1(ctx):
    """Daily four inch depth high/low temp."""
    dt = datetime.datetime(
        ctx["date"].year, ctx["date"].month, ctx["date"].day
    )
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            """
            SELECT station, max(t4_c_avg_qc) as max_tsoil_c,
            min(t4_c_avg_qc) as min_tsoil_c from sm_hourly WHERE
            valid BETWEEN %s and %s and t4_c_avg_qc is not null
            GROUP by station
        """,
            conn,
            params=(dt, dt + datetime.timedelta(hours=24)),
            index_col="station",
        )
    if df.empty:
        raise NoDataFound("No Data Found for This Plot.")
    df["max_tsoil_f"] = (
        (df["max_tsoil_c"].values * units("degC")).to(units("degF")).m
    )
    df["min_tsoil_f"] = (
        (df["min_tsoil_c"].values * units("degC")).to(units("degF")).m
    )

    data = []
    for station, row in df.iterrows():
        if station not in ctx["nt"].sts:
            continue
        if ctx["qc"].get(station, {}).get("soil4", False):
            continue
        data.append(
            {
                "lon": ctx["nt"].sts[station]["lon"],
                "lat": ctx["nt"].sts[station]["lat"],
                "tmpf": row["max_tsoil_f"],
                "dwpf": row["min_tsoil_f"],
                "id": ctx["nt"].sts[station]["plot_name"],
                "id_color": "k",
            }
        )

    return data, df


def plot2(ctx):
    """Daily air high/low temp."""
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            """
            SELECT station, tair_c_max_qc,
            tair_c_min_qc from sm_daily WHERE
            valid = %s and tair_c_max_qc is not null and
            tair_c_min_qc is not null
        """,
            conn,
            params=(ctx["date"],),
            index_col="station",
        )
    if df.empty:
        raise NoDataFound("No Data Found for This Plot.")
    df["high_f"] = (
        (df["tair_c_max_qc"].values * units("degC")).to(units("degF")).m
    )
    df["low_f"] = (
        (df["tair_c_min_qc"].values * units("degC")).to(units("degF")).m
    )

    data = []
    for station, row in df.iterrows():
        if station not in ctx["nt"].sts:
            continue
        data.append(
            {
                "lon": ctx["nt"].sts[station]["lon"],
                "lat": ctx["nt"].sts[station]["lat"],
                "tmpf": row["high_f"],
                "dwpf": row["low_f"],
                "id": ctx["nt"].sts[station]["plot_name"],
                "id_color": "k",
            }
        )

    return data, df


def plot3(ctx):
    """Daily air high/low temp."""
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            """
            SELECT station, t4_c_avg_qc from sm_daily WHERE
            valid = %s and t4_c_avg_qc is not null
        """,
            conn,
            params=(ctx["date"],),
            index_col="station",
        )
    if df.empty:
        raise NoDataFound("No Data Found for This Plot.")
    df["soil4_avg_f"] = (
        (df["t4_c_avg_qc"].values * units("degC")).to(units("degF")).m
    )

    data = []
    for station, row in df.iterrows():
        if station not in ctx["nt"].sts:
            continue
        data.append(
            {
                "lon": ctx["nt"].sts[station]["lon"],
                "lat": ctx["nt"].sts[station]["lat"],
                "tmpf": row["soil4_avg_f"],
                "id": ctx["nt"].sts[station]["plot_name"],
                "id_color": "k",
            }
        )

    return data, df


def plot4(ctx):
    """Daily rad."""
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            """
            SELECT station, slrkj_tot_qc from sm_daily WHERE
            valid = %s and slrkj_tot_qc is not null
        """,
            conn,
            params=(ctx["date"],),
            index_col="station",
        )
    if df.empty:
        raise NoDataFound("No Data Found for This Plot.")

    data = []
    for station, row in df.iterrows():
        if station not in ctx["nt"].sts:
            continue
        data.append(
            {
                "lon": ctx["nt"].sts[station]["lon"],
                "lat": ctx["nt"].sts[station]["lat"],
                "tmpf": row["slrkj_tot_qc"] / 1000.0,
                "id": ctx["nt"].sts[station]["plot_name"],
                "id_color": "k",
            }
        )

    return data, df


def plot5(ctx, col):
    """Daily ET."""
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            f"SELECT station, {col}_qc from sm_daily WHERE valid = %s and "
            f"{col}_qc >= 0",
            conn,
            params=(ctx["date"],),
            index_col="station",
        )
    if df.empty:
        raise NoDataFound("No Data Found for This Plot.")
    if col == "dailyet":
        df["data"] = mm2inch(df["dailyet_qc"].values)
    else:
        df["data"] = df[col + "_qc"].values

    data = []
    for station, row in df.iterrows():
        if station not in ctx["nt"].sts:
            continue
        data.append(
            {
                "lon": ctx["nt"].sts[station]["lon"],
                "lat": ctx["nt"].sts[station]["lat"],
                "tmpf": row["data"],
                "tmpf_format": "%.02f",
                "id": ctx["nt"].sts[station]["plot_name"],
                "id_color": "k",
            }
        )
    return data, df


def plot7(ctx):
    """Daily peak wind."""
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            """
            SELECT station, ws_mph_max_qc, to_char(ws_mph_tmx, 'HH24MI')
            as time from sm_daily WHERE
            valid = %s and ws_mph_max_qc is not null
        """,
            conn,
            params=(ctx["date"],),
            index_col="station",
        )
    if df.empty:
        raise NoDataFound("No Data Found for This Plot.")

    data = []
    for station, row in df.iterrows():
        if station not in ctx["nt"].sts:
            continue
        data.append(
            {
                "lon": ctx["nt"].sts[station]["lon"],
                "lat": ctx["nt"].sts[station]["lat"],
                "tmpf": row["ws_mph_max_qc"],
                #  'dwpf': row['time'],  backend bug plotting non-numbers
                "id": ctx["nt"].sts[station]["plot_name"],
                "id_color": "k",
            }
        )

    return data, df


def plot8(ctx):
    """Daily peak wind."""
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            "SELECT station, ws_mph_qc from sm_daily WHERE valid = %s and "
            "ws_mph_qc is not null",
            conn,
            params=(ctx["date"],),
            index_col="station",
        )
    if df.empty:
        raise NoDataFound("No Data Found for This Plot.")

    data = []
    for station, row in df.iterrows():
        if station not in ctx["nt"].sts:
            continue
        data.append(
            {
                "lon": ctx["nt"].sts[station]["lon"],
                "lat": ctx["nt"].sts[station]["lat"],
                "tmpf": row["ws_mph_qc"],
                #  'dwpf': row['time'],  backend bug plotting non-numbers
                "id": ctx["nt"].sts[station]["plot_name"],
                "id_color": "k",
            }
        )

    return data, df


def plot9(ctx):
    """Daily peak wind."""
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            "SELECT station, vwc12_qc, vwc24_qc from "
            "sm_daily WHERE valid = %s and vwc24_qc is not null "
            "and station != 'FRUI4'",
            conn,
            params=(ctx["date"],),
            index_col="station",
        )
    if df.empty:
        raise NoDataFound("No Data Found for This Plot.")
    df["vwc_12"] = df["vwc12_qc"].clip(0.1, 0.45)
    df["vwc_24"] = df["vwc24_qc"].clip(0.1, 0.45)
    df["val"] = (df["vwc_12"] * 12 + df["vwc_24"] * 12) - (24 * 0.1)
    df = df[~df["val"].isna()]

    data = []
    for station, row in df.iterrows():
        if station not in ctx["nt"].sts:
            continue
        data.append(
            {
                "lon": ctx["nt"].sts[station]["lon"],
                "lat": ctx["nt"].sts[station]["lat"],
                "tmpf": row["val"],
                "tmpf_format": "%.02f",
                "id": ctx["nt"].sts[station]["plot_name"],
                "id_color": "k",
            }
        )

    return data, df


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    ctx["qc"] = loadqc(date=ctx["date"])
    ctx["nt"] = NetworkTable("ISUSM")
    if not ctx["nt"].sts:
        raise NoDataFound("No station metadata found.")
    # Adjust stations to make some room
    ctx["nt"].sts["BOOI4"]["lon"] -= 0.15
    ctx["nt"].sts["BOOI4"]["lat"] -= 0.15
    ctx["nt"].sts["AHTI4"]["lon"] += 0.25
    ctx["nt"].sts["AHTI4"]["lat"] += 0.25

    ctx["nt"].sts["DONI4"]["lon"] += 0.05
    ctx["nt"].sts["DONI4"]["lat"] -= 0.2

    if ctx["opt"] == "1":
        title = "ISU Soil Moisture Max/Min 4 Inch Soil Temperature"
        subtitle = "based on available hourly observations"
        data, df = plot1(ctx)
    elif ctx["opt"] == "2":
        title = "ISU Soil Moisture Max/Min Air Temperature"
        subtitle = "based on available daily summary data"
        data, df = plot2(ctx)
    elif ctx["opt"] == "3":
        title = "ISU Soil Moisture Average 4 Inch Soil Temperature"
        subtitle = "based on available daily summary data"
        data, df = plot3(ctx)
    elif ctx["opt"] == "4":
        title = "ISU Soil Moisture Solar Radiation [MJ]"
        subtitle = "based on available daily summary data"
        data, df = plot4(ctx)
    elif ctx["opt"] == "5":
        title = "ISU Soil Moisture Potential Evapotranspiration [inch]"
        subtitle = "based on available daily summary data"
        data, df = plot5(ctx, "dailyet")
    elif ctx["opt"] == "6":
        title = "ISU Soil Moisture Precipitation [inch]"
        subtitle = (
            "based on available daily summary data, liquid equiv of snow "
            "estimated"
        )
        data, df = plot5(ctx, "rain_in_tot")
    elif ctx["opt"] == "7":
        title = "ISU Soil Moisture Peak Wind Gust [MPH]"
        subtitle = "based on available daily summary data"
        data, df = plot7(ctx)
    elif ctx["opt"] == "8":
        title = "ISU Soil Moisture Average Wind Speed [MPH]"
        subtitle = "based on available daily summary data"
        data, df = plot8(ctx)
    else:  # 9
        title = (
            "ISU Soil Moisture Plant Available Soil Water (6-30 inch) [inch]"
        )
        subtitle = (
            'based on available daily summary data, 10.8" theoretical max '
            "assuming 45% capacity"
        )
        data, df = plot9(ctx)

    tle = ctx["date"].strftime("%b %-d, %Y")
    mp = MapPlot(
        apctx=ctx,
        sector="iowa",
        continentalcolor="white",
        nocaption=True,
        title=f"{tle} {title}",
        subtitle=subtitle,
    )
    mp.drawcounties("#EEEEEE")
    mp.plot_station(data, fontsize=12)

    return mp.fig, df


if __name__ == "__main__":
    plotter(dict(opt="5", date="2019-04-21"))
