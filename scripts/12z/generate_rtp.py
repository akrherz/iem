"""
 Generate a RTP product for the weather bureau as my database as more AWOS
 obs than what they get
"""
import datetime
import os
import subprocess
import tempfile

from pyiem import network
from pyiem.tracker import loadqc
from pyiem.util import get_dbconnc, utc

NETWORKS = ["IA_ASOS", "ISUSM", "IA_DCP", "IA_RWIS"]


def main():
    """Go Main Go"""
    nt = network.Table(NETWORKS)
    qdict = loadqc()
    pgconn, icursor = get_dbconnc("iem")

    # We run at 12z
    now12z = utc().replace(hour=12, minute=0, second=0, microsecond=0)
    today6z = now12z.replace(hour=6)
    today0z = now12z.replace(hour=0)
    yesterday6z = today6z - datetime.timedelta(days=1)
    yesterday12z = now12z - datetime.timedelta(days=1)

    asosfmt = "%-6s:%-19s: %3s / %3s / %5s / %4s / %2s\n"
    fmt = "%-6s:%-43s: %3s / %3s / %5s / %4s / %2s\n"

    # 6z to 6z high temperature
    highs = {}
    sql = """SELECT id,
        round(max(tmpf)::numeric,0) as max_tmpf,
        count(tmpf) as obs FROM current_log c, stations t
        WHERE t.iemid = c.iemid and t.network = ANY(%s) and valid >= %s
        and valid < %s
        and tmpf > -99 GROUP by id """
    args = (NETWORKS, yesterday6z, today6z)
    icursor.execute(sql, args)
    for row in icursor:
        if qdict.get(row["id"], {}).get("tmpf"):
            continue
        highs[row["id"]] = row["max_tmpf"]

    # 12z to 12z precip
    pcpn = {}
    sql = """
        select id, sum(precip) from
        (select id, extract(hour from valid) as hour,
        max(phour) as precip from current_log c, stations t
        WHERE t.network = ANY(%s) and t.iemid = c.iemid
        and valid  >= %s and valid < %s
        GROUP by id, hour) as foo
        GROUP by id
    """
    args = (NETWORKS, yesterday12z, now12z)
    icursor.execute(sql, args)
    for row in icursor:
        if qdict.get(row["id"], {}).get("precip") or row["sum"] is None:
            continue
        pcpn[row["id"]] = f"{row['sum']:5.2f}"

    # 0z to 12z low temperature
    lows = {}
    sql = """
        SELECT id, round(min(tmpf)::numeric,0) as min_tmpf,
        count(tmpf) as obs FROM
        current_log c JOIN stations t on (t.iemid = c.iemid)
        WHERE t.network = ANY(%s) and valid >= %s
        and valid < %s  and tmpf > -99 GROUP by id
    """
    args = (NETWORKS, today0z, now12z)
    icursor.execute(sql, args)
    for row in icursor:
        if qdict.get(row["id"], {}).get("tmpf"):
            continue
        lows[row["id"]] = row["min_tmpf"]

    tt = yesterday6z.strftime("%d %b %Y").upper()
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", delete=False
    ) as fh:
        fh.write("\n\n\n")
        for netid in NETWORKS:
            networkname = "AWOS" if netid == "IA_ASOS" else netid
            fh.write(
                f".BR DMX {now12z:%m%d} Z "
                "DH06/TAIRVX/DH12/TAIRVP/PPDRVZ/SFDRVZ/SDIRVZ\n"
                f": IOWA {networkname} RTP FIRST GUESS "
                "PROCESSED BY THE IEM\n"
                f":   06Z to 06Z HIGH TEMPERATURE FOR {tt}\n"
                ":   00Z TO 12Z TODAY LOW TEMPERATURE\n"
                ":   12Z YESTERDAY TO 12Z TODAY RAINFALL\n"
                ":   ...BASED ON REPORTED OBS...\n"
            )
            ids = list(nt.sts.keys())
            ids.sort()
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
                myp = pcpn.get(sid, "M")
                if network != "IA_ASOS":
                    myp = "M"
                _fmt = asosfmt if netid == "IA_ASOS" else fmt
                fh.write(
                    _fmt
                    % (
                        sid,
                        nt.sts[sid]["name"],
                        highs.get(sid, "M"),
                        lows.get(sid, "M"),
                        myp,
                        "M",
                        "M",
                    )
                )

            fh.write(".END\n\n")

    pqstr = f"plot ac {now12z:%Y%m%d}0000 awos_rtp.shef awos_rtp.shef shef"
    subprocess.call(["pqinsert", "-p", pqstr, fh.name])
    os.unlink(fh.name)
    pgconn.close()


if __name__ == "__main__":
    main()
