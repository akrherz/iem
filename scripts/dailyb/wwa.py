"""Some simple summary stats for the IEM Daily Bulletin..."""

import datetime
from zoneinfo import ZoneInfo

from pyiem.util import get_dbconn, utc

POSTGIS = get_dbconn("postgis")
cursor = POSTGIS.cursor()

textfmt = (
    "             Summary +_________ By WFO ____________+  Watches\n"
    "Type         US   IA | ARX   DVN   DMX   OAX   FSD |  US\n"
    "Tornado     %(TOu)3s  %(TOi)3s | %(TOARX)3s   %(TODVN)3s   "
    "%(TODMX)3s   %(TOOAX)3s   %(TOFSD)3s | %(TORw)3s\n"
    "Svr Tstorm  %(SVu)3s  %(SVi)3s | %(SVARX)3s   %(SVDVN)3s   "
    "%(SVDMX)3s   %(SVOAX)3s   %(SVFSD)3s | %(SVRw)3s\n"
    "Flash Flood %(FFu)3s  %(FFi)3s | %(FFARX)3s   %(FFDVN)3s   "
    "%(FFDMX)3s   %(FFOAX)3s   %(FFFSD)3s | N/A\n"
    "\n"
    "ARX = LaCrosse, WI  DVN = Davenport, IA    DMX = Des Moines, IA\n"
    "OAX = Omaha, NE     FSD = Sioux Falls, SD\n"
    "\n"
)

htmlfmt = """
<table cellpadding="3" cellspacing="0" border="1">
<tr>
 <td></td>
 <th colspan="2">Summary</th>
 <th colspan="5">By WFO</th>
 <th>Watches</th></tr>
<tr>
 <th>Type</th>
 <th>US</th><th>IA</th>
 <th>ARX</th><th>DVN</th><th>DMX</th><th>OAX</th><th>FSD</th>
 <th>US</th></tr>
<tr>
 <th>Tornado</th>
 <td>%(TOu)3s</td><td>%(TOi)3s</td>
 <td>%(TOARX)3s</td><td>%(TODVN)3s</td><td>%(TODMX)3s</td>
   <td>%(TOOAX)3s</td><td>%(TOFSD)3s</td>
 <td>%(TORw)3s</td></tr>
<tr>
 <th>Svr Tstorm</th>
 <td>%(SVu)3s</td><td>%(SVi)3s</td>
 <td>%(SVARX)3s</td><td>%(SVDVN)3s</td><td>%(SVDMX)3s</td>
 <td>%(SVOAX)3s</td><td>%(SVFSD)3s</td>
 <td>%(SVRw)3s</td></tr>
<tr>
 <th>Flash Flood</th>
 <td>%(FFu)3s</td><td>%(FFi)3s</td>
 <td>%(FFARX)3s</td><td>%(FFDVN)3s</td><td>%(FFDMX)3s</td>
 <td>%(FFOAX)3s</td><td>%(FFFSD)3s</td><td>---</td></tr>
</table>

<p>ARX = LaCrosse, WI  DVN = Davenport, IA    DMX = Des Moines, IA
OAX = Omaha, NE     FSD = Sioux Falls, SD

"""


def run(sts=None, ets=None):
    """Generate listing of warning counts"""
    # default for CST yesterday
    if sts is None or ets is None:
        yest = utc() - datetime.timedelta(hours=24)
        yest = yest.replace(second=0, microsecond=0, minute=0)
        ts = yest.astimezone(ZoneInfo("America/Chicago"))
        sts = ts.replace(hour=0)
        ets = sts + datetime.timedelta(hours=24)

    d = {}

    # Get US states
    d["TOu"] = 0
    d["SVu"] = 0
    d["FFu"] = 0
    cursor.execute(
        f"select phenomena, count(*) from sbw_{sts.year} "
        "WHERE status = 'NEW' and issue >= %s and issue < %s "
        "and phenomena IN ('TO','SV','FF') GROUP by phenomena",
        (sts, ets),
    )
    for row in cursor:
        d["%su" % (row[0],)] = row[1]

    # Get Iowa
    d["TOi"] = 0
    d["SVi"] = 0
    d["FFi"] = 0
    cursor.execute(
        f"select phenomena, count(*) as count from sbw_{sts.year} w, states s "
        "WHERE ST_intersects(s.the_geom, w.geom) and s.state_abbr = 'IA' "
        "and issue >= %s and issue < %s and status = 'NEW' "
        "and phenomena IN ('TO','SV','FF') GROUP by phenomena",
        (sts, ets),
    )
    for row in cursor:
        d["%si" % (row[0],)] = row[1]

    # Get per WFO
    for wfo in ["DMX", "DVN", "ARX", "FSD", "OAX"]:
        d["TO%s" % (wfo,)] = 0
        d["SV%s" % (wfo,)] = 0
        d["FF%s" % (wfo,)] = 0
    cursor.execute(
        f"SELECT phenomena, wfo, count(*) as count from sbw_{sts.year} WHERE "
        "issue >= %s and issue < %s and status = 'NEW' "
        "and phenomena IN ('TO','SV','FF') and "
        "wfo in ('DMX','FSD','ARX','DVN','OAX') GROUP by wfo, phenomena",
        (sts, ets),
    )
    for row in cursor:
        d["%s%s" % (row[0], row[1])] = row[2]

    # SPC Watches
    d["TORw"] = 0
    d["SVRw"] = 0

    cursor.execute(
        "SELECT type, count(*) as count from watches WHERE "
        "issued >= %s and issued < %s GROUP by type",
        (sts, ets),
    )
    for row in cursor:
        d["%sw" % (row[0],)] = row[1]

    label = "%s - %s" % (
        sts.strftime("%-I %p %-d %b %Y"),
        ets.strftime("%-I %p %-d %b %Y %Z"),
    )

    txt = "> NWS Watch/Warning Summary for %s\n" % (label,)
    html = "<h3>NWS Watch/Warning Summary for %s</h3>" % (label,)

    txt += textfmt % d
    html += htmlfmt % d

    return txt, html


def main():
    """Lets actually do something"""
    sts = utc(2015, 5, 4, 0)
    sts = sts.astimezone(ZoneInfo("America/Chicago"))
    sts = sts.replace(hour=0)
    ets = sts + datetime.timedelta(hours=24)
    txt, html = run(sts, ets)
    print(txt)
    print(html)


if __name__ == "__main__":
    main()
