"""Generation of National Mesonet Project CSV File.

https://mesonet.agron.iastate.edu/agclimate/isusm.csv
"""
from datetime import datetime
from io import StringIO

import numpy as np
import pandas as pd
from metpy.units import units
from pyiem.network import Table as NetworkTable
from pyiem.util import convert_value, get_sqlalchemy_conn
from pyiem.webutil import iemapp

INVERSION = [
    "BOOI4",
    "CAMI4",
    "CRFI4",
]


def nan(val):
    """Convert to NaN, if necessary."""
    return np.nan if val is None else val


def p(val, prec, minv, maxv):
    """rounder"""
    if pd.isna(val) or val < minv or val > maxv:
        return ""
    return str(round(val, prec))


def p3(val, prec, minv, maxv):
    """rounder"""
    if pd.isna(val) or val < minv or val > maxv:
        return ""
    return str(round(val * 100.0, prec))


def p2(val, prec, minv, maxv):
    """rounder"""
    if pd.isna(val) or val < minv or val > maxv:
        return ""
    return str(round(convert_value(val, "degC", "degK"), prec))


def do_temp_rh(sid, row):
    """Do air temp and RH%."""
    heights = [
        "2",
    ]
    temps = [
        p2(row["tair_c_avg"], 1, -90, 90),
    ]
    rhs = [
        p(row["rh_avg"], 1, 0, 100),
    ]
    if sid in INVERSION:
        with get_sqlalchemy_conn("isuag") as conn:
            df = pd.read_sql(
                "SELECT * from sm_inversion WHERE station = %s and "
                "valid > %s - '4 hours'::interval ORDER by valid DESC LIMIT 1",
                conn,
                params=(sid, row["valid"]),
            )
        if not df.empty:
            row2 = df.iloc[0]
            for foot, col in [[1.5, "15"], [5, "5"], [10, "10"]]:
                depth_mm = convert_value(foot * 12, "inch", "meter")
                heights.append(f"{depth_mm:.3f}")
                temps.append(p2(row2[f"tair_{col}_c_avg"], 1, -90, 90))
                rhs.append("")

    return "%s#%s#%s" % (
        ";".join(heights),
        ";".join(temps),
        ";".join(rhs),
    )


def do_soil_moisture(row):
    """Do necessary conversions for soil moisture."""
    data = row.to_dict()
    depths = []
    temps = []
    moisture = []
    for depth in [2, 4, 6, 8, 12, 16, 20, 24, 30, 40]:
        # CS655
        t = data.get(f"t{depth}_c_avg")
        sv_t = data.get(f"sv_t{depth}")
        vwc = data.get(f"vwc{depth}")
        sv_vwc = data.get(f"sv_vwc{depth}")
        if pd.isna([t, sv_t, vwc, sv_vwc]).all():
            continue
        depth_mm = convert_value(depth, "inch", "meter")
        for _t, _v in [[t, vwc], [sv_t, sv_vwc]]:
            if pd.isna([_t, _v]).all():
                continue
            depths.append(f"{depth_mm:.3f}")
            temps.append(p2(_t, 3, -90, 90))
            moisture.append(p3(_v, 2, 0, 100))

    if not depths:
        return ""
    return "%s#%s#%s" % (
        ";".join(depths),
        ";".join(temps),
        ";".join(moisture),
    )


def use_table(sio):
    """Process for the given table."""
    nt = NetworkTable("ISUSM")
    table = f"sm_minute_{datetime.now().year}"
    with get_sqlalchemy_conn("isuag") as conn:
        obsdf = pd.read_sql(
            f"""
            WITH latest as (
                SELECT station, valid,
                row_number() OVER (PARTITION by station ORDER by valid DESC)
                from {table} WHERE valid > now() - '48 hours'::interval
                and valid < now()
            ), agg as (
                select station, valid from latest where row_number = 1
            )
            select s.*, s.valid at time zone 'UTC' as utc_valid,
            case when s.valid = a.valid then true else false end as is_last
            from {table} s, agg a WHERE s.station = a.station
            and s.valid > (a.valid - '1 hour'::interval) and s.valid <= a.valid
            """,
            conn,
            index_col=None,
        )
    if obsdf[obsdf["is_last"]].empty:
        return
    lastob = obsdf[obsdf["is_last"]].set_index("station")
    hrtotal = (
        obsdf[["station", "rain_in_tot", "slrkj_tot"]].groupby("station").sum()
    )
    for sid, row in lastob.iterrows():
        hr_row = hrtotal.loc[sid]
        sio.write(
            ("%s,%.4f,%.4f,%s,%.1f,%s,%s,%s,%s,3#%s#%s#%s\n")
            % (
                sid,
                nt.sts[sid]["lat"],
                nt.sts[sid]["lon"],
                row["utc_valid"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                nt.sts[sid]["elevation"],
                do_soil_moisture(row),
                p(hr_row["slrkj_tot"] * 1000.0 / 3600.0, 1, 0, 1600),
                do_temp_rh(sid, row),
                p(
                    (nan(hr_row["rain_in_tot"]) * units("inch"))
                    .to(units("cm"))
                    .m,
                    2,
                    0,
                    100,
                ),
                p(
                    (nan(row["ws_mph"]) * units("mph"))
                    .to(units("meter / second"))
                    .m,
                    2,
                    0,
                    100,
                ),
                p(
                    (nan(row["ws_mph_max"]) * units("mph"))
                    .to(units("meter / second"))
                    .m,
                    2,
                    0,
                    100,
                ),
                p(row["winddir_d1_wvt"], 2, 0, 360),
            )
        )


def do_output(sio):
    """Do as I say"""
    sio.write(
        "station_id,LAT [degN],LON [degE],date_time,ELEV [m],"
        "depth [m]#SOILT [K]#SOILMP [%],"
        "GSRD[1]H [W/m^2],height [m]#T [K]#RH [%],"
        "PCP[1]H [mm],"
        "height [m]#FF[1]H [m/s]#FFMAX[1]H [m/s]#DD[1]H [degN]\n"
    )

    use_table(sio)
    sio.write(".EOO\n")


@iemapp()
def application(_environ, start_response):
    """Do Something"""
    headers = [("Content-type", "text/csv;header=present")]
    start_response("200 OK", headers)
    sio = StringIO()
    do_output(sio)
    return [sio.getvalue().encode("ascii")]


def test_basic():
    """Test that we can do things we need to do!"""
    sio = StringIO()
    do_output(sio)
    with open("/tmp/pytest_isusm.csv", "w", encoding="utf-8") as fh:
        fh.write(sio.getvalue())
    assert False
