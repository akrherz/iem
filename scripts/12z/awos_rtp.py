"""
 Generate a RTP product for the weather bureau as my database as more AWOS
 obs than what they get
"""
import os
import subprocess
import datetime

from pyiem.tracker import loadqc
from pyiem import network
from pyiem.util import get_dbconn, utc


def main():
    """Go Main Go"""
    nt = network.Table("IA_ASOS")
    qdict = loadqc()
    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor()

    # We run at 12z
    now12z = utc().replace(hour=12, minute=0, second=0, microsecond=0)
    today6z = now12z.replace(hour=6)
    today0z = now12z.replace(hour=0)
    yesterday6z = today6z - datetime.timedelta(days=1)
    yesterday12z = now12z - datetime.timedelta(days=1)

    fmt = "%-6s:%-19s: %3s / %3s / %5s / %4s / %2s\n"

    shef_fn = "/tmp/awos_rtp.shef"
    out = open(shef_fn, "w", encoding="utf8")
    out.write(
        (
            "\n"
            "\n"
            "\n"
            ".BR DMX %s Z DH06/TAIRVX/DH12/TAIRVP/PPDRVZ/SFDRVZ/SDIRVZ\n"
            ": IOWA AWOS RTP FIRST GUESS PROCESSED BY THE IEM\n"
            ":   06Z to 06Z HIGH TEMPERATURE FOR %s\n"
            ":   00Z TO 12Z TODAY LOW TEMPERATURE\n"
            ":   12Z YESTERDAY TO 12Z TODAY RAINFALL\n"
            ":   ...BASED ON REPORTED OBS...\n"
        )
        % (now12z.strftime("%m%d"), yesterday6z.strftime("%d %b %Y").upper())
    )

    # 6z to 6z high temperature
    highs = {}
    sql = """SELECT id,
        round(max(tmpf)::numeric,0) as max_tmpf,
        count(tmpf) as obs FROM current_log c, stations t
        WHERE t.iemid = c.iemid and t.network = 'IA_ASOS' and valid >= %s
        and valid < %s
        and tmpf > -99 GROUP by id """
    args = (yesterday6z, today6z)
    icursor.execute(sql, args)
    for row in icursor:
        if qdict.get(row[0], {}).get("tmpf"):
            continue
        highs[row[0]] = row[1]

    # 12z to 12z precip
    pcpn = {}
    sql = """
        select id, sum(precip) from
        (select id, extract(hour from valid) as hour,
        max(phour) as precip from current_log c, stations t
        WHERE t.network = 'IA_ASOS' and t.iemid = c.iemid
        and valid  >= %s and valid < %s
        GROUP by id, hour) as foo
        GROUP by id
    """
    args = (yesterday12z, now12z)
    icursor.execute(sql, args)
    for row in icursor:
        if qdict.get(row[0], {}).get("precip") or row[1] is None:
            continue
        pcpn[row[0]] = "%5.2f" % (row[1],)

    # 0z to 12z low temperature
    lows = {}
    sql = """
        SELECT id, round(min(tmpf)::numeric,0) as min_tmpf,
        count(tmpf) as obs FROM
        current_log c JOIN stations t on (t.iemid = c.iemid)
        WHERE t.network = 'IA_ASOS' and valid >= %s
        and valid < %s  and tmpf > -99 GROUP by id
    """
    args = (today0z, now12z)
    icursor.execute(sql, args)
    for row in icursor:
        if qdict.get(row[0], {}).get("tmpf"):
            continue
        lows[row[0]] = row[1]

    ids = list(nt.sts.keys())
    ids.sort()
    for myid in ids:
        if nt.sts[myid]["attributes"].get("IS_ASOS") != "1":
            continue
        out.write(
            fmt
            % (
                myid,
                nt.sts[myid]["name"],
                highs.get(myid, "M"),
                lows.get(myid, "M"),
                pcpn.get(myid, "M"),
                "M",
                "M",
            )
        )

    out.write(".END\n")
    out.close()

    cmd = (
        "pqinsert -p 'plot ac %s0000 awos_rtp.shef awos_rtp.shef shef' %s"
    ) % (now12z.strftime("%Y%m%d"), shef_fn)
    subprocess.call(cmd, shell=True)
    os.unlink(shef_fn)


if __name__ == "__main__":
    main()
