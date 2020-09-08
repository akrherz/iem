"""
Ingest data provided by the rucsoundings.noaa.gov website

RAOB sounding valid at:
   RAOB     12     17      JUL    2013
      1  94980  72558  41.32N 96.37W   350   1117
      2    100    100   1400    129  72558      3
      3           OAX                99999     kt   HHMM bearing  range
      9   9830    350    222    205    135      3   1115      0      0
      4  10000    204  99999  99999  99999  99999   1114  99999  99999
      5   9710    456    248    210  99999  99999   1115  99999  99999

   TYPE        HOUR        DAY      MONTH       YEAR    (blank)     (blank)
      1       WBAN#       WMO#        LAT        LON       ELEV       RTIME
      2       HYDRO       MXWD      TROPL      LINES     TINDEX      SOURCE
      3     (blank)      STAID    (blank)    (blank)      SONDE     WSUNITS

                                data lines
9 PRESSURE  HEIGHT TEMP      DEWPT   WIND DIR    WIND SPD  HHMM BEARING RANGE

HOUR:   time of report in UTC
LAT:    latitude in degrees and hundredths
LON:    longitude in degrees and hundredths
ELEV:   elevation from station history in meters
RTIME:  is the actual release time of radiosonde from TTBB. Appears in GTS data
        only.
HYDRO:  the pressure of the level to where the sounding passes the hydrostatic
        check (see section 4.3).**
MXWD:   the pressure of the level having the maximum wind in the sounding.  If
        within the body of the sounding there is no "8" level then
        MXWN is estimated (see section 3.2).
TROPL:  the pressure of the level containing the tropopause. If within the
        body of the sounding there is no "7" level, then TROPL is estimated
        (see section 3.3)**
LINES:  number of levels in the sounding, including the 4 identification lines.
TINDEX: indicator for estimated tropopause. A "7" indicates that sufficient
        data was available to attempt the estimation; 11 indicates that data
        terminated and that tropopause is a "suspected" tropopause.
SOURCE: 0 = National Climatic Data Center (NCDC)
        1 = Atmospheric Environment Service (AES), Canada
        2 = National Severe Storms Forecast Center (NSSFC)
        3 = GTS or GSD GTS data only
        4 = merge of NCDC and GTS data (sources 2,3 merged into sources 0,1)
SONDE:  type of radiosonde code from TTBB. Only reported with GTS data
        10 = VIZ "A" type radiosonde
        11 = VIZ "B" type radiosonde
        12 = Space data corp.(SDC) radiosonde.
WSUNITS:wind speed units (selected upon output)
        ms = tenths of meters per second
        kt = knots

PRESSURE: in whole millibars (original format)
          in tenths of millibars (new format)
HEIGHT:   height in meters (m)
TEMP:     temperature in tenths of degrees Celsius
DEWPT:    dew point temperature in tenths of a degree Celsius
WIND DIR: wind direction in degrees
WIND SPD: wind speed in knots
HHMM:     hour and minute (UTC) that this data line was taken
          (for RAOBS, estimated by assuming a 5 m/s ascent rate).
BEARING: Bearing from the ground point for this level
RANGE:   Range (nautical miles) from the ground point for this level.

"""
import datetime
import sys

import pytz
import requests
from tqdm import tqdm
from pyiem.util import exponential_backoff, get_dbconn, logger, utc
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql

LOG = logger()


class RAOB:
    """Simple class representing a RAOB profile"""

    def __init__(self):
        """ constructor"""
        self.station = None
        self.valid = None
        self.release_time = None
        self.profile = []
        self.wind_units = None
        self.hydro_level = None
        self.maxwd_level = None
        self.tropo_level = None

    def conv_hhmm(self, raw):
        """ Convert string to timestamp """
        if raw == "99999":
            return None
        ts = self.valid.replace(hour=int(raw[:-2]), minute=int(raw[-2:]))
        if ts.hour > 20 and self.valid.hour < 2:
            ts -= datetime.timedelta(days=1)
        return ts

    def conv_speed(self, raw):
        """ convert sped to mps units """
        if raw in ["99999", "-9999.00"]:
            return None
        if self.wind_units == "kt":
            return float(raw) * 0.5144
        return float(raw)

    def __str__(self):
        """ override str() """
        return "RAOB from %s valid %s with %s levels" % (
            self.station,
            self.valid,
            len(self.profile),
        )

    def database_save(self, txn):
        """ Save this to the provided database cursor """
        txn.execute(
            "SELECT fid from raob_flights where station = %s and valid = %s",
            (self.station, self.valid),
        )
        if txn.rowcount == 0:
            txn.execute(
                "INSERT into raob_flights (valid, station, release_time, "
                "hydro_level, maxwd_level, tropo_level) "
                "values (%s,%s,%s,%s,%s,%s) RETURNING fid",
                (
                    self.valid,
                    self.station,
                    self.release_time,
                    self.hydro_level,
                    self.maxwd_level,
                    self.tropo_level,
                ),
            )
        row = txn.fetchone()
        fid = row[0]
        txn.execute("DELETE from raob_profile where fid = %s", (fid,))
        if txn.rowcount > 0 and self.valid.hour in [0, 12]:
            LOG.info(
                "RAOB del %s rows for sid: %s valid: %s",
                txn.rowcount,
                self.station,
                self.valid.strftime("%Y-%m-%d %H"),
            )
        table = "raob_profile_%s" % (self.valid.year,)
        for d in self.profile:
            txn.execute(
                f"INSERT into {table} (fid, ts, levelcode, pressure, height, "
                "tmpc, dwpc, drct, smps, bearing, range_miles) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    fid,
                    d["ts"],
                    d["levelcode"],
                    d["pressure"],
                    d["height"],
                    d["tmpc"],
                    d["dwpc"],
                    d["drct"],
                    d["smps"],
                    d["bearing"],
                    d["range"],
                ),
            )


