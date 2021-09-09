""" One off conversion of RRMBUF to CSV """
from io import StringIO

import pytz
from pyiem.util import get_dbconn


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


def application(_environ, start_response):
    """Do Stuff"""
    pgconn = get_dbconn("afos", user="nobody")
    cursor = pgconn.cursor()
    headers = [("Content-type", "text/plain")]
    start_response("200 OK", headers)
    m1 = StringIO()
    m2 = StringIO()
    for wfo in ["OKX", "ALY", "BTV", "BUF", "BGM"]:
        meta, meat = do(cursor, wfo)
        m1.write(meta)
        m2.write(meat)

    m1.write("id,timestamp,value,lat,lon,name,source\n")
    m1.write(m2.getvalue())
    return [m1.getvalue().encode("ascii")]
