"""
 Generate and email a report to the IASS folks with summarized IEM estimated
 COOP data included...
"""
import sys
from io import StringIO
import datetime
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

import psycopg2.extras
from pyiem.util import get_dbconn

DISTRICTS = [
    "North West",
    "North Central",
    "North East",
    "West Central",
    "Central",
    "East Central",
    "South West",
    "South Central",
    "South East",
]
STIDS = [
    [
        "Rock Rapids    RKRI4",
        "Sheldon    SHDI4",
        "Sibley    SIBI4",
        "Sioux Center    SIXI4",
        "Spirit Lake    VICI4",
        "Storm Lake    SLBI4",
    ],
    [
        "Algona    ALGI4",
        "Charles City    CIYI4",
        "Dakota City    DAKI4",
        "Hampton    HPTI4",
        "Mason City    MCWI4",
        "Osage    OSAI4",
    ],
    [
        "Cresco    CRCI4",
        "Decorah    DCRI4",
        "Dubuque    DLDI4",
        "Fayette    FYTI4",
        "Manchester    MHRI4",
        "Tripoli    TRPI4",
    ],
    [
        "Audubon    AUDI4",
        "Carroll    CINI4",
        "Jefferson    JFFI4",
        "Logan    LOGI4",
        "Mapleton    MPTI4",
        "Rockwell City    RKWI4",
    ],
    [
        "Boone    BNWI4",
        "Grinnell    GRII4",
        "Grundy Center    GNDI4",
        "Iowa Falls    IWAI4",
        "Marshalltown    MSHI4",
        "Webster City    WEBI4",
    ],
    [
        "Anamosa    AMOI4",
        "Cedar Rapids    CRPI4",
        "Clinton    CLNI4",
        "Lowden    LWDI4",
        "Maquoketa    MKTI4",
        "Vinton    VNTI4",
    ],
    [
        "Atlantic    ATLI4",
        "Clarinda    CLDI4",
        "Glenwood    GLNI4",
        "Oakland    OAKI4",
        "Red Oak    ROKI4",
        "Sidney    SIDI4",
    ],
    [
        "Allerton    ALRI4",
        "Beaconsfield    BCNI4",
        "Centerville    CNTI4",
        "Indianola    IDAI4",
        "Lamoni    3OI",
        "Osceola    OSEI4",
    ],
    [
        "Bloomfield    BLMI4",
        "Donnellson    DNNI4",
        "Fairfield    FRFI4",
        "Keosauqua    KEQI4",
        "Washington    WSHI4",
    ],
]


def compute_weekly(fp, sts, ets):
    """ Compute the weekly stats we need """
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Max daily high
    # min daily high
    # average temperature
    # departure from normal for average temp
    # Total precip
    # precip departure from normal
    # since 1 april precip
    # since 1 april departure
    # since 1 april GDD50
    # since 1 april departure
    sday = sts.strftime("%m%d")
    eday = ets.strftime("%m%d")
    apr1 = "%s-04-01" % (sts.year,)
    cursor.execute(
        """
    WITH obs as (
        SELECT id as station , climate_site,
        max(max_tmpf) as hi,
        min(min_tmpf)  as lo,
        avg((max_tmpf+min_tmpf)/2.) as avg,
        sum(case when pday > 0.009 then pday else 0 end) as total_p
        FROM summary s JOIN stations t on (t.iemid = s.iemid)
        WHERE day >= %s and day <= %s
        and t.network = 'IA_COOP' and max_tmpf > -90
        and min_tmpf < 90
        GROUP by station, climate_site
    ), april_obs as (
        SELECT id as station,  climate_site,
        sum(case when pday > 0.009 then pday else 0 end) as p,
        sum(gddxx(50,86,max_tmpf,min_tmpf)) as gdd
        from summary s JOIN stations t on (t.iemid = s.iemid)
        WHERE t.network = 'IA_COOP' and
        day >= %s and day <= %s
        GROUP by station, climate_site
    ), climo as (
        SELECT station,
        avg((high+low)/2.) as avg,
        sum(precip) as avg_p
        from climate51
        WHERE to_char(valid, 'mmdd') >= %s and to_char(valid, 'mmdd') <= %s
        GROUP by station
    ), april_climo as (
        SELECT station,
        sum(precip) as avg_p,
        sum(gdd50) as avg_gdd
        from climate51 WHERE extract(month from valid) > 3
        and to_char(valid, 'mmdd') < %s
        GROUP by station
    )  SELECT obs.station,
    obs.hi,
    obs.lo,
    obs.avg,
    (obs.avg - climo.avg) as temp_dfn,
    obs.total_p,
    (obs.total_p - climo.avg_p) as precip_dfn,
    april_obs.p as april_p,
    (april_obs.p - april_climo.avg_p) as april_p_dfn,
    april_obs.gdd as april_gdd,
    (april_obs.gdd - april_climo.avg_gdd) as april_gdd_dfn
    from obs JOIN climo on (obs.climate_site = climo.station)
    JOIN april_obs on (obs.station = april_obs.station)
    JOIN april_climo on (april_climo.station  = obs.climate_site)
""",
        (sts, ets, apr1, ets, sday, eday, eday),
    )
    data = {}
    for row in cursor:
        data[row["station"]] = row

    for district, sector in zip(DISTRICTS, STIDS):
        fp.write("%s District\n" % (district,))
        for sid in sector:
            nwsli = sid[-5:].strip()
            name = sid[:-5].strip()
            if nwsli not in data:
                print("Missing NWSLI: %s" % (nwsli,))
                continue
            fp.write(
                (
                    "%-15.15s %3.0f %3.0f %3.0f %3.0f  %5.2f  %5.2f   "
                    "%5.2f %6.2f %7.0f %5.0f\n"
                )
                % (
                    name,
                    data[nwsli]["hi"],
                    data[nwsli]["lo"],
                    data[nwsli]["avg"],
                    data[nwsli]["temp_dfn"],
                    data[nwsli]["total_p"],
                    data[nwsli]["precip_dfn"],
                    data[nwsli]["april_p"],
                    data[nwsli]["april_p_dfn"],
                    data[nwsli]["april_gdd"],
                    data[nwsli]["april_gdd_dfn"],
                )
            )


