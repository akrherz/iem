"""Generate a First Guess RTP that the bureau can use for their product."""
import datetime
import os
import subprocess
import tempfile

import pytz
from pyiem import network
from pyiem.tracker import loadqc
from pyiem.util import get_dbconn, utc


def main():
    """Go Main Go."""
    nt = network.Table("IA_ASOS")
    qdict = loadqc()
    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor()

    ets = utc().replace(
        tzinfo=pytz.utc, hour=0, minute=0, second=0, microsecond=0
    )
    sts12z = ets + datetime.timedelta(hours=-12)
    sts6z = ets + datetime.timedelta(hours=-18)
    sts24h = ets + datetime.timedelta(days=-1)

    fmt = "%-6s:%-19s: %3s / %3s / %5s / %4s / %2s\n"

    # We get 18 hour highs
    highs = {}
    sql = """SELECT t.id as station,
        round(max(tmpf)::numeric,0) as max_tmpf,
        count(tmpf) as obs FROM current_log c, stations t
        WHERE t.iemid = c.iemid and t.network = 'IA_ASOS' and valid > %s
            and valid < %s
        and tmpf > -99 GROUP by t.id """
    icursor.execute(sql, (sts6z, ets))
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
        WHERE t.network = 'IA_ASOS' and t.iemid = c.iemid
        and valid  >= %s and valid < %s
        GROUP by t.id, hour) as foo
        GROUP by id""",
        (sts24h, ets),
    )
    for row in icursor:
        if qdict.get(row[0], {}).get("precip") or row[1] is None:
            continue
        pcpn[row[0]] = f"{row[1]:5.2f}"

    lows = {}
    icursor.execute(
        """SELECT t.id as station,
        round(min(tmpf)::numeric,0) as min_tmpf,
        count(tmpf) as obs FROM current_log c, stations t
        WHERE t.iemid = c.iemid and t.network = 'IA_ASOS' and valid > %s and
        valid < %s and tmpf > -99 GROUP by t,id""",
        (sts6z, ets),
    )

    for row in icursor:
        if qdict.get(row[0], {}).get("tmpf"):
            continue
        lows[row[0]] = row[1]

    ids = list(nt.sts.keys())
    ids.sort()

    with tempfile.NamedTemporaryFile("w", delete=False) as fh:
        fh.write(
            f"""


.BR DMX {ets:%m%d} Z DH00/TAIRVS/TAIRVI/PPDRVZ/SFDRVZ/SDIRVZ
: IOWA AWOS RTP FIRST GUESS PROCESSED BY THE IEM
:   06Z TO 00Z HIGH TEMPERATURE FOR {sts12z:%d %b %Y}
:   06Z TO 00Z LOW TEMPERATURE FOR {sts12z:%d %b %Y}
:   00Z YESTERDAY TO 00Z TODAY RAINFALL
:   ...BASED ON REPORTED OBS...
"""
        )
        for sid in ids:
            if nt.sts[sid]["attributes"].get("IS_AWOS") != "1":
                continue
            myP = pcpn.get(sid, "M")
            myH = highs.get(sid, "M")
            myL = lows.get(sid, "M")

            fh.write(fmt % (sid, nt.sts[sid]["name"], myH, myL, myP, "M", "M"))

        fh.write(".END\n")

    cmd = [
        "pqinsert",
        "-p",
        f"plot ac {ets:%Y%m%d}0000 awos_rtp_00z.shef awos_rtp_00z.shef shef",
        fh.name,
    ]
    subprocess.call(cmd)
    os.unlink(fh.name)


if __name__ == "__main__":
    main()
