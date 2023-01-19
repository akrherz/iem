"""give me some AFOS data please."""
import re
import zipfile
from datetime import datetime, timezone
from io import BytesIO, StringIO

from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape

DATE_REGEX = re.compile(r"^[0-9]{4}\-\d+\-\d+")
WARPIL = "FLS FFS AWW TOR SVR FFW SVS LSR SPS WSW FFA WCN NPW".split()


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
            for q in WARPIL:
                res.append(f"{q}{pil[3:6]}")
        else:
            res.append(f"{pil.strip():6.6s}")
    return res


def get_date(raw):
    """Handle date errors more gracefully."""
    if raw is None or raw.strip() == "":
        return None
    if not DATE_REGEX.match(raw):
        return False
    # Option 1, provided just YYYY-MM-DD
    if len(raw) <= 10:
        dt = datetime.strptime(raw, "%Y-%m-%d")
    else:
        try:
            dt = datetime.strptime(raw[:16], "%Y-%m-%dT%H:%M")
        except ValueError:
            return False

    return dt.replace(tzinfo=timezone.utc)


def zip_handler(cursor):
    """Stream back a zipfile!"""
    bio = BytesIO()
    with zipfile.ZipFile(bio, "w") as zfp:
        for row in cursor:
            zfp.writestr(f"{row[1]}_{row[2]}.txt", row[0])
    bio.seek(0)
    return [bio.getvalue()]


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
    sdate = get_date(form.get("sdate"))
    edate = get_date(form.get("edate"))
    if sdate is False or edate is False:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [
            b"Either sdate or edate failed form "
            b"YYYY-mm-dd or YYYY-mm-ddTHH:MM, both are UTC dates"
        ]
    ttaaii = form.get("ttaaii", "")[:6]
    fmt = form.get("fmt", "text")
    headers = [("X-Content-Type-Options", "nosniff")]
    if form.get("dl") == "1" or fmt == "zip":
        suffix = "zip" if fmt == "zip" else "txt"
        headers.append(("Content-type", "application/octet-stream"))
        headers.append(
            ("Content-disposition", f"attachment; filename=afos.{suffix}")
        )
    else:
        if fmt == "text":
            headers.append(("Content-type", "text/plain"))
        elif fmt == "html":
            headers.append(("Content-type", "text/html"))
    start_response("200 OK", headers)
    if not pils:
        return [b"ERROR: No pil specified..."]
    centerlimit = "" if center == "" else f" and source = '{center}' "
    timelimit = ""
    if sdate is not None:
        timelimit += f" and entered >= '{sdate}' "
    if edate is not None:
        timelimit += f" and entered < '{edate}' "

    sio = StringIO()
    if pils[0][:3] == "MTR":
        access = get_dbconn("iem")
        cursor = access.cursor()
        sql = (
            "SELECT raw from current_log c JOIN stations t on "
            "(t.iemid = c.iemid) WHERE raw != '' and "
            f"id = '{pils[0][3:].strip()}' ORDER by valid DESC LIMIT {limit}"
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
            sio.write(f"ERROR: METAR lookup for {pils[0][3:].strip()} failed")
        return [sio.getvalue().encode("ascii", "ignore")]

    try:
        mydb = get_dbconn("afos")
    except Exception:  # noqa
        return [b"Error Connecting to Database, please try again!"]

    cursor = mydb.cursor()

    if len(pils) == 1:
        pillimit = f" pil = '{pils[0]}' "
        if len(pils[0].strip()) == 3:
            pillimit = f" substr(pil, 1, 3) = '{pils[0].strip()}' "
    else:
        pillimit = f" pil in {tuple(pils)}"
    ttlimit = ""
    if len(ttaaii) == 6:
        ttlimit = f" and wmo = '{ttaaii}' "

    # Do optimized query first, see if we can get our limit right away
    sql = (
        "SELECT data, pil, "
        "to_char(entered at time zone 'UTC', 'YYYYMMDDHH24MI') as ts "
        f"from products WHERE {pillimit} "
        f"and entered > now() - '31 days'::interval {centerlimit} "
        f"{timelimit} {ttlimit} ORDER by entered DESC LIMIT {limit}"
    )
    cursor.execute(sql)
    if cursor.rowcount != limit:
        sql = (
            "SELECT data, pil, "
            "to_char(entered at time zone 'UTC', 'YYYYMMDDHH24MI') as ts "
            f"from products WHERE {pillimit} {centerlimit} {timelimit} "
            f"{ttlimit} ORDER by entered DESC LIMIT {limit}"
        )
        cursor.execute(sql)
    if fmt == "zip":
        return zip_handler(cursor)

    for row in cursor:
        if fmt == "html":
            sio.write(
                f'<a href="/wx/afos/p.php?pil={row[1]}&e={row[2]}">'
                "Permalink</a> for following product: "
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
        sio.write(f"ERROR: Could not Find: {','.join(pils)}")
    return [sio.getvalue().encode("ascii", "ignore")]


def test_pil_logic():
    """Make sure our pil logic works!"""
    res = pil_logic("AFDDMX")
    assert len(res) == 1
    assert res[0] == "AFDDMX"
    res = pil_logic("WAREWX")
    assert len(res) == 12
    res = pil_logic("STOIA,AFDDMX")
    assert res[0] == "STOIA "
    assert res[1] == "AFDDMX"
