"""Download and process the scan dataset"""
import datetime
import sys
from zoneinfo import ZoneInfo

import requests
from pyiem.network import Table as NetworkTable
from pyiem.observation import Observation
from pyiem.util import c2f, get_dbconnc, logger, utc

LOG = logger()


mapping = {
    "Site Id": {"iemvar": "station", "multiplier": 1},
    "Date": {"iemvar": "", "multiplier": 1},
    "Time (CST)": {"iemvar": "", "multiplier": 1},
    "Time (CDT)": {"iemvar": "", "multiplier": 1},
    "PREC.I-1 (in)": {"iemvar": "", "multiplier": 1},
    "PREC.I-2 (in)": {"iemvar": "", "multiplier": 1},
    "TOBS.I-1 (degC)": {"iemvar": "tmpc", "multiplier": 1},
    "TMAX.H-1 (degC)": {"iemvar": "", "multiplier": 1},
    "TMIN.H-1 (degC)": {"iemvar": "", "multiplier": 1},
    "TAVG.H-1 (degC)": {"iemvar": "", "multiplier": 1},
    "PRCP.H-1 (in)": {"iemvar": "phour", "multiplier": 1},
    "SMS.I-1:-2 (pct)": {"iemvar": "c1smv", "multiplier": 1},
    "SMS.I-1:-4 (pct)": {"iemvar": "c2smv", "multiplier": 1},
    "SMS.I-1:-8 (pct)": {"iemvar": "c3smv", "multiplier": 1},
    "SMS.I-1:-20 (pct)": {"iemvar": "c4smv", "multiplier": 1},
    "SMS.I-1:-40 (pct)": {"iemvar": "c5smv", "multiplier": 1},
    "STO.I-1:-2 (degC)": {"iemvar": "c1tmpc", "multiplier": 1},
    "STO.I-1:-4 (degC)": {"iemvar": "c2tmpc", "multiplier": 1},
    "STO.I-1:-8 (degC)": {"iemvar": "c3tmpc", "multiplier": 1},
    "STO.I-1:-20 (degC)": {"iemvar": "c4tmpc", "multiplier": 1},
    "STO.I-1:-40 (degC)": {"iemvar": "c5tmpc", "multiplier": 1},
    "STO.I-2:-2 (degC)": {"iemvar": "", "multiplier": 1},
    "STO.I-2:-4 (degC)": {"iemvar": "", "multiplier": 1},
    "STO.I-2:-8 (degC)": {"iemvar": "", "multiplier": 1},
    "STO.I-2:-20 (degC)": {"iemvar": "", "multiplier": 1},
    "STO.I-2:-40 (degC)": {"iemvar": "", "multiplier": 1},
    "SAL.I-1:-2 (gram/l)": {"iemvar": "", "multiplier": 1},
    "SAL.I-1:-4 (gram/l)": {"iemvar": "", "multiplier": 1},
    "SAL.I-1:-8 (gram/l)": {"iemvar": "", "multiplier": 1},
    "SAL.I-1:-20 (gram/l)": {"iemvar": "", "multiplier": 1},
    "SAL.I-1:-40 (gram/l)": {"iemvar": "", "multiplier": 1},
    "RDC.I-1:-2 (unitless)": {"iemvar": "", "multiplier": 1},
    "RDC.I-1:-4 (unitless)": {"iemvar": "", "multiplier": 1},
    "RDC.I-1:-8 (unitless)": {"iemvar": "", "multiplier": 1},
    "RDC.I-1:-20 (unitless)": {"iemvar": "", "multiplier": 1},
    "RDC.I-1:-40 (unitless)": {"iemvar": "", "multiplier": 1},
    "BATT.I-1 (volt)": {"iemvar": "", "multiplier": 1},
    "BATT.I-2 (volt)": {"iemvar": "", "multiplier": 1},
    "WDIRV.H-1:144 (degree)": {"iemvar": "drct", "multiplier": 1},
    "WDIRV.H-1:101 (degree)": {"iemvar": "drct", "multiplier": 1},
    "WDIRV.H-1:120 (degree)": {"iemvar": "drct", "multiplier": 1},
    "WDIRV.H-1:140 (degree)": {"iemvar": "drct", "multiplier": 1},
    "WDIRV.H-1:117 (degree)": {"iemvar": "drct", "multiplier": 1},
    "WSPDX.H-1:144 (mph)": {"iemvar": "gust", "multiplier": 0.8689},
    "WSPDX.H-1:101 (mph)": {"iemvar": "gust", "multiplier": 0.8689},
    "WSPDX.H-1:120 (mph)": {"iemvar": "gust", "multiplier": 0.8689},
    "WSPDX.H-1:140 (mph)": {"iemvar": "gust", "multiplier": 0.8689},
    "WSPDX.H-1:117 (mph)": {"iemvar": "gust", "multiplier": 0.8689},
    "WSPDV.H-1:144 (mph)": {"iemvar": "sknt", "multiplier": 0.8689},
    "WSPDV.H-1:101 (mph)": {"iemvar": "sknt", "multiplier": 0.8689},
    "WSPDV.H-1:120 (mph)": {"iemvar": "sknt", "multiplier": 0.8689},
    "WSPDV.H-1:140 (mph)": {"iemvar": "sknt", "multiplier": 0.8689},
    "WSPDV.H-1:117 (mph)": {"iemvar": "sknt", "multiplier": 0.8689},
    "RHUM.I-1 (pct)": {"iemvar": "relh", "multiplier": 1},
    "PRES.I-1 (inch_Hg)": {"iemvar": "pres", "multiplier": 1},
    "SRADV.H-1 (watt/m2)": {"iemvar": "srad", "multiplier": 1},
    "DPTP.H-1 (degC)": {"iemvar": "dwpc", "multiplier": 1},
    "PVPV.H-1 (kPa)": {"iemvar": "", "multiplier": 1},
    "RHUMN.H-1 (pct)": {"iemvar": "", "multiplier": 1},
    "RHUMX.H-1 (pct)": {"iemvar": "", "multiplier": 1},
    "SVPV.H-1 (kPa)": {"iemvar": "", "multiplier": 1},
}

