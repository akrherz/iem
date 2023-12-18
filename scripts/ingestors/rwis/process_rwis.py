"""Process the IDOT RWIS Data files"""
# stdlib
import datetime
import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd

# third party
import requests
from pyiem import util
from pyiem.database import get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.observation import Observation
from pyiem.tracker import TrackerEngine

LOG = util.logger()
NT = NetworkTable("IA_RWIS")
RWIS2METAR = {
    "00": "XADA",
    "01": "XALG",
    "02": "XATN",
    "03": "XALT",
    "04": "XAME",
    "05": "XANK",
    "06": "XAVO",
    "07": "XBUR",
    "08": "XCAR",
    "09": "XCDR",
    "10": "XCID",
    "11": "XCEN",
    "12": "XCOU",
    "13": "XCRE",
    "14": "XDAV",
    "15": "XDEC",
    "16": "XDSM",
    "17": "XDES",
    "18": "XDST",
    "19": "XDEW",
    "20": "XDUB",
    "21": "XFOD",
    "22": "XGRI",
    "23": "XIAC",
    "24": "XIOW",
    "25": "XJEF",
    "26": "XLEO",
    "27": "XMAN",
    "28": "XMAQ",
    "29": "XMAR",
    "30": "XMCW",
    "31": "XMIS",
    "32": "XMOU",
    "33": "XNEW",
    "34": "XONA",
    "35": "XOSC",
    "36": "XOTT",
    "37": "XPEL",
    "38": "XRED",
    "39": "XSID",
    "40": "XSIG",
    "41": "XSIO",
    "42": "XSPE",
    "43": "XSTO",
    "44": "XTIP",
    "45": "XURB",
    "46": "XWAT",
    "47": "XWIL",
    "48": "XWBG",
    "49": "XHAN",
    "50": "XSBI",
    "51": "XIGI",
    "52": "XCRI",
    "53": "XCFI",
    "54": "XSYI",
    "55": "XBFI",
    "56": "XDYI",
    "57": "XTMI",
    "58": "XPFI",
    "59": "XCTI",
    "60": "XDNI",
    "61": "XQCI",
    "62": "XSMI",
    "63": "XRWI",
    "64": "XETI",
    "65": "XCCI",
    "66": "XKSI",
    "67": "XKNI",
    "68": "XCMI",
    "69": "XRGI",
    "70": "XKYI",
    "72": "XCTI",
}
# STATUS 1 is online
ATMOS_URI = (
    "https://services.arcgis.com/8lRhdTsQyJpO52F1/arcgis/rest/services/"
    "RWIS_Atmospheric_Data_View/FeatureServer/0/query?where=STATUS%3D1&"
    "f=json&outFields=DATA_LAST_UPDATED,AIR_TEMP,RELATIVE_HUMIDITY,DEW_POINT,"
    "VISIBILITY,AVG_WINDSPEED_KNOTS,MAX_WINDSPEED_KNOTS,WIND_DIRECTION_DEG,"
    "PRECIPITATION_RATE,PRECIPITATION_ACCUMULATION,NWS_ID"
)
SURFACE_URI = (
    "https://services.arcgis.com/8lRhdTsQyJpO52F1/arcgis/rest/services/"
    "RWIS_Surface_Data_View/FeatureServer/0/query?where=STATUS%3D1&f=json&"
    "outFields=NWS_ID,SURFACE_CONDITION,SURFACE_TEMP,ICE_PERCENTAGE,"
    "FREEZE_TEMP,SENSOR_ID,FrictionIndex,DATA_LAST_UPDATED"
)


