"""
Mine grid point extracted values for our good and the good of the IEM
Use Unidata's motherlode server :)

Called from RUN_40_AFTER.sh
"""

import sys
from datetime import datetime, timedelta, timezone
from io import StringIO
from zoneinfo import ZoneInfo

import click
import httpx
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.network import Table as NetworkTable
from pyiem.reference import ISO8601
from pyiem.util import logger
from sqlalchemy.engine import Connection

LOG = logger()
NT = NetworkTable("IA_ASOS")

BASE_URL = "https://thredds.ucar.edu/thredds/ncss/grid/grib/NCEP/"
BASE_URL2 = (
    "https://thredds-test.unidata.ucar.edu/thredds/ncss/grid/grib/NCEP/"
)
URLS = {
    "NAM": (
        "NAM/CONUS_12km/conduit/NAM_CONUS_12km_conduit_%Y%m%d_%H00.grib2/GC"
    ),
    "GFS": "GFS/Global_0p5deg/GFS_Global_0p5deg_%Y%m%d_%H00.grib2/GC",
    "RAP": "RAP/CONUS_13km/RR_CONUS_13km_%Y%m%d_%H00.grib2/GC",
}
VLOOKUP = {
    "sbcape": {
        "NAM": "Convective_available_potential_energy_surface",
        "GFS": "Convective_available_potential_energy_surface",
        "RAP": "Convective_available_potential_energy_surface",
    },
    "sbcin": {
        "NAM": "Convective_inhibition_surface",
        "GFS": "Convective_inhibition_surface",
        "RAP": "Convective_inhibition_surface",
    },
    "pwater": {
        "NAM": "Precipitable_water_entire_atmosphere_single_layer",
        "GFS": "Precipitable_water_entire_atmosphere_single_layer",
        "RAP": "Precipitable_water_entire_atmosphere_single_layer",
    },
}


def xref(row, varname, model):
    """Safer lookup"""
    rowkey = VLOOKUP[varname][model]
    if rowkey not in row:
        LOG.warning("Failed to find %s in %s\nrow:%s", varname, model, row)
        sys.exit()
    return row[rowkey]


def run(conn: Connection, model, station, lon, lat, ts):
    """
    Ingest the model data for a given Model, stationid and timestamp
    """

    vstring = ""
    for val in VLOOKUP.values():
        if val[model] is not None:
            vstring += f"var={val[model]}&"

    host = (
        BASE_URL
        if (datetime.now(timezone.utc) - ts).total_seconds() < 86400
        else BASE_URL2
    )
    url = (
        f"{host}{ts.strftime(URLS[model])}?{vstring}latitude={lat}&"
        f"longitude={lon}&temporal=all&vertCoord="
        "&accept=csv&point=true"
    )
    try:
        fp = httpx.get(url, timeout=120)
        if fp.status_code == 404:
            LOG.info(url)
            LOG.warning("Grid %s %s missing", model, ts)
            return 0
        sio = StringIO(fp.text)
    except Exception as exp:
        print(exp)
        print(url)
        LOG.warning(
            "FAIL ts: %s station: %s model: %s",
            ts.strftime("%Y-%m-%d %H"),
            station,
            model,
        )
        return None

    table = f"model_gridpoint_{ts.year}"
    sql = (
        "DELETE from {table} WHERE station = :station "
        "and model = :model and runtime = :runtime"
    )
    args = {"station": station, "model": model, "runtime": ts}
    res = conn.execute(sql_helper(sql, table=table), args)
    if res.rowcount > 0:
        LOG.warning(
            "Deleted %s rows for ts: %s station: %s model: %s",
            res.rowcount,
            ts,
            station,
            model,
        )

    count = 0
    sio.seek(0)
    df = pd.read_csv(sio)
    for _, row in df.iterrows():
        for k in row.keys():
            row[k[: k.find("[")]] = row[k]
        sbcape = xref(row, "sbcape", model)
        sbcin = xref(row, "sbcin", model)
        pwater = xref(row, "pwater", model)
        fts = datetime.strptime(row["time"], ISO8601)
        fts = fts.replace(tzinfo=ZoneInfo("UTC"))
        sql = """INSERT into {table} (station, model, runtime,
              ftime, sbcape, sbcin, pwater)
              VALUES (:station, :model, :runtime, :ftime, :sbcape, :sbcin,
              :pwater)"""
        args = {
            "station": station,
            "model": model,
            "runtime": ts,
            "ftime": fts,
            "sbcape": sbcape,
            "sbcin": sbcin,
            "pwater": pwater,
        }
        conn.execute(sql_helper(sql, table=table), args)
        count += 1
    return count


def run_model(conn: Connection, model, runtime):
    """Actually do a model and timestamp"""
    for sid in NT.sts:
        cnt = run(
            conn,
            model,
            f"K{sid}",
            NT.sts[sid]["lon"],
            NT.sts[sid]["lat"],
            runtime,
        )
        if cnt == 0:
            LOG.warning("No data K%s %s %s", sid, runtime, model)


def check_and_run(conn: Connection, model, runtime):
    """Check the database for missing data"""
    table = f"model_gridpoint_{runtime.year}"
    res = conn.execute(
        sql_helper(
            "SELECT * from {table} WHERE runtime = :rt and model = :model",
            table=table,
        ),
        {"rt": runtime, "model": model},
    )
    if res.rowcount < 10:
        LOG.warning(
            "Rerunning %s [runtime=%s] due to rowcount %s",
            model,
            runtime,
            res.rowcount,
        )
        run_model(conn, model, runtime)


@click.command()
@click.option("--valid", type=click.DateTime(), required=True)
def main(valid: datetime):
    """Do Something"""
    valid = valid.replace(tzinfo=timezone.utc)
    with get_sqlalchemy_conn("mos") as conn:
        if valid.hour % 6 == 0:
            ts = valid - timedelta(hours=6)
            for model in ["GFS", "NAM"]:
                run_model(conn, model, ts)
                conn.commit()
                check_and_run(conn, model, ts - timedelta(days=7))
                conn.commit()

        ts = valid - timedelta(hours=2)
        run_model(conn, "RAP", ts)
        conn.commit()
        check_and_run(conn, "RAP", ts - timedelta(days=7))
        conn.commit()


if __name__ == "__main__":
    main()
