"""give me some AFOS data please."""
from io import StringIO

from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape


def pil_logic(s):
    """Convert the CGI pil value into something we can query

    Args:
      s (str): The CGI variable wanted

    Returns:
      list of PILs to send to the database"""
    if s == "":
        return []
    s = s.upper()
    pils = []
    if s.find(",") == -1:
        pils.append(s)
    else:
        pils = s.split(",")

    res = []
    for pil in pils:
        if pil[:3] == "WAR":
            for q in [
                "FLS",
                "FFS",
                "AWW",
                "TOR",
                "SVR",
                "FFW",
                "SVS",
                "LSR",
                "SPS",
                "WSW",
                "FFA",
                "WCN",
                "NPW",
            ]:
                res.append("%s%s" % (q, pil[3:6]))
        else:
            res.append("%6.6s" % (pil.strip() + "      ",))
    return res


def application(environ, start_response):
    """Process the request"""
    # Attempt to keep the file from downloading and just displaying in chrome
    form = parse_formvars(environ)
    pils = pil_logic(form.get("pil", ""))
    try:
        limit = int(form.get("limit", 1))
    except ValueError:
        limit = 1
    center = form.get("center", "")[:4]
    sdate = form.get("sdate", "")[:10]
    edate = form.get("edate", "")[:10]
    ttaaii = form.get("ttaaii", "")[:6]
    fmt = form.get("fmt", "text")
    headers = [("X-Content-Type-Options", "nosniff")]
    if form.get("dl") == "1":
        headers.append(("Content-type", "application/octet-stream"))
        headers.append(
            ("Content-disposition", "attachment; filename=afos.txt")
        )
    else:
        if fmt == "text":
            headers.append(("Content-type", "text/plain"))
        elif fmt == "html":
            headers.append(("Content-type", "text/html"))
    start_response("200 OK", headers)
    if not pils:
        return [b"ERROR: No pil specified..."]
    centerlimit = "" if center == "" else (" and source = '%s' " % (center,))
    timelimit = ""
    if sdate != "":
        timelimit += " and entered >= '%s' " % (sdate,)
    if edate != "":
        timelimit += " and entered < '%s' " % (edate,)

    sio = StringIO()
    if pils[0][:3] == "MTR":
        access = get_dbconn("iem")
        cursor = access.cursor()
        sql = """
            SELECT raw from current_log c JOIN stations t
            on (t.iemid = c.iemid)
            WHERE raw != '' and id = '%s' ORDER by valid DESC LIMIT %s
            """ % (
            pils[0][3:].strip(),
            limit,
        )
        cursor.execute(sql)
        for row in cursor:
            if fmt == "html":
                sio.write("<pre>\n")
            else:
                sio.write("\001\n")
            if fmt == "html":
                sio.write(html_escape(row[0].replace("\r\r\n", "\n")))
            else:
                sio.write(row[0].replace("\r\r\n", "\n"))
            if fmt == "html":
                sio.write("</pre>\n")
            else:
                sio.write("\003\n")
        if cursor.rowcount == 0:
            sio.write(
                "ERROR: METAR lookup for %s failed" % (pils[0][3:].strip(),)
            )
        return [sio.getvalue().encode("ascii", "ignore")]

    try:
        mydb = get_dbconn("afos", user="nobody")
    except Exception:  # noqa
        return [b"Error Connecting to Database, please try again!"]

    cursor = mydb.cursor()

    if len(pils) == 1:
        pillimit = " pil = '%s' " % (pils[0],)
        if len(pils[0].strip()) == 3:
            pillimit = " substr(pil, 1, 3) = '%s' " % (pils[0].strip(),)
    else:
        pillimit = " pil in %s" % (tuple(pils),)
    ttlimit = ""
    if len(ttaaii) == 6:
        ttlimit = " and wmo = '%s' " % (ttaaii,)

    # Do optimized query first, see if we can get our limit right away
    sql = """
        SELECT data, pil,
        to_char(entered at time zone 'UTC', 'YYYYMMDDHH24MI') as ts
        from products WHERE %s
        and entered > now() - '31 days'::interval %s %s %s
        ORDER by entered DESC LIMIT %s""" % (
        pillimit,
        centerlimit,
        timelimit,
        ttlimit,
        limit,
    )

    cursor.execute(sql)
    if cursor.rowcount != limit:
        sql = """
            SELECT data, pil,
            to_char(entered at time zone 'UTC', 'YYYYMMDDHH24MI') as ts
            from products WHERE %s %s %s %s
            ORDER by entered DESC LIMIT %s """ % (
            pillimit,
            centerlimit,
            timelimit,
            ttlimit,
            limit,
        )
        cursor.execute(sql)

    for row in cursor:
        if fmt == "html":
            sio.write(
                (
                    '<a href="/wx/afos/p.php?pil=%s&e=%s">Permalink</a> '
                    "for following product: "
                )
                % (row[1], row[2])
            )
            sio.write("<br /><pre>\n")
        else:
            sio.write("\001\n")
        # Remove control characters from the product as we are including
        # them manually here...
        if fmt == "html":
            sio.write(
                html_escape(row[0])
                .replace("\003", "")
                .replace("\001\r\r\n", "")
                .replace("\r\r\n", "\n")
            )
        else:
            sio.write(
                (row[0])
                .replace("\003", "")
                .replace("\001\r\r\n", "")
                .replace("\r\r\n", "\n")
            )
        if fmt == "html":
            sio.write("</pre><hr>\n")
        else:
            sio.write("\n\003\n")

    if cursor.rowcount == 0:
        sio.write("ERROR: Could not Find: %s" % (",".join(pils),))
    return [sio.getvalue().encode("ascii", "ignore")]


def test_pil_logic():
    """Make sure our pil logic works! """
    res = pil_logic("AFDDMX")
    assert len(res) == 1
    assert res[0] == "AFDDMX"
    res = pil_logic("WAREWX")
    assert len(res) == 12
    res = pil_logic("STOIA,AFDDMX")
    assert res[0] == "STOIA "
    assert res[1] == "AFDDMX"