postvars = {
    "sitenum": "2031",
    "report": "ALL",
    "timeseries": "Hourly",
    "interval": "DAY",  # PST ?
    "format": "copy",
    "site_network": "scan",
    "time_zone": "CST",
}
URI = "https://wcc.sc.egov.usda.gov/nwcc/view"


def savedata(icursor, scursor, reprocessing, data, maxts):
    """
    Save away our data into IEM Access
    """
    if "Time" in data:
        tstr = data["Date"] + " " + data["Time"]
    elif "Time (CST)" in data:
        tstr = data["Date"] + " " + data["Time (CST)"]
    else:
        tstr = data["Date"] + " " + data["Time (CDT)"]
    ts = datetime.datetime.strptime(tstr, "%Y-%m-%d %H:%M")
    localts = utc().astimezone(ZoneInfo("America/Chicago"))
    ts = localts.replace(
        year=ts.year,
        month=ts.month,
        day=ts.day,
        hour=ts.hour,
        minute=ts.minute,
        second=0,
        microsecond=0,
    )
    sid = f"S{data['Site Id']}"

    if not reprocessing and sid in maxts and maxts[sid] >= ts:
        return

    iem = Observation(sid, "SCAN", ts)

    iem.data["ts"] = ts
    iem.data["year"] = ts.astimezone(ZoneInfo("UTC")).year
    for key in data.keys():
        if (
            key in mapping
            and mapping[key]["iemvar"] != ""
            and key != "Site Id"
        ):
            iem.data[mapping[key]["iemvar"]] = float(data[key].strip())

    iem.data["valid"] = ts
    if iem.data.get("tmpc") is not None:
        iem.data["tmpf"] = c2f(float(iem.data.get("tmpc")))
    if iem.data.get("dwpc") is not None:
        iem.data["dwpf"] = c2f(float(iem.data.get("dwpc")))
    for i in range(1, 6):
        if iem.data.get(f"c{i}tmpf") is not None:
            iem.data[f"c{i}tmpf"] = c2f(float(iem.data.get(f"c{i}tmpc")))
        if iem.data.get(f"c{i}smv") is not None:
            iem.data[f"c{i}smv"] = float(iem.data.get(f"c{i}smv"))
    if iem.data.get("phour") is not None:
        iem.data["phour"] = float(iem.data.get("phour"))
    if not iem.save(icursor):
        LOG.info("iemaccess for sid: %s ts: %s updated no rows", sid, ts)

    if reprocessing:
        scursor.execute(
            """DELETE from t%(year)s_hourly
        WHERE station = '%(station)s' and valid = '%(valid)s'
        """
            % iem.data
        )
    sql = (
        """INSERT into t%(year)s_hourly (station, valid, tmpf,
        dwpf, srad,
         sknt, drct, relh, pres, c1tmpf, c2tmpf, c3tmpf, c4tmpf,
         c5tmpf,
         c1smv, c2smv, c3smv, c4smv, c5smv, phour)
        VALUES
        ('%(station)s', '%(valid)s', %(tmpf)s, %(dwpf)s,
         %(srad)s,%(sknt)s,
        %(drct)s, %(relh)s, %(pres)s, %(c1tmpf)s,
        %(c2tmpf)s,
        %(c3tmpf)s, %(c4tmpf)s, %(c5tmpf)s, %(c1smv)s,
         %(c2smv)s,
        %(c3smv)s, %(c4smv)s, %(c5smv)s, %(phour)s)
        """
        % iem.data
    )
    scursor.execute(sql.replace("None", "null"))


