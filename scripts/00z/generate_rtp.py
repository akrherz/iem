"""Generate a First Guess RTP that the bureau can use for their product.

called from RUN_0Z.sh
"""
import datetime
import os
import subprocess
import tempfile

from pyiem import network
from pyiem.tracker import loadqc
from pyiem.util import get_dbconnc, logger, utc

LOG = logger()
NETWORKS = ["IA_ASOS", "ISUSM", "IA_DCP", "IA_RWIS"]


def main():
    """Go Main Go."""
    nt = network.Table(NETWORKS)
    qdict = loadqc()
    pgconn, icursor = get_dbconnc("iem")

    ets = utc().replace(hour=0, minute=0, second=0, microsecond=0)
    sts12z = ets + datetime.timedelta(hours=-12)
    sts6z = ets + datetime.timedelta(hours=-18)
    sts24h = ets + datetime.timedelta(days=-1)

    asosfmt = "%-6s:%-19s: %3s / %3s / %5s\n"
    fmt = "%-6s:%-43s: %3s / %3s\n"

    # We get 18 hour highs
    highs = {}
    sql = """SELECT t.id as station,
        round(max(tmpf)::numeric,0) as max_tmpf,
        count(tmpf) as obs FROM current_log c, stations t
        WHERE t.iemid = c.iemid and t.network = ANY(%s) and valid > %s
            and valid < %s
        and tmpf between -70 and 130 GROUP by t.id """
    icursor.execute(sql, (NETWORKS, sts6z, ets))
    for row in icursor:
        if qdict.get(row["station"], {}).get("tmpf"):
            continue
        highs[row["station"]] = row["max_tmpf"]

    # 00 UTC to 00 UTC Preciptation
    pcpn = {}
    icursor.execute(
        """
        select id as station, sum(precip) from
        (select t.id, extract(hour from valid) as hour,
        max(phour) as precip from current_log c, stations t
        WHERE t.network = ANY(%s) and t.iemid = c.iemid
        and valid  >= %s and valid < %s
        GROUP by t.id, hour) as foo
        GROUP by id""",
        (NETWORKS, sts24h, ets),
    )
    for row in icursor:
        if qdict.get(row["station"], {}).get("precip") or row["sum"] is None:
            continue
        if 0 < row["sum"] < 0.009:
            pcpn[row["station"]] = "T"
        else:
            pcpn[row["station"]] = f"{row['sum']:5.2f}"

    lows = {}
    icursor.execute(
        """SELECT t.id as station,
        round(min(tmpf)::numeric,0) as min_tmpf,
        count(tmpf) as obs FROM current_log c, stations t
        WHERE t.iemid = c.iemid and t.network = ANY(%s) and valid > %s and
        valid < %s and tmpf > -99 GROUP by t,id""",
        (NETWORKS, sts6z, ets),
    )

    for row in icursor:
        if qdict.get(row["station"], {}).get("tmpf"):
            continue
        lows[row["station"]] = row["min_tmpf"]

    ids = list(nt.sts.keys())
    ids.sort()

    with tempfile.NamedTemporaryFile("w", delete=False) as fh:
        fh.write("\n\n\n")
        for netid in NETWORKS:
            networkname = "AWOS" if netid == "IA_ASOS" else netid
            fh.write(
                f".BR DMX {ets:%m%d} Z "
                "DH00/TAIRVS/TAIRVI"
                f"{'/PPDRVZ' if netid == 'IA_ASOS' else ''}\n"
                f": IOWA {networkname} RTP FIRST GUESS PROCESSED BY THE IEM\n"
                f":   06Z TO 00Z HIGH TEMPERATURE FOR {sts12z:%d %b %Y}\n"
                f":   06Z TO 00Z LOW TEMPERATURE FOR {sts12z:%d %b %Y}\n"
                ":   00Z YESTERDAY TO 00Z TODAY RAINFALL\n"
                ":   ...BASED ON REPORTED OBS...\n"
            )
            for sid in ids:
                if nt.sts[sid]["network"] != netid:
                    continue
                if (
                    netid == "IA_ASOS"
                    and nt.sts[sid]["attributes"].get("IS_AWOS") != "1"
                ):
                    continue
                if netid == "IA_DCP" and nt.sts[sid]["name"].find("RAWS") < 0:
                    continue
                myP = pcpn.get(sid, "M")
                if netid != "IA_ASOS":
                    myP = "M"
                myH = highs.get(sid, "M")
                myL = lows.get(sid, "M")
                _fmt = asosfmt if netid == "IA_ASOS" else fmt
                args = [sid, nt.sts[sid]["name"], myH, myL, myP]
                if netid != "IA_ASOS":
                    args = args[:-1]
                fh.write(_fmt % tuple(args))

            fh.write(".END\n\n")

    cmd = [
        "pqinsert",
        "-p",
        f"plot ac {ets:%Y%m%d}0000 awos_rtp_00z.shef awos_rtp_00z.shef shef",
        fh.name,
    ]
    LOG.info(" ".join(cmd))
    subprocess.call(cmd)
    os.unlink(fh.name)
    pgconn.close()


if __name__ == "__main__":
    main()
