"""Process the US Climate Reference Network.

Called from RUN_20_AFTER.sh
"""

import glob
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import click
import httpx
import pandas as pd
from metpy.units import units
from psycopg.rows import dict_row
from pyiem.database import get_dbconn
from pyiem.observation import Observation
from pyiem.util import logger

LOG = logger()
BASE = "/mesonet/tmp/uscrn"
URI = "https://www.ncei.noaa.gov/pub/data/uscrn/products/subhourly01"
FTP = "ftp://ftp.ncei.noaa.gov/pub/data/uscrn/products/subhourly01"


def n2n(val):
    """yawn"""
    if pd.isnull(val):
        return None
    return val


def is_within(val, floor, ceiling):
    """Nulls"""
    if val is None or pd.isnull(val):
        return None
    if val < floor or val >= ceiling:
        return None
    return val


def process_file(icursor, ocursor, year, filename, size, reprocess):
    """Ingest these files, please
    1    WBANNO                         XXXXX
    2    UTC_DATE                       YYYYMMDD
    3    UTC_TIME                       HHmm
    4    LST_DATE                       YYYYMMDD
    5    LST_TIME                       HHmm
    6    CRX_VN                         XXXXXX
    7    LONGITUDE                      Decimal_degrees
    8    LATITUDE                       Decimal_degrees
    9    AIR_TEMPERATURE                Celsius
    10   PRECIPITATION                  mm
    11   SOLAR_RADIATION                W/m^2
    12   SR_FLAG                        X
    13   SURFACE_TEMPERATURE            Celsius
    14   ST_TYPE                        X
    15   ST_FLAG                        X
    16   RELATIVE_HUMIDITY              %
    17   RH_FLAG                        X
    18   SOIL_MOISTURE_5                m^3/m^3
    19   SOIL_TEMPERATURE_5             Celsius
    20   WETNESS                        Ohms
    21   WET_FLAG                       X
    22   WIND_1_5                       m/s
    23   WIND_FLAG                      X
    """
    with open(filename, "rb") as fp:
        if size > 0:
            fp.seek(os.stat(filename).st_size - size)
        df = pd.read_csv(
            fp,
            low_memory=False,
            sep=r"\s+",
            names=[
                "WBANNO",
                "UTC_DATE",
                "UTC_TIME",
                "LST_DATE",
                "LST_TIME",
                "CRX_VN",
                "LON",
                "LAT",
                "TMPC",
                "PRECIP_MM",
                "SRAD",
                "SR_FLAG",
                "SKINC",
                "ST_TYPE",
                "ST_FLAG",
                "RH",
                "RH_FLAG",
                "VSM5",
                "SOILC5",
                "WETNESS",
                "WET_FLAG",
                "SMPS",
                "SMPS_FLAG",
            ],
            na_values={
                "TMPC": "-9999",
                "PRECIP_MM": "-9999",
                "SRAD": "-99999",
                "SKINC": "-9999",
                "RH": "-9999",
                "VSM5": "-99",
                "SOILC5": "-9999",
                "WETNESS": "-9999",
                "SMPS": "-99",
            },
            converters={"WBANNO": str, "UTC_TIME": str},
        )
    if reprocess and not df.empty:
        ocursor.execute(
            f"DELETE from t{year} WHERE station = %s",
            (df.iloc[0]["WBANNO"],),
        )
        LOG.info(
            "Removed %s rows %s %s",
            ocursor.rowcount,
            year,
            df.iloc[0]["WBANNO"],
        )
    for _, row in df.iterrows():
        valid = datetime.strptime(
            "%s %s" % (row["UTC_DATE"], row["UTC_TIME"]), "%Y%m%d %H%M"
        )
        valid = valid.replace(tzinfo=ZoneInfo("UTC"))
        ob = Observation(str(row["WBANNO"]), "USCRN", valid)
        ob.data["tmpf"] = is_within(
            (float(row["TMPC"]) * units.degC).to(units.degF).magnitude,
            -100,
            150,
        )
        ob.data["pcounter"] = is_within(
            (float(row["PRECIP_MM"]) * units("mm")).to(units.inch).magnitude,
            0,
            900,
        )
        ob.data["srad"] = is_within(row["SRAD"], 0, 2000)
        ob.data["tsf0"] = is_within(
            (float(row["SKINC"]) * units.degC).to(units.degF).magnitude,
            -100,
            200,
        )
        ob.data["relh"] = is_within(row["RH"], 1, 100.1)
        ob.data["c1smv"] = is_within(row["VSM5"], 0.01, 1.01)
        ob.data["c1tmpf"] = is_within(
            (float(row["SOILC5"]) * units.degC).to(units.degF).magnitude,
            -100,
            200,
        )
        ob.data["sknt"] = is_within(
            (float(row["SMPS"]) * units("m/s"))
            .to(units("miles per hour"))
            .magnitude,
            0,
            200,
        )
        ob.save(icursor, skip_current=reprocess)
        table = f"t{valid.year}"
        if not reprocess:
            ocursor.execute(
                f"DELETE from {table} WHERE station = %s and valid = %s",
                (row["WBANNO"], valid),
            )
        ocursor.execute(
            f"""
        INSERT into {table} (station, valid, tmpc, precip_mm, srad,
        srad_flag, skinc, skinc_flag, skinc_type, rh, rh_flag, vsm5,
        soilc5, wetness, wetness_flag, wind_mps, wind_mps_flag) VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                str(row["WBANNO"]),
                valid,
                n2n(row["TMPC"]),
                n2n(row["PRECIP_MM"]),
                n2n(row["SRAD"]),
                row["SR_FLAG"],
                n2n(row["SKINC"]),
                row["ST_TYPE"],
                row["ST_FLAG"],
                n2n(row["RH"]),
                row["RH_FLAG"],
                n2n(row["VSM5"]),
                n2n(row["SOILC5"]),
                n2n(row["WETNESS"]),
                row["WET_FLAG"],
                n2n(row["SMPS"]),
                row["SMPS_FLAG"],
            ),
        )


def download(year, reprocess=False) -> list:
    """Go Great Things"""
    dirname = f"{BASE}/{year}"
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    os.chdir(dirname)
    files = glob.glob("*.txt")
    if not files:
        LOG.warning("uscrn_ingest %s has no files", year)
        return []
    queue = []
    dlerrors = 0
    for filename in files:
        if dlerrors > 5:
            return queue
        size = os.stat(filename).st_size
        try:
            resp = httpx.get(
                f"{URI}/{year}/{filename}",
                headers={"Range": f"bytes={size}-{size + 16000000}"},
                timeout=30,
            )
            # No new data
            if resp.status_code == 416:
                continue
            # Helene Failure
            if resp.status_code == 200 and resp.text.startswith("Access"):
                continue
            if resp.status_code in [404, 403]:
                LOG.info("uscrn_ingest %s is %s", filename, resp.status_code)
                continue
            if resp.status_code < 400:
                with open(filename, "a") as fh:
                    fh.write(resp.content.decode("utf-8"))
            if resp.status_code < 400 or reprocess:
                queue.append([filename, len(resp.content)])
        except Exception as exp:
            dlerrors += 1
            LOG.warning("uscrn_ingest %s traceback: %s", filename, exp)
            continue
    if reprocess:
        return [(fn, -1) for fn in files]
    return queue


@click.command()
@click.option("--year", type=int, required=False, help="Year to process")
def main(year: int | None):
    """Go Main Go"""
    iem_pgconn = get_dbconn("iem")
    pgconn = get_dbconn("uscrn")
    reprocess = False
    if year is not None:
        # Process an entire year
        reprocess = True
    else:
        year = datetime.now().year
    for [fn, size] in download(year, reprocess):
        icursor = iem_pgconn.cursor(row_factory=dict_row)
        ocursor = pgconn.cursor()
        try:
            process_file(icursor, ocursor, year, fn, size, reprocess)
        except Exception as exp:
            LOG.warning("uscrn_ingest %s traceback: %s", fn, exp)
        icursor.close()
        ocursor.close()
        iem_pgconn.commit()
        pgconn.commit()


if __name__ == "__main__":
    main()
