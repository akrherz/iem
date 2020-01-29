"""
Return a simple CSV of recent observations from the database
"""

import memcache
from paste.request import parse_formvars
from pyiem.util import get_dbconn


def run(sid):
    """ run() """
    dbconn = get_dbconn("iem", user="nobody")
    cursor = dbconn.cursor()
    cursor.execute(
        """SELECT valid at time zone 'UTC', tmpf, dwpf, raw,
    ST_x(geom), ST_y(geom) , tmpf, dwpf, drct, sknt, phour, alti, mslp, vsby,
    gust from current_log c JOIN
    stations t on (t.iemid = c.iemid) WHERE t.id = %s and t.metasite = 'f'
    ORDER by valid ASC""",
        (sid,),
    )

    res = (
        "station,utcvalid,lon,lat,tmpf,dwpf,drct,sknt,"
        "p01i,alti,mslp,vsby,gust,raw\n"
    )
    for row in cursor:
        res += ("%s,%s,%.4f,%.4f,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" "") % (
            sid,
            row[0].strftime("%Y-%m-%d %H:%M"),
            row[4],
            row[5],
            row[6],
            row[7],
            row[8],
            row[9],
            row[10],
            row[11],
            row[12],
            row[13],
            row[14],
            row[3],
        )

    return res.replace("None", "M")


def application(environ, start_response):
    """Go Main Go"""
    start_response("200 OK", [("Content-type", "text/plain")])
    form = parse_formvars(environ)
    sid = form.get("station", "AMW")[:5]

    mckey = "/cgi-bin/request/recent.py|%s" % (sid,)
    mc = memcache.Client(["iem-memcached:11211"], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run(sid)
        mc.set(mckey, res, 300)

    return [res.encode("ascii")]