def compute_monthly(fp, year, month):
    """ Compute the monthly data we need to compute """
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Max daily high
    # min daily high
    # average temperature
    # departure from normal for average temp
    # Total precip
    # precip departure from normal
    # days with measurable precip
    # heating degree days
    # heating degree day departure
    # days with temp below 32
    # days with temp below 28
    sts = datetime.datetime(year, month, 1)
    ets = sts + datetime.timedelta(days=35)
    ets = ets.replace(day=1)

    cursor.execute(
        """
    WITH obs as (
        SELECT id as station, climate_site,
        max(max_tmpf) as hi,
        min(min_tmpf)  as lo,
        avg((max_tmpf+min_tmpf)/2.) as avg,
        sum(case when pday > 0 then pday else 0 end) as total_p,
        sum(case when pday > 0.009 then 1 else 0 end) as days,
        sum(hdd65(max_tmpf,min_tmpf)) as hdd,
        sum(case when min_tmpf <= 32 then 1 else 0 end) as days32,
        sum(case when min_tmpf <= 28 then 1 else 0 end) as days28
        FROM summary s JOIN stations t on (t.iemid = s.iemid)
        WHERE t.network = 'IA_COOP' and day >= %s and day < %s
        GROUP by station, climate_site
    ), climo as (
        SELECT station,
        avg((high+low)/2.) as avg,
        sum(precip) as avg_p,
        sum(hdd65) as avg_hdd
        from climate51 WHERE extract(month from valid) = %s
        GROUP by station
    )  SELECT obs.station,
    obs.hi,
    obs.lo,
    obs.avg,
    (obs.avg - climo.avg) as temp_dfn,
    obs.total_p,
    (obs.total_p - climo.avg_p) as precip_dfn,
    obs.days,
    obs.hdd,
    (obs.hdd - climo.avg_hdd) as hdd_dfn,
    obs.days32,
    obs.days28
    from obs JOIN climo on (obs.climate_site = climo.station)
""",
        (sts, ets, month),
    )
    data = {}
    for row in cursor:
        data[row["station"]] = row

    for district, sector in zip(DISTRICTS, STIDS):
        fp.write("%s District\n" % (district,))
        for sid in sector:
            nwsli = sid[-5:].strip()
            name = sid[:-5].strip()
            if data[nwsli]["hi"] is None:
                fp.write(
                    ("%-15.15s  --- No Observations Reported ---\n") % (name,)
                )
                continue
            fp.write(
                (
                    "%-15.15s %3.0f %3.0f %3.0f %3.0f  %5.2f  %5.2f   "
                    "%2s %5.0f %5.0f %3s  %3s\n"
                )
                % (
                    name,
                    data[nwsli]["hi"],
                    data[nwsli]["lo"],
                    data[nwsli]["avg"],
                    data[nwsli]["temp_dfn"],
                    data[nwsli]["total_p"],
                    data[nwsli]["precip_dfn"],
                    data[nwsli]["days"],
                    data[nwsli]["hdd"] or 0,
                    data[nwsli]["hdd_dfn"] or 0,
                    data[nwsli]["days32"],
                    data[nwsli]["days28"],
                )
            )


