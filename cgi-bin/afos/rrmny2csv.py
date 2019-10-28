#!/usr/bin/env python
""" One off conversion of RRMBUF to CSV """

import pytz
from pyiem.util import get_dbconn, ssw


def do(cursor, wfo):
    """workflow"""
    cursor.execute(
        """
    SELECT data, entered from products where pil = 'RRM%s' and
    entered > 'TODAY'::date  and
    data ~* '.A' ORDER by entered DESC
    """
        % (wfo,)
    )

    if cursor.rowcount == 0:
        return "# RRM%s not found?!?!\n" % (wfo,), ""
    meta = ""
    meat = ""
    for row in cursor:
        meta += ("# based on IEM processing of RRM%s dated: %s UTC\n") % (
            wfo,
            row[1].astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M"),
        )
        data = row[0].replace("\001", "")
        for line in data.split("\r\r\n"):
            if not line.startswith(".A"):
                continue
            tokens = line.split()
            sid = tokens[1]
            dv = "%s %s" % (tokens[2], tokens[4][2:6])
            val = tokens[5].split('"')[0]
            tokens2 = " ".join(tokens[5:]).split()
            # ssw(line+"\n")
            lbl = line.split('"')[1]
            src = ""
            if lbl.find("  ") > 0:
                t = lbl.split("  ")
                src = t[2]
                lbl = t[1]
            meat += ("%9s,%s,%s,%s,%s,%s,%s\n") % (
                sid,
                dv,
                val,
                tokens2[0].split("=")[1],
                tokens2[1].split("=")[1],
                lbl,
                src,
            )

    return meta, meat


def run():
    """ Do Stuff """
    pgconn = get_dbconn("afos", user="nobody")
    cursor = pgconn.cursor()
    ssw("Content-type:text/plain\n\n")
    m1 = ""
    m2 = ""
    for wfo in ["OKX", "ALY", "BTV", "BUF", "BGM"]:
        meta, meat = do(cursor, wfo)
        m1 += meta
        m2 += meat

    ssw(m1)
    ssw("id,timestamp,value,lat,lon,name,source\n")
    ssw(m2)


if __name__ == "__main__":
    run()