def conv_press(raw):
    """ Convert raw string to database value """
    if raw == "99999":
        return None
    return float(raw) / 10.0


def conv_temp(raw):
    """ Convert raw string to database value """
    if raw == "99999":
        return None
    return float(raw) / 10.0


def conv_drct(raw):
    """ Convert raw string to database value """
    if raw == "99999":
        return None
    return float(raw)


def parse(raw, sid):
    """ Parse the raw data and yield RAOB objects """
    rob = None
    for line in raw.split("\n"):
        tokens = line.strip().split()
        if line[:4] == "RAOB":
            continue
        if len(tokens) == 0:
            if rob is not None:
                yield rob
            rob = None
            continue
        if tokens[0] == "RAOB":
            s = " ".join(tokens[1:])
            ts = datetime.datetime.strptime(s, "%H %d %b %Y")
            rob = RAOB()
            rob.valid = ts.replace(tzinfo=pytz.UTC)
            continue
        if tokens[0] == "1":
            fl_hhmm = line[44:].strip()
            if len(fl_hhmm) > 2:
                rob.release_time = rob.conv_hhmm(fl_hhmm)
            continue
        if tokens[0] == "2":
            rob.hydro_level = conv_press(tokens[1])
            rob.maxwd_level = conv_press(tokens[2])
            rob.tropo_level = conv_press(tokens[3])
        if tokens[0] == "3":
            rob.station = sid
            rob.wind_units = tokens[3]
            continue
        if tokens[0] in ["4", "5", "6", "9"]:
            rob.profile.append(
                {
                    "levelcode": tokens[0],
                    "pressure": float(tokens[1]) / 10.0,
                    "height": conv_drct(tokens[2]),
                    "tmpc": conv_temp(tokens[3]),
                    "dwpc": conv_temp(tokens[4]),
                    "drct": conv_drct(tokens[5]),
                    "smps": rob.conv_speed(tokens[6]),
                    "ts": rob.conv_hhmm(tokens[7]),
                    "bearing": conv_drct(tokens[8]),
                    "range": conv_drct(tokens[9]),
                }
            )
    if rob is not None:
        yield rob


def main(valid):
    """Run for the given valid time!"""
    nt = NetworkTable("RAOB")
    dbconn = get_dbconn("postgis")
    # check what we have
    obs = read_sql(
        "SELECT station, count(*) from "
        f"raob_flights f JOIN raob_profile_{valid.year} p "
        "ON (f.fid = p.fid) where valid = %s GROUP by station "
        "ORDER by station ASC",
        dbconn,
        params=(valid,),
        index_col="station",
    )
    obs["added"] = 0
    v12 = valid - datetime.timedelta(hours=13)

    progress = tqdm(list(nt.sts.keys()), disable=not sys.stdout.isatty())
    for sid in progress:
        # skip virtual sites
        if sid.startswith("_"):
            continue
        if sid in obs.index and obs.at[sid, "count"] > 10:
            continue
        progress.set_description(sid)
        uri = (
            "https://rucsoundings.noaa.gov/get_raobs.cgi?data_source=RAOB;"
            "start_year=%s;start_month_name=%s;"
        ) % (valid.year, valid.strftime("%b"))
        uri += ("start_mday=%s;start_hour=%s;start_min=0;n_hrs=12.0;") % (
            valid.day,
            valid.hour,
        )
        uri += "fcst_len=shortest;airport=%s;" % (sid,)
        uri += "text=Ascii%20text%20%28GSD%20format%29;"
        uri += ("hydrometeors=false&startSecs=%s&endSecs=%s") % (
            v12.strftime("%s"),
            valid.strftime("%s"),
        )

        req = exponential_backoff(requests.get, uri, timeout=30)
        if req is None or req.status_code != 200:
            LOG.info("dl failed %s for %s", sid, valid)
            continue
        cursor = dbconn.cursor()
        try:
            for rob in parse(req.content.decode("utf-8"), sid):
                if rob.valid == valid:
                    obs.at[sid, "added"] = len(rob.profile)
                rob.database_save(cursor)
        except Exception as exp:
            fn = "/tmp/%s_%s_fail" % (sid, valid.strftime("%Y%m%d%H%M"))
            LOG.info("FAIL %s %s %s, check %s for data", sid, valid, exp, fn)
            with open(fn, "w") as fh:
                fh.write(req.content)
        finally:
            cursor.close()
            dbconn.commit()
    LOG.debug("%s entered %s levels of data", valid, obs["added"].sum())
    df2 = obs[obs["count"] == 0]
    if len(df2.index) > 40:
        LOG.info("%s high missing count of %s", valid, len(df2.index))


def frontend(argv):
    """Figure out what we need to do here! """
    valid = utc(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]))
    main(valid)
    for days in [3, 14, 365]:
        ts = valid - datetime.timedelta(days=days)
        main(ts)


if __name__ == "__main__":
    frontend(sys.argv)