def load_times(icursor):
    """
    Load the latest ob times from the database
    """
    icursor.execute(
        "SELECT t.id, valid from current c, stations t WHERE "
        "t.iemid = c.iemid and t.network = 'SCAN'"
    )
    data = {}
    for row in icursor:
        data[row["id"]] = row["valid"]
    return data


def main(argv):
    """Go Main Go"""
    nt = NetworkTable("SCAN")
    SCAN, scursor = get_dbconnc("scan")
    ACCESS, icursor = get_dbconnc("iem")
    reprocessing = False
    if len(argv) == 4:
        postvars["intervalType"] = "View Historic"
        postvars["year"] = argv[1]
        postvars["month"] = argv[2]
        postvars["day"] = argv[3]
        reprocessing = True

    maxts = load_times(icursor)
    for sid in nt.sts:
        # iem uses S<id> and scan site uses just <id>
        postvars["sitenum"] = sid[1:]
        try:
            req = requests.get(URI, params=postvars, timeout=10)
            if req.status_code != 200:
                LOG.info("Got %s for url %s", req.status_code, req.url)
                continue
            response = req.content.decode("utf-8", "ignore")
        except Exception as exp:
            LOG.info("Failed to download: %s %s", sid, exp)
            continue
        linesin = response.split("\n")
        # trim blank lines
        lines = [li for li in linesin if li.strip() != ""]
        cols = lines[1].split(",")
        if not cols:
            LOG.info("For station: %s had no columns", sid)
        data = {}
        for row in lines[2:]:
            if row.strip() == "":
                continue
            tokens = row.replace("'", "").split(",")
            for col, token in zip(cols, tokens):
                if col.strip() == "":
                    continue
                col = col.replace("  (loam)", "").replace("  (silt)", "")
                data[col.strip()] = token
            if "Date" in data:
                savedata(icursor, scursor, reprocessing, data, maxts)
    icursor.close()
    scursor.close()
    ACCESS.commit()
    SCAN.commit()


if __name__ == "__main__":
    main(sys.argv)
