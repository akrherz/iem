"""Generate a First Guess RTP that the bureau can use for their product
"""
from __future__ import print_function
import datetime
import subprocess

import pytz
from pyiem.tracker import loadqc
from pyiem import network
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    nt = network.Table("AWOS")
    qdict = loadqc()
    pgconn = get_dbconn("iem", user="nobody")
    icursor = pgconn.cursor()

    utc = datetime.datetime.utcnow()
    ets = utc.replace(
        tzinfo=pytz.utc, hour=0, minute=0, second=0, microsecond=0
    )
    sts12z = ets + datetime.timedelta(hours=-12)
    sts6z = ets + datetime.timedelta(hours=-18)
    sts24h = ets + datetime.timedelta(days=-1)

    fmt = "%-6s:%-19s: %3s / %3s / %5s / %4s / %2s\n"

    out = open("/tmp/awos_rtp.shef", "w")
    out.write(
        """


.BR DMX %s Z DH00/TAIRVS/TAIRVI/PPDRVZ/SFDRVZ/SDIRVZ
: IOWA AWOS RTP FIRST GUESS PROCESSED BY THE IEM
:   06Z TO 00Z HIGH TEMPERATURE FOR %s
:   06Z TO 00Z LOW TEMPERATURE FOR %s
:   00Z YESTERDAY TO 00Z TODAY RAINFALL
:   ...BASED ON REPORTED OBS...
"""
        % (
            ets.strftime("%m%d"),
            sts12z.strftime("%d %b %Y").upper(),
            sts12z.strftime("%d %b %Y").upper(),
        )
    )

    # We get 18 hour highs
    highs = {}
    sql = """SELECT t.id as station,
        round(max(tmpf)::numeric,0) as max_tmpf,
        count(tmpf) as obs FROM current_log c, stations t
        WHERE t.iemid = c.iemid and t.network = 'AWOS' and valid > %s
            and valid < %s
        and tmpf > -99 GROUP by t.id """
    args = (sts6z, ets)
    icursor.execute(sql, args)
    for row in icursor:
        if qdict.get(row[0], {}).get("tmpf"):
            continue
        highs[row[0]] = row[1]

    # 00 UTC to 00 UTC Preciptation
    pcpn = {}
    icursor.execute(
        """
        select id as station, sum(precip) from
        (select t.id, extract(hour from valid) as hour,
        max(phour) as precip from current_log c, stations t
        WHERE t.network = 'AWOS' and t.iemid = c.iemid
        and valid  >= %s and valid < %s
        GROUP by t.id, hour) as foo
        GROUP by id""",
        (sts24h, ets),
    )
    for row in icursor:
        if qdict.get(row[0], {}).get("precip") or row[1] is None:
            continue
        pcpn[row[0]] = "%5.2f" % (row[1],)

    lows = {}
    icursor.execute(
        """SELECT t.id as station,
        round(min(tmpf)::numeric,0) as min_tmpf,
        count(tmpf) as obs FROM current_log c, stations t
        WHERE t.iemid = c.iemid and t.network = 'AWOS' and valid > %s and
        valid < %s and tmpf > -99 GROUP by t,id""",
        (sts6z, ets),
    )

    for row in icursor:
        if qdict.get(row[0], {}).get("tmpf"):
            continue
        lows[row[0]] = row[1]

    ids = list(nt.sts.keys())
    ids.sort()
    for sid in ids:
        myP = pcpn.get(sid, "M")
        myH = highs.get(sid, "M")
        myL = lows.get(sid, "M")

        out.write(fmt % (sid, nt.sts[sid]["name"], myH, myL, myP, "M", "M"))

    out.write(".END\n")
    out.close()

    cmd = (
        "/home/ldm/bin/pqinsert -p 'plot ac %s0000 awos_rtp_00z.shef "
        "awos_rtp_00z.shef shef' /tmp/awos_rtp.shef"
    ) % (ets.strftime("%Y%m%d"),)
    subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    main()
