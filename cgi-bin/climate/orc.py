"""A specialized report"""
import datetime
from io import StringIO

from pyiem.util import get_dbconn
from pyiem.webutil import iemapp


def averageTemp(db, hi="high", lo="low"):
    """Average Temp"""
    highSum, lowSum = 0, 0
    for day in db.keys():
        highSum += db[day][hi]
        lowSum += db[day][lo]

    highAvg = highSum / float(len(db))
    lowAvg = lowSum / float(len(db))

    return highAvg, lowAvg


def hdd(db, hi="high", lo="low"):
    """Compute heating degree days"""
    dd = 0
    for day in db:
        h = db[day][hi]
        low = db[day][lo]
        a = (h + low) / 2.00
        if a < 65:
            dd += 65.0 - a
    return dd


def cdd(db, hi="high", lo="low"):
    """Cooling Degree Days"""
    dd = 0
    for day in db:
        h = db[day][hi]
        low = db[day][lo]
        a = (h + low) / 2.00
        if a > 65:
            dd += a - 65.0
    return dd


@iemapp()
def application(_environ, start_response):
    """Go Main Go"""
    COOP = get_dbconn("coop")
    ccursor = COOP.cursor()
    IEM = get_dbconn("iem")
    icursor = IEM.cursor()
    ASOS = get_dbconn("asos")
    acursor = ASOS.cursor()

    ADJUSTMENT = 0
    now = datetime.datetime.now()
    e = now.replace(day=17)
    s = (e - datetime.timedelta(days=31)).replace(day=18)
    db = {}
    now = s
    while now <= e:
        db[now.strftime("%m%d")] = {
            "high": -99,
            "low": -99,
            "avg_high": -99,
            "avg_low": -99,
        }
        now += datetime.timedelta(days=1)

    # Get Sioux City data
    icursor.execute(
        """SELECT day, max_tmpf, min_tmpf from
        summary s JOIN stations t ON (t.iemid = s.iemid)
        WHERE t.id = 'SUX' and day >= %s and
        day <= %s and max_tmpf is not null and min_tmpf is not null
        """,
        (s.date(), e.date()),
    )
    for row in icursor:
        db[row[0].strftime("%m%d")]["high"] = row[1] + ADJUSTMENT
        db[row[0].strftime("%m%d")]["low"] = row[2] + ADJUSTMENT

    # Lemars
    ccursor.execute(
        """SELECT high, low, valid  from climate
        WHERE station = 'IA4735'"""
    )
    for row in ccursor:
        if row[2].strftime("%m%d") not in db:
            continue
        db[row[2].strftime("%m%d")]["avg_high"] = row[0]
        db[row[2].strftime("%m%d")]["avg_low"] = row[1]

    # Compute Average wind speed
    acursor.execute(
        """
      SELECT station, avg(sknt) from alldata where station in ('SHL', 'ORC')
      and valid BETWEEN '%s' and '%s' and sknt >= 0
      GROUP by station ORDER by station DESC
      """,
        (s, e),
    )
    awind = -99
    if acursor.rowcount > 0:
        row = acursor.fetchone()
        awind = row[1]

    headers = [("Content-type", "text/plain")]
    start_response("200 OK", headers)
    sio = StringIO()
    sio.write("  Orange City Climate Summary\n")
    sio.write("%15s %6s %6s\n" % ("DATE", "HIGH", "LOW"))
    now = s
    while now <= e:
        sio.write(
            ("%15s %6i %6i %6i %6i\n")
            % (
                now.strftime("%Y-%m-%d"),
                db[now.strftime("%m%d")]["high"],
                db[now.strftime("%m%d")]["low"],
                db[now.strftime("%m%d")]["avg_high"],
                db[now.strftime("%m%d")]["avg_low"],
            )
        )
        now += datetime.timedelta(days=1)

    h, low = averageTemp(db)
    ch, cl = averageTemp(db, "avg_high", "avg_low")

    l_hdd = hdd(db)
    c_hdd = hdd(db, "avg_high", "avg_low")

    l_cdd = cdd(db)
    c_cdd = cdd(db, "avg_high", "avg_low")

    sio.write(
        """
Summary Information [%s - %s]
-------------------
              Observed     |  Climate  |  Diff
    High        %4.1f           %4.1f       %4.1f
    Low         %4.1f           %4.1f       %4.1f
 HDD(base65)    %4.0f           %4.0f       %4.0f
 CDD(base65)    %4.0f           %4.0f       %4.0f
 Wind[MPH]      %4.1f             M          M
"""
        % (
            s.strftime("%d %B %Y"),
            e.strftime("%d %B %Y"),
            h,
            ch,
            h - ch,
            low,
            cl,
            low - cl,
            l_hdd,
            c_hdd,
            l_hdd - c_hdd,
            l_cdd,
            c_cdd,
            l_cdd - c_cdd,
            awind,
        )
    )
    return [sio.getvalue().encode("ascii")]
