"""Ingest the RWIS rainwise data"""
import datetime
from io import StringIO

import requests
import pandas as pd
import pytz
from pyiem.util import get_dbconn
from pyiem.observation import Observation


URI = (
    "http://www.rainwise.net/inview/api/stationdata-iowa.php?"
    "username=iowadot&sid=1f6075797434189912d55196d0be5bac&"
    "pid=d0fb9ae6b1352a03720abdedcdc16e80"
)
# &sdate=2013-12-09&edate=2013-12-09&mac=0090C2E90575

ASSOC = {
    "RDTI4": "0090C2E90575",
    "RULI4": "0090C2E904B2",
    "RSNI4": "0090C2E9BC17",
    "ROOI4": "0090C2E90568",
    "RASI4": "0090C2E90538",
}


def get_last_obs(icursor):
    """Get the last obs we have for each of the sites"""
    sids = ASSOC.keys()
    data = {}
    icursor.execute(
        """
    SELECT id, valid from current_log c JOIN stations t on (t.iemid = c.iemid)
    WHERE t.network = 'IA_RWIS' and valid > '1990-01-01' and  t.id in
    """
        + str(tuple(sids))
    )
    for row in icursor:
        data[row[0]] = row[1]
    return data


def process(today, icursor, nwsli, lastts):
    """Process this NWSLI please"""
    myuri = "%s&sdate=%s&edate=%s&mac=%s" % (
        URI,
        today.strftime("%Y-%m-%d"),
        today.strftime("%Y-%m-%d"),
        ASSOC[nwsli],
    )
    # print nwsli, myuri
    try:
        sio = StringIO()
        sio.write(requests.get(myuri, timeout=15).text)
    except Exception:
        return
    try:
        sio.seek(0)
        df = pd.read_csv(sio)
    except Exception as exp:
        print(
            ("ingest_rw.py pandas fail for sid: %s\nreason: %s") % (nwsli, exp)
        )
        return
    # Index([u'utc', u'mac', u'serial', u'tia', u'til', u'tih', u'tdl',
    # u'tdh', u'ria', u'ril', u'rih', u'rdl', u'rdh', u'bia', u'bil',
    # u'bih', u'bdl', u'bdh', u'wia', u'dia', u'wih', u'dih', u'wdh',
    # u'ddh', u'ris', u'rds', u'lis', u'lds', u'sia', u'sis', u'sds',
    # u'unt', u'ver', u'heatindex', u'windchill', u'dewpoint', u'uv',
    # u'batt', u'evpt', u't', u'flg', u'ip', u't1ia', u't1il', u't1ih',
    # u't1dl', u't1dh', u't2ia', u't2il', u't2ih', u't2dl', u't2dh'],
    # dtype=object)

    conv = {
        "tmpf": "tmpf",
        "max_tmpf": "max_tmpf",
        "min_tmpf": "min_tmpf",
        "relh": "ria",
        "pres": "pres",
        "sknt": "sknt",
        "drct": "dia",
        "gust": "gust",  # fix units
        "max_gust": "max_gust",  # fix units
        "dwpf": "dwpf",
        "tsf0": "tsf0",
        "tsf1": "tsf1",
    }
    if df.empty or "dewpoint" not in df.columns:
        # print 'RW download for: %s had columns: %s' % (nwsli, df.columns)
        return
    df["dwpf"] = df["dewpoint"] / 10.0
    df["tmpf"] = df["tia"] / 10.0
    df["max_tmpf"] = df["tdh"] / 10.0
    df["min_tmpf"] = df["tdl"] / 10.0
    df["tsf0"] = df["t1ia"] / 10.0
    df["tsf1"] = df["t2ia"] / 10.0
    df["sknt"] = df["wia"] / 10.15  # x10
    df["gust"] = df["wih"] / 10.15
    df["pres"] = df["bia"] / 100.0
    df["max_gust"] = df["wdh"] / 10.15

    sdf = df.sort_values(by=["utc"], ascending=[True])

    for _, row in sdf.iterrows():
        if pd.isnull(row["utc"]):
            continue
        utc = datetime.datetime.strptime(row["utc"], "%Y-%m-%d %H:%M:%S")
        utc = utc.replace(tzinfo=pytz.timezone("UTC"))

        if lastts is not None and utc < lastts:
            continue
        # print nwsli, utc
        iem = Observation(nwsli, "IA_RWIS", utc)
        for iemvar in conv:
            iem.data[iemvar] = row[conv[iemvar]]

        iem.save(icursor)


def main():
    """Go Main Go"""
    today = datetime.datetime.now()

    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor()
    data = get_last_obs(icursor)
    for nwsli in ASSOC:
        process(today, icursor, nwsli, data.get(nwsli, None))
    icursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
