"""Process the US Climate Reference Network"""
import datetime
import os
import sys
import glob
import subprocess

import pytz
import pandas as pd
import requests
from metpy.units import units
from pyiem.observation import Observation
from pyiem.util import get_dbconn, exponential_backoff, logger

LOG = logger()
BASE = "/mesonet/tmp/uscrn"
URI = "https://www1.ncdc.noaa.gov/pub/data/uscrn/products/subhourly01"
FTP = "ftp://ftp.ncdc.noaa.gov/pub/data/uscrn/products/subhourly01"


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


def init_year(year):
    """We need to do great things, for a great new year"""
    # We need FTP first, since that does proper wild card expansion
    subprocess.call(f"wget -q '{FTP}/{year}/*.txt'", shell=True)


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
            f"DELETE from uscrn_t{year} WHERE station = %s",
            (df.iloc[0]["WBANNO"],),
        )
        LOG.info(
            "Removed %s rows %s %s",
            ocursor.rowcount,
            year,
            df.iloc[0]["WBANNO"],
        )
    for _, row in df.iterrows():
        valid = datetime.datetime.strptime(
            "%s %s" % (row["UTC_DATE"], row["UTC_TIME"]), "%Y%m%d %H%M"
        )
        valid = valid.replace(tzinfo=pytz.utc)
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
        table = "uscrn_t%s" % (valid.year,)
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


def download(year, reprocess=False):
    """Go Great Things"""
    dirname = "%s/%s" % (BASE, year)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    os.chdir(dirname)
    files = glob.glob("*.txt")
    if not files:
        init_year(year)
        files = glob.glob("*.txt")
    queue = []
    for filename in files:
        size = os.stat(filename).st_size
        req = exponential_backoff(
            requests.get,
            "%s/%s/%s" % (URI, year, filename),
            headers={"Range": "bytes=%s-%s" % (size, size + 16000000)},
            timeout=30,
        )
        # No new data
        if req is None or req.status_code == 416:
            continue
        if req.status_code in [404, 403]:
            LOG.info("uscrn_ingest %s is %s", filename, req.status_code)
            continue
        if req.status_code < 400:
            with open(filename, "a") as fh:
                fh.write(req.content.decode("utf-8"))
        if req.status_code < 400 or reprocess:
            queue.append([filename, len(req.content)])
        else:
            print("Got status code %s %s" % (req.status_code, req.content))
    if reprocess:
        return [(fn, -1) for fn in files]
    return queue


def main(argv):
    """Go Main Go"""
    iem_pgconn = get_dbconn("iem")
    other_pgconn = get_dbconn("other")
    year = datetime.datetime.utcnow().year
    reprocess = False
    if len(argv) == 2:
        # Process an entire year
        year = int(argv[1])
        reprocess = True
    for [fn, size] in download(year, len(argv) == 2):
        icursor = iem_pgconn.cursor()
        ocursor = other_pgconn.cursor()
        try:
            process_file(icursor, ocursor, year, fn, size, reprocess)
        except Exception as exp:
            LOG.info("uscrn_ingest %s traceback: %s", fn, exp)
        icursor.close()
        ocursor.close()
        iem_pgconn.commit()
        other_pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
