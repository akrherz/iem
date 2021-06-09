"""ISU Soil Moisture Network Daily Plots."""
import datetime

from pandas.io.sql import read_sql
from metpy.units import units
from pyiem.plot.geoplot import MapPlot
from pyiem.util import get_autoplot_context, get_dbconn, mm2inch
from pyiem.network import Table as NetworkTable  # This is needed.
from pyiem.tracker import loadqc
from pyiem.exceptions import NoDataFound


PLOTTYPES = {
    "1": "Daily Max/Min 4 Inch Soil Temps",
    "2": "Daily Max/Min Air Temperature",
    "3": "Daily Average 4 Inch Soil Temp",
    "4": "Daily Solar Radiation",
    "5": "Daily Potential Evapotranspiration",
    "6": "Daily Precipitation",
    "7": "Peak Wind Gust",
    "8": "Daily Average Wind Speed",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This application generates maps of daily ISU
    Soil Moisture Network Data."""
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
    df = read_sql(
        """
        SELECT station, max(tsoil_c_avg_qc) as max_tsoil_c,
        min(tsoil_c_avg_qc) as min_tsoil_c from sm_hourly WHERE
        valid BETWEEN %s and %s and tsoil_c_avg_qc is not null
        GROUP by station
    """,
        ctx["pgconn"],
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
    df = read_sql(
        """
        SELECT station, tair_c_max_qc,
        tair_c_min_qc from sm_daily WHERE
        valid = %s and tair_c_max_qc is not null and
        tair_c_min_qc is not null
    """,
        ctx["pgconn"],
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
    df = read_sql(
        """
        SELECT station, tsoil_c_avg_qc from sm_daily WHERE
        valid = %s and tsoil_c_avg_qc is not null
    """,
        ctx["pgconn"],
        params=(ctx["date"],),
        index_col="station",
    )
    if df.empty:
        raise NoDataFound("No Data Found for This Plot.")
    df["soil4_avg_f"] = (
        (df["tsoil_c_avg_qc"].values * units("degC")).to(units("degF")).m
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
    df = read_sql(
        """
        SELECT station, slrkj_tot_qc from sm_daily WHERE
        valid = %s and slrkj_tot_qc is not null
    """,
        ctx["pgconn"],
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
    df = read_sql(
        f"SELECT station, {col}_qc from sm_daily WHERE valid = %s and "
        f"{col}_qc >= 0",
        ctx["pgconn"],
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
    df = read_sql(
        """
        SELECT station, ws_mps_max_qc, to_char(ws_mps_tmx, 'HH24MI') as time
        from sm_daily WHERE
        valid = %s and ws_mps_max_qc is not null
    """,
        ctx["pgconn"],
        params=(ctx["date"],),
        index_col="station",
    )
    if df.empty:
        raise NoDataFound("No Data Found for This Plot.")
    df["gust_mph"] = (
        (df["ws_mps_max_qc"].values * units("meter / second"))
        .to(units("mph"))
        .m
    )

    data = []
    for station, row in df.iterrows():
        if station not in ctx["nt"].sts:
            continue
        data.append(
            {
                "lon": ctx["nt"].sts[station]["lon"],
                "lat": ctx["nt"].sts[station]["lat"],
                "tmpf": row["gust_mph"],
                #  'dwpf': row['time'],  backend bug plotting non-numbers
                "id": ctx["nt"].sts[station]["plot_name"],
                "id_color": "k",
            }
        )

    return data, df


def plot8(ctx):
    """Daily peak wind."""
    df = read_sql(
        """
        SELECT station, ws_mps_s_wvt_qc
        from sm_daily WHERE
        valid = %s and ws_mps_s_wvt_qc is not null
    """,
        ctx["pgconn"],
        params=(ctx["date"],),
        index_col="station",
    )
    if df.empty:
        raise NoDataFound("No Data Found for This Plot.")
    df["wind_mph"] = (
        (df["ws_mps_s_wvt_qc"].values * units("meter / second"))
        .to(units("mph"))
        .m
    )

    data = []
    for station, row in df.iterrows():
        if station not in ctx["nt"].sts:
            continue
        data.append(
            {
                "lon": ctx["nt"].sts[station]["lon"],
                "lat": ctx["nt"].sts[station]["lat"],
                "tmpf": row["wind_mph"],
                #  'dwpf': row['time'],  backend bug plotting non-numbers
                "id": ctx["nt"].sts[station]["plot_name"],
                "id_color": "k",
            }
        )

    return data, df


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    ctx["qc"] = loadqc(date=ctx["date"])
    ctx["pgconn"] = get_dbconn("isuag")
    ctx["nt"] = NetworkTable("ISUSM")
    if not ctx["nt"].sts:
        raise NoDataFound("No station metadata found.")
    # Adjust stations to make some room
    ctx["nt"].sts["BOOI4"]["lon"] -= 0.15
    ctx["nt"].sts["BOOI4"]["lat"] -= 0.15
    ctx["nt"].sts["AHTI4"]["lon"] += 0.25
    ctx["nt"].sts["AHTI4"]["lat"] += 0.25

    title = "TBD"
    subtitle = "TBD"
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

    tle = ctx["date"].strftime("%b %-d, %Y")
    mp = MapPlot(
        sector="iowa",
        continentalcolor="white",
        nocaption=True,
        title="%s %s" % (tle, title),
        subtitle=subtitle,
    )
    mp.drawcounties("#EEEEEE")
    mp.plot_station(data, fontsize=12)

    return mp.fig, df


if __name__ == "__main__":
    plotter(dict(opt="5", date="2019-04-21"))