def merge(atmos, surface):
    """Merge the surface data into the atmospheric one, return a dict.

    Args:
      atmos (DataFrame): atmospherics
      surface (DataFrame): surface data

    Returns:
      dictionary of values
    """
    # Figure out our most recent obs as the RWIS service will only emit online
    with get_sqlalchemy_conn("iem") as conn:
        currents = pd.read_sql(
            """
            select id, valid from current c JOIN stations t
                on (c.iemid = t.iemid) WHERE t.network = 'IA_RWIS'
            """,
            conn,
            index_col="id",
        )

    atmos = atmos.set_index("NWS_ID")
    # pivot
    surface["SENSOR_ID"] = surface["SENSOR_ID"].astype(int)
    surface = surface.pivot(
        index="NWS_ID",
        columns="SENSOR_ID",
        values=[
            "valid",
            "SURFACE_CONDITION",
            "SURFACE_TEMP",
            "ICE_PERCENTAGE",
            "FREEZE_TEMP",
            "FrictionIndex",
        ],
    )
    surface.columns = surface.columns.to_flat_index()
    df = atmos.join(surface)
    LOG.debug("We have %s rows of data", len(df.index))
    data = {}
    for nwsli, row in df.iterrows():
        if nwsli not in NT.sts:
            LOG.debug("station %s is unknown to us, skipping", nwsli)
            continue
        data[nwsli] = {
            "valid": row["valid"].to_pydatetime(),
            "online": True,
            "tmpf": row["AIR_TEMP"],
            "dwpf": row["DEW_POINT"],
            "relh": row["RELATIVE_HUMIDITY"],
            "sknt": row["AVG_WINDSPEED_KNOTS"],
            "gust": row["MAX_WINDSPEED_KNOTS"],
            "drct": row["WIND_DIRECTION_DEG"],
            "pday": row["PRECIPITATION_ACCUMULATION"],
        }
        for sid in range(4):
            try:
                data[nwsli][f"scond{sid}"] = row[("SURFACE_CONDITION", sid)]
                data[nwsli][f"tsf{sid}"] = row[("SURFACE_TEMP", sid)]
            except KeyError as exp:
                LOG.info("KeyError raised for nwsli: '%s' %s", nwsli, exp)
    for sid in NT.sts:
        if sid not in data and sid in currents.index:
            LOG.info("station %s is missing, adding", sid)
            data[sid] = {"valid": currents.at[sid, "valid"], "online": False}
    return data


def do_iemtracker(obs):
    """Iterate over the obs and do IEM Tracker related activities"""
    threshold = util.utc() - datetime.timedelta(hours=3)
    iem_pgconn, icursor = util.get_dbconnc("iem")
    portfolio_pgconn, pcursor = util.get_dbconnc("portfolio")
    tracker = TrackerEngine(icursor, pcursor)
    tracker.process_network(obs, "iarwis", NT, threshold)
    tracker.send_emails()
    iem_pgconn.commit()
    portfolio_pgconn.commit()


def METARtemp(val):
    """convert temp to METAR"""
    f_temp = float(val)
    i_temp = int(round(f_temp, 0))
    f1_temp = int(round(f_temp * 10.0, 0))
    if i_temp < 0:
        i_temp = 0 - i_temp
        m_temp = "M%02i" % (i_temp,)
    else:
        m_temp = "%02i" % (i_temp,)

    if f1_temp < 0:
        t_temp = "1%03i" % (0 - f1_temp,)
    else:
        t_temp = "0%03i" % (f1_temp,)

    return m_temp, t_temp


def METARwind(sknt, drct, gust):
    """convert to METAR"""
    s = ""
    d5 = drct
    if str(d5)[-1] == "5":
        d5 -= 5
    s += "%03.0f%02.0f" % (d5, sknt)
    if gust is not None:
        s += "G%02.0f" % (gust,)
    s += "KT"
    return s