def monthly_header(fp, sts, ets):
    """ Write the monthly header information """
    fp.write(
        """Weather Summary For Iowa Agricultural Statistics Service
Prepared By Iowa Environmental Mesonet

For the Period:    %s
            To:    %s

                                                               DAYS DAYS
                      AIR                                       OF   OF
                  TEMPERATURE      PRECIPITATION     HDD   HDD  32   28
STATION          HI  LO AVG DFN  TOTAL    DFN DAYS   TOT   DFN COLD COLD
-------          --  --  --  --  -----   ----   --   ---   ---  --   --
"""
        % (sts.strftime("%A %B %d, %Y"), ets.strftime("%A %B %d, %Y"))
    )


def weekly_header(fp, sts, ets):
    """ Write the header information """
    fp.write(
        """Weather Summary For Iowa Agricultural Statistics Service
Prepared By Iowa Environmental Mesonet

For the Period:     %s
            To:     %s


                         CURRENT WEEK           SINCE APR 1    SINCE APR 1
                   TEMPERATURE  PRECIPITATION  PRECIPITATION  GDD BASE 50F
                   -----------  -------------  -------------  ------------
STATION          HI  LO AVG DFN  TOTAL    DFN   TOTAL    DFN   TOTAL   DFN
-------          --  --  --  --  -----   ----   -----   ----   -----  ----
"""
        % (sts.strftime("%A %B %d, %Y"), ets.strftime("%A %B %d, %Y"))
    )


def email_report(report, subject):
    """ Actually do the emailing stuff """
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = "akrherz@iastate.edu"
    msg["Cc"] = "akrherz@iastate.edu"
    msg["To"] = "akrherz@localhost"
    msg.preamble = "Report"

    fn = "iem.txt"

    b = MIMEBase("Text", "Plain")
    report.seek(0)
    b.set_payload(report.read())
    encoders.encode_base64(b)
    b.add_header("Content-Disposition", 'attachment; filename="%s"' % (fn))
    msg.attach(b)

    # Send the email via our own SMTP server.
    s = smtplib.SMTP("localhost")
    s.sendmail(msg["From"], [msg["To"], msg["Cc"]], msg.as_string())
    s.quit()


def main():
    """Go Main"""
    # If we are in Nov,Dec,Jan,Feb,Mar -> do monthly report
    # otherwise, do the weekly
    # This script is run each Monday or the first of the month
    # from RUN_2AM script
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    rtype = sys.argv[1]
    # We are testing things
    if len(sys.argv) >= 4:
        if rtype == "monthly":
            sts = datetime.date(int(sys.argv[2]), int(sys.argv[3]), 1)
            ets = sts + datetime.timedelta(days=35)
            ets = ets.replace(day=1)
            report = StringIO()
            monthly_header(report, sts, ets)
            compute_monthly(report, sts.year, sts.month)
            report.seek(0)
            print(report.read())
        if rtype == "weekly":
            sts = datetime.date(
                int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
            )
            ets = sts + datetime.timedelta(days=6)
            report = StringIO()
            weekly_header(report, sts, ets)
            compute_weekly(report, sts, ets)
            report.seek(0)
            print(report.read())
    else:
        if rtype == "monthly" and yesterday.month in (11, 12, 1, 2, 3):
            sts = yesterday.replace(day=1)
            ets = yesterday
            report = StringIO()
            monthly_header(report, sts, ets)
            compute_monthly(report, sts.year, sts.month)
            email_report(report, "IEM Monthly Data Report")
        if rtype == "weekly" and today.month in range(4, 11):
            sts = today - datetime.timedelta(days=7)
            ets = yesterday
            report = StringIO()
            weekly_header(report, sts, ets)
            compute_weekly(report, sts, ets)
            email_report(report, "IEM Weekly Data Report")


if __name__ == "__main__":
    main()
