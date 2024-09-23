"""Generate a First Guess RTP that the bureau can use for their product.

called from RUN_0Z.sh
"""

import os
import subprocess
import tempfile
from datetime import date, timedelta

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.tracker import loadqc
from pyiem.util import logger, utc
from sqlalchemy import text

LOG = logger()
JOBS = [
    {
        "wfo": "DMX",
        "filename": "awos_rtp_00z.shef",
        "networks": ["IA_ASOS", "ISUSM", "IA_DCP", "IA_RWIS"],
        "precip_works": ["IA_ASOS", "IL_ASOS", "ISUSM"],
        "limiter": "state = :state",
        "filter": ["state", "IA"],
        "state": "IA",
    },
    {
        "filename": "awos_rtp_00z_dvn.shef",
        "networks": "IL_ASOS IA_ASOS ISUSM IA_DCP IL_RWIS IA_RWIS".split(),
        "precip_works": ["IA_ASOS", "IL_ASOS", "ISUSM"],
        "limiter": "wfo = :wfo",
        "filter": ["wfo", "DVN"],
        "wfo": "DVN",
    },
]


def pp(val, width, dec):
    """Pretty Print."""
    fmt = f"%{width}s"
    if val is None or pd.isna(val):
        return fmt % ("M",)
    if 0 < val < 0.009:
        return fmt % ("T",)
    fmt = f"%{width}.{dec}f"
    return fmt % (val,)


def do_dvn_coop(fh):
    """Special job for DVN."""
    today = date.today()
    fh.write(
        f".BR DVN {today:%m%d} C DH18/TAIRZX/TAIRZN/PPDRZZ/SFDRZZ/SDIRZZ\n"
        ": COOP Reports processed by IEM\n"
    )
    with get_sqlalchemy_conn("iem") as conn:
        res = conn.execute(
            text(
                """
                select id, name, max_tmpf, min_tmpf, pday, snow, snowd,
                coop_valid from
                summary s JOIN stations t on (s.iemid = t.iemid)
                WHERE t.network ~* 'COOP' and day = :dt and
                extract(hour from s.coop_valid) between 16 and 19 and
                t.wfo = 'DVN' and (max_tmpf is not null or min_tmpf is not null
                or pday is not null or snow is not null or snowd is not null)
                ORDER by id asc
                """
            ),
            {"dt": today},
        )
        for row in res.mappings():
            fh.write(
                f"{row['id']:5.5s} :{row['name']:24.24s}:"
                f"DH{row['coop_valid'].strftime('%H%M')}/"
                f"{pp(row['max_tmpf'], 4, 0)}/{pp(row['min_tmpf'], 4, 0)}/"
                f"{pp(row['pday'], 5, 2)}/{pp(row['snow'], 5, 1)}/"
                f"{pp(row['snowd'], 5, 0)}\n"
            )
        fh.write(".END\n\n")


def fix_isusm(df, yesterday, today):
    """Manually correct this."""
    with get_sqlalchemy_conn("isuag") as conn:
        corrected = pd.read_sql(
            text(
                """
            SELECT station, sum(rain_in_tot_qc) from sm_hourly where
            valid > :yesterday and valid <= :today and
            station = ANY(:stations) GROUP by station
            """
            ),
            conn,
            params={
                "yesterday": yesterday,
                "today": today,
                "stations": df.index.values.tolist(),
            },
            index_col="station",
        )
    if corrected.empty:
        return
    df.loc[corrected.index, "sum"] = corrected["sum"]