def gen_metars(obs, filename, convids=False):
    """Create METAR Data files

    Args:
      obs (list): list of dictionaries with obs in them
      filename (str): filename to write data to
      convids (bool): should we use special logic for ID conversion

    """
    mtime = util.utc().strftime("%d%H%M")
    thres = util.utc() - datetime.timedelta(hours=3)
    with open(filename, "w", encoding="utf-8") as fp:
        fp.write("\001\015\015\012001\n")
        fp.write(f"SAUS43 KDMX {mtime}\015\015\012METAR\015\015\012")
        for sid in obs:
            ob = obs[sid]
            if ob["valid"] < thres:
                continue
            if sid in ["RIOI4", "ROSI4", "RSMI4", "RMCI4"]:
                continue
            metarid = sid[:4]
            remoteid = NT.sts[sid]["remote_id"]
            if remoteid is None:
                LOG.info("nwsli: %s is unknown remote_id", sid)
                continue
            if convids:
                metarid = RWIS2METAR.get("%02i" % (remoteid,), "XXXX")
            temptxt = ""
            t_temptxt = ""
            windtxt = ""
            if ob.get("sknt") is not None and ob.get("drct") is not None:
                windtxt = METARwind(ob["sknt"], ob["drct"], ob.get("gust"))
            if obs.get("tmpf") is not None and obs.get("dwpf") is not None:
                m_tmpc, t_tmpc = METARtemp(
                    util.convert_value(ob["tmpf"], "degF", "degC")
                )
                m_dwpc, t_dwpc = METARtemp(
                    util.convert_value(ob["dwpf"], "degF", "degC")
                )
                temptxt = "%s/%s" % (m_tmpc, m_dwpc)
                t_temptxt = "T%s%s " % (t_tmpc, t_dwpc)
            fp.write(
                ("%s %s %s %s RMK AO2 %s%s\015\015\012" "")
                % (
                    metarid,
                    ob["valid"].strftime("%d%H%MZ"),
                    windtxt,
                    temptxt,
                    t_temptxt,
                    "=",
                )
            )

        fp.write("\015\015\012\003")


def update_iemaccess(obs):
    """Update the IEMAccess database"""
    for sid in obs:
        # FIXME
        pgconn, icursor = util.get_dbconnc("iem")
        ob = obs[sid]
        iemob = Observation(sid, "IA_RWIS", ob["valid"])
        for varname in ob:
            if varname in ["valid"]:
                continue
            # Don't insert NaN values into iemaccess
            thisval = ob.get(varname)
            if thisval is None:
                continue
            # strings fail the isnan check
            if isinstance(thisval, str):
                iemob.data[varname] = ob.get(varname)
            elif not np.isnan(thisval):
                iemob.data[varname] = ob.get(varname)
        iemob.save(icursor)
        icursor.close()
        pgconn.commit()


def process_features(features):
    """Make a dataframe."""
    rows = []
    for feat in features:
        props = feat["attributes"]
        props["valid"] = (
            datetime.datetime(1970, 1, 1)
            + datetime.timedelta(seconds=props["DATA_LAST_UPDATED"] / 1000.0)
        ).replace(tzinfo=datetime.timezone.utc)
        rows.append(props)
    return pd.DataFrame(rows).replace({9999: np.nan})


def fetch(uri):
    """Download the files we need"""
    res = util.exponential_backoff(requests.get, uri, timeout=30)
    if res is None:
        LOG.info("failed to fetch %s", uri)
        sys.exit()
    data = res.json()
    if "features" not in data:
        LOG.info(
            "Got status_code: %s for %s, invalid result of: %s",
            res.status_code,
            uri,
            json.dumps(data, sort_keys=True, indent=4, separators=(",", ": ")),
        )
        sys.exit()
    return process_features(data["features"])


def ldm_insert_metars(fn1, fn2):
    """Insert into LDM please"""
    for fn in [fn1, fn2]:
        proc = subprocess.Popen(
            ("pqinsert -p '%s' %s") % (fn.replace("/tmp/", ""), fn),
            shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        os.waitpid(proc.pid, 0)
        os.unlink(fn)


def main():
    """Go Main Go"""
    atmos = fetch(ATMOS_URI)
    surface = fetch(SURFACE_URI)
    if atmos.empty or surface.empty:
        LOG.info(
            "FAIL, empty dataframe atmos sz:%s, surface sz:%s",
            len(atmos.index),
            len(surface.index),
        )
        return
    obs = merge(atmos, surface)
    do_iemtracker(obs)
    # Remove back out those stations that are offline
    obs = {k: v for k, v in obs.items() if v["online"]}

    ts = util.utc().strftime("%d%H%M")
    fn1 = f"/tmp/IArwis{ts}.sao"
    fn2 = f"/tmp/IA.rwis{ts}.sao"
    gen_metars(obs, fn1, False)
    gen_metars(obs, fn2, True)
    ldm_insert_metars(fn1, fn2)

    update_iemaccess(obs)


if __name__ == "__main__":
    main()