def main(job):
    """Go Main Go."""
    qdict = loadqc()

    job["ets"] = utc().replace(hour=0, minute=0, second=0, microsecond=0)
    job["sts12z"] = job["ets"] + timedelta(hours=-12)
    job["sts6z"] = job["ets"] + timedelta(hours=-18)
    job["sts24h"] = job["ets"] + timedelta(days=-1)

    asosfmt = "%-6s:%-43s: %3s / %3s / %5s\n"
    fmt = "%-6s:%-43s: %3s / %3s\n"

    job["badtemps"] = [sid for sid in qdict if qdict[sid].get("tmpf")]
    job["badprecip"] = [sid for sid in qdict if qdict[sid].get("precip")]
    with get_sqlalchemy_conn("iem") as conn:
        # We get 18 hour highs
        data = pd.read_sql(
            text(
                f"""
        SELECT id, round(max(
            greatest(max_tmpf_6hr, tmpf))::numeric,0) as max_tmpf,
        count(tmpf) as obs FROM current_log c, stations t
        WHERE t.iemid = c.iemid and t.network = ANY(:networks) and
        valid >= :sts6z and valid < :ets and {job['limiter']}
        and tmpf > -99 and not id = ANY(:badtemps) GROUP by id
                 """
            ),
            conn,
            params=job,
            index_col="id",
        )
        # 18 hour low temperature
        lows = pd.read_sql(
            text(
                f"""
        SELECT id, round(min(
            least(min_tmpf_6hr, tmpf))::numeric,0) as min_tmpf,
        count(tmpf) as obs FROM
        current_log c JOIN stations t on (t.iemid = c.iemid)
        WHERE t.network = ANY(:networks) and valid >= :sts6z
        and valid < :ets and tmpf > -99 and not
        id = ANY(:badtemps) and {job['limiter']} GROUP by id
                """
            ),
            conn,
            params=job,
            index_col="id",
        )
        data["min_tmpf"] = lows["min_tmpf"]

        # 12z to 12z precip
        pcpn = pd.read_sql(
            text(
                f"""
        select id as station, sum(precip) from
        (select id, extract(hour from valid) as hour,
        max(phour) as precip from current_log c, stations t
        WHERE t.network = ANY(:networks) and t.iemid = c.iemid
        and valid >= :sts24h and valid < :ets
        and not id = ANY(:badprecip) and {job['limiter']}
        GROUP by id, hour) as foo
        GROUP by id
    """
            ),
            conn,
            params=job,
            index_col="station",
        )
        fix_isusm(pcpn, job["sts24h"], job["ets"])
        pcpn = pcpn[pcpn["sum"].notna()]
        data["precip"] = pcpn["sum"]

    with tempfile.NamedTemporaryFile("w", delete=False) as fh:
        fh.write("\n\n\n")
        for netid in job["networks"]:
            nt = NetworkTable(netid)
            ids = list(nt.sts.keys())
            ids.sort()
            for sid, meta in nt.sts.items():
                if meta[job["filter"][0]] != job["filter"][1]:
                    ids.remove(sid)
            if not ids:
                continue
            networkname = netid.replace("ASOS", "AWOS")
            precip_on = netid in job["precip_works"]
            fh.write(
                f".BR {job['wfo']} {job['ets']:%m%d} Z "
                "DH00/TAIRVS/TAIRVI"
                f"{'/PPDRVZ' if precip_on else ''}\n"
                f": {networkname} RTP FIRST GUESS PROCESSED BY THE IEM\n"
                ":   06Z TO 00Z HIGH TEMPERATURE FOR "
                f"{job['sts12z']:%d %b %Y}\n"
                ":   06Z TO 00Z LOW TEMPERATURE FOR "
                f"{job['sts12z']:%d %b %Y}\n"
                ":   00Z YESTERDAY TO 00Z TODAY RAINFALL\n"
                ":   ...BASED ON REPORTED OBS AND ANY 6 HR MAX MIN...\n"
            )
            for sid in ids:
                if (
                    netid == "IA_ASOS"
                    and nt.sts[sid]["attributes"].get("IS_AWOS") != "1"
                ):
                    continue
                if netid == "IA_DCP" and nt.sts[sid]["name"].find("RAWS") < 0:
                    continue
                my_high = "M"
                my_low = "M"
                my_precip = "M"
                if sid in data.index:
                    row = data.loc[sid]
                    if not pd.isna(row["max_tmpf"]):
                        my_high = int(row["max_tmpf"].round(0))
                    if not pd.isna(row["min_tmpf"]):
                        my_low = int(row["min_tmpf"].round(0))
                    if not pd.isna(row["precip"]):
                        if 0 < row["precip"] < 0.009:
                            my_precip = "T"
                        else:
                            my_precip = f"{row['precip']:.02f}"
                _fmt = asosfmt if precip_on else fmt
                args = [
                    sid,
                    nt.sts[sid]["name"],
                    my_high,
                    my_low,
                    my_precip,
                ]
                if not precip_on:
                    args = args[:-1]
                fh.write(_fmt % tuple(args))

            fh.write(".END\n\n")
        if job["wfo"] == "DVN":
            do_dvn_coop(fh)

    cmd = [
        "pqinsert",
        "-p",
        f"plot ac {job['ets']:%Y%m%d}0000 {job['filename']} "
        f"{job['filename']} shef",
        fh.name,
    ]
    LOG.info(" ".join(cmd))
    subprocess.call(cmd)
    os.unlink(fh.name)


if __name__ == "__main__":
    for _job in JOBS:
        main(_job)
