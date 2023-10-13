"""
 Download interface for the data stored in coop database (alldata)

 This is called from /request/coop/fe.phtml
"""
import datetime
import zipfile
from io import BytesIO, StringIO

import pandas as pd
from metpy.units import units
from paste.request import parse_formvars
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconnc, get_sqlalchemy_conn, utc
from sqlalchemy import text

DEGC = units.degC
DEGF = units.degF
EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def f2c(val):
    """Convert F to C."""
    return (val * DEGF).to(DEGC).m


def get_scenario_period(ctx):
    """Compute the inclusive start and end dates to fetch scenario data for
    Arguments:
        ctx dictionary context this app was called with
    """
    sts = datetime.date(ctx["scenario_year"], ctx["ets"].month, ctx["ets"].day)
    ets = datetime.date(ctx["scenario_year"], 12, 31)
    return sts, ets


def sane_date(year, month, day):
    """Attempt to account for usage of days outside of the bounds for
    a given month"""
    # Calculate the last date of the given month
    nextmonth = datetime.date(year, month, 1) + datetime.timedelta(days=35)
    lastday = nextmonth.replace(day=1) - datetime.timedelta(days=1)
    return datetime.date(year, month, min(day, lastday.day))


def get_cgi_dates(form):
    """Figure out which dates are requested via the form, we shall attempt
    to account for invalid dates provided!"""
    today = datetime.date.today()
    y1 = int(form.get("year1", today.year))
    m1 = int(form.get("month1", 1))
    d1 = int(form.get("day1", 1))
    y2 = int(form.get("year2", today.year))
    m2 = int(form.get("month2", today.month))
    d2 = int(form.get("day2", today.day))

    ets = min(
        sane_date(y2, m2, d2),
        datetime.date.today() - datetime.timedelta(days=1),
    )

    return [sane_date(y1, m1, d1), ets]


def get_cgi_stations(form):
    """Figure out which stations the user wants, return a list of them"""
    reqlist = form.getall("station[]")
    if not reqlist:
        reqlist = form.getall("stations")
    if not reqlist:
        return []
    if "_ALL" in reqlist:
        network = form.get("network")
        nt = NetworkTable(network, only_online=False)
        return nt.sts.keys()

    return reqlist


def do_apsim(cursor, ctx):
    """
    [weather.met.weather]
    latitude = 42.1 (DECIMAL DEGREES)
    tav = 9.325084 (oC) ! annual average ambient temperature
    amp = 29.57153 (oC) ! annual amplitude in mean monthly temperature
    year          day           radn          maxt          mint          rain
    ()            ()            (MJ/m^2)      (oC)          (oC)          (mm)
     1986          1             7.38585       0.8938889    -7.295556      0
    """
    if len(ctx["stations"]) > 1:
        return (
            "ERROR: APSIM output is only "
            "permitted for one station at a time."
        ).encode("ascii")

    station = ctx["stations"][0]
    table = get_tablename(ctx["stations"])
    network = f"{station[:2]}CLIMATE"
    nt = NetworkTable(network, only_online=False)

    thisyear = datetime.datetime.now().year
    extra = {}
    if ctx["scenario"] == "yes":
        sts = datetime.datetime(int(ctx["scenario_year"]), 1, 1)
        ets = datetime.datetime(int(ctx["scenario_year"]), 12, 31)
        febtest = datetime.date(thisyear, 3, 1) - datetime.timedelta(days=1)
        sdaylimit = ""
        if febtest.day == 28:
            sdaylimit = " and sday != '0229'"
        cursor.execute(
            f"""
            SELECT day, high, low, precip, 1 as doy,
            coalesce(era5land_srad, narr_srad, merra_srad, hrrr_srad) as srad
            from {table} WHERE station = %s
            and day >= %s and day <= %s {sdaylimit}""",
            (ctx["stations"][0], sts, ets),
        )
        for row in cursor:
            ts = row["day"].replace(year=thisyear)
            extra[ts] = row
            extra[ts]["doy"] = int(ts.strftime("%j"))
        if febtest not in extra:
            feb28 = datetime.date(thisyear, 2, 28)
            extra[febtest] = extra[feb28]

    sio = StringIO()
    sio.write("! Iowa Environmental Mesonet -- NWS Cooperative Data\n")
    sio.write(f"! Created: {utc():%d %b %Y %H:%M:%S} UTC\n")
    sio.write("! Contact: daryl herzmann akrherz@iastate.edu 515-294-5978\n")
    sio.write(f"! Station: {station} {nt.sts[station]['name']}\n")
    sio.write(f"! Data Period: {ctx['sts']} - {ctx['ets']}\n")
    if ctx["scenario"] == "yes":
        sio.write(
            f"! !SCENARIO DATA! inserted after: {ctx['ets']} "
            f"replicating year: {ctx['scenario_year']}\n"
        )

    sio.write("[weather.met.weather]\n")
    sio.write(f"latitude = {nt.sts[station]['lat']:.1f} (DECIMAL DEGREES)\n")

    # Compute average temperature!
    cursor.execute(
        "SELECT avg((high+low)/2) as avgt from ncei_climate91 "
        "WHERE station = %s",
        (nt.sts[station]["ncei91"],),
    )
    row = cursor.fetchone()
    sio.write(
        f"tav = {f2c(row['avgt']):.3f} (oC) "
        "! annual average ambient temperature\n"
    )

    # Compute the annual amplitude in temperature
    cursor.execute(
        """
        select max(avg) as h, min(avg) as l from
            (SELECT extract(month from valid) as month, avg((high+low)/2.)
             from ncei_climate91
             WHERE station = %s GROUP by month) as foo
             """,
        (nt.sts[station]["ncei91"],),
    )
    row = cursor.fetchone()
    sio.write(
        ("amp = %.3f (oC) ! annual amplitude in mean monthly temperature\n")
        % (f2c(row["h"]) - f2c(row["l"]),)
    )

    sio.write(
        """year        day       radn       maxt       mint      rain
  ()         ()   (MJ/m^2)       (oC)       (oC)       (mm)\n"""
    )

    cursor.execute(
        """
        SELECT day, high, low, precip,
        extract(doy from day) as doy,
        coalesce(era5land_srad, narr_srad, merra_srad, hrrr_srad) as srad
        from alldata WHERE station = %s and
        day >= %s and day <= %s and high is not null and
        low is not null and precip is not null ORDER by day ASC
        """,
        (station, ctx["sts"], ctx["ets"]),
    )
    for row in cursor:
        srad = -99 if row["srad"] is None else row["srad"]
        sio.write(
            ("%4s %10.0f %10.3f %10.1f %10.1f %10.2f\n")
            % (
                row["day"].year,
                int(row["doy"]),
                srad,
                f2c(row["high"]),
                f2c(row["low"]),
                row["precip"] * 25.4,
            )
        )

    if extra:
        dec31 = datetime.date(thisyear, 12, 31)
        now = row["day"]
        while now <= dec31:
            row = extra[now]
            srad = -99 if row["srad"] is None else row["srad"]
            sio.write(
                ("%4s %10.0f %10.3f %10.1f %10.1f %10.2f\n")
                % (
                    now.year,
                    int(row["doy"]),
                    srad,
                    f2c(row["high"]),
                    f2c(row["low"]),
                    row["precip"] * 25.4,
                )
            )
            now += datetime.timedelta(days=1)
    return sio.getvalue().encode("ascii")


def do_century(cursor, ctx):
    """Materialize the data in Century Format
    * Century format  (precip cm, avg high C, avg low C)
    prec  1980   2.60   6.40   0.90   1.00   0.70   0.00
    tmin  1980  14.66  12.10   7.33  -0.89  -5.45  -7.29
    tmax  1980  33.24  30.50  27.00  18.37  11.35   9.90
    prec  1981  12.00   7.20   0.60   4.90   1.10   0.30
    tmin  1981  14.32  12.48   8.17   0.92  -3.25  -8.90
    tmax  1981  30.84  28.71  27.02  16.84  12.88   6.82
    """
    if len(ctx["stations"]) > 1:
        return (
            "ERROR: Century output is only "
            "permitted for one station at a time."
        ).encode("ascii")

    station = ctx["stations"][0]
    nt = NetworkTable(f"{station[:2]}CLIMATE", only_online=False)

    # Automatically set dates to start and end of year to make output clean
    sts = datetime.date(ctx["sts"].year, 1, 1)
    ets = datetime.date(ctx["ets"].year, 12, 31)
    if ets >= datetime.date.today():
        ets = datetime.date.today() - datetime.timedelta(days=1)

    table = get_tablename(ctx["stations"])
    thisyear = datetime.datetime.now().year
    cursor.execute(
        f"""
    WITH scenario as (
        SELECT {thisyear}::int as year, month, high, low, precip
        from {table}
        WHERE station = %s and day > %s and day <= %s and sday != '0229'
    ), obs as (
      select year, month, high, low, precip from {table}
      WHERE station = %s and day >= %s and day <= %s
    ), data as (
      SELECT * from obs UNION select * from scenario
    )

    SELECT year, month, avg(high) as tmax, avg(low) as tmin,
    sum(precip) as prec from data GROUP by year, month
    """,
        (station, ctx["scenario_sts"], ctx["scenario_ets"], station, sts, ets),
    )
    data = {}
    for row in cursor:
        if row["year"] not in data:
            data[row["year"]] = {}
            for mo in range(1, 13):
                data[row["year"]][mo] = {"prec": -99, "tmin": -99, "tmax": -99}

        data[row["year"]][row["month"]] = {
            "prec": (row["prec"] * units("inch")).to(units("mm")).m,
            "tmin": f2c(float(row["tmin"])),
            "tmax": f2c(float(row["tmax"])),
        }
    sio = StringIO()
    sio.write("# Iowa Environmental Mesonet -- NWS Cooperative Data\n")
    sio.write(f"# Created: {utc():%d %b %Y %H:%M:%S} UTC\n")
    sio.write("# Contact: daryl herzmann akrherz@iastate.edu 515-294-5978\n")
    sio.write("# Station: %s %s\n" % (station, nt.sts[station]["name"]))
    sio.write("# Data Period: %s - %s\n" % (sts, ets))
    if ctx["scenario"] == "yes":
        sio.write(
            "# !SCENARIO DATA! inserted after: %s replicating year: %s\n"
            % (ctx["ets"], ctx["scenario_year"])
        )
    idxs = ["prec", "tmin", "tmax"]
    for year in range(sts.year, ets.year + 1):
        for idx in idxs:
            sio.write(
                (
                    "%s  %s%7.2f%7.2f%7.2f%7.2f%7.2f%7.2f%7.2f"
                    "%7.2f%7.2f%7.2f%7.2f%7.2f\n"
                )
                % (
                    idx,
                    year,
                    data[year][1][idx],
                    data[year][2][idx],
                    data[year][3][idx],
                    data[year][4][idx],
                    data[year][5][idx],
                    data[year][6][idx],
                    data[year][7][idx],
                    data[year][8][idx],
                    data[year][9][idx],
                    data[year][10][idx],
                    data[year][11][idx],
                    data[year][12][idx],
                )
            )
    return sio.getvalue().encode("ascii")


def do_daycent(cursor, ctx):
    """Materialize data for daycent

    Daily Weather Data File (use extra weather drivers = 0):
    > 1 1 1990 1 7.040 -10.300 0.000

    NOTES:
    Column 1 - Day of month, 1-31
    Column 2 - Month of year, 1-12
    Column 3 - Year
    Column 4 - Day of the year, 1-366
    Column 5 - Maximum temperature for day, degrees C
    Column 6 - Minimum temperature for day, degrees C
    Column 7 - Precipitation for day, centimeters
    """
    if len(ctx["stations"]) > 1:
        return (
            "ERROR: Daycent output is only "
            "permitted for one station at a time."
        ).encode("ascii")

    table = get_tablename(ctx["stations"])

    extra = {}
    thisyear = datetime.datetime.now().year
    if ctx["scenario"] == "yes":
        sts = datetime.datetime(int(ctx["scenario_year"]), 1, 1)
        ets = datetime.datetime(int(ctx["scenario_year"]), 12, 31)
        febtest = datetime.date(thisyear, 3, 1) - datetime.timedelta(days=1)
        sdaylimit = ""
        if febtest.day == 28:
            sdaylimit = " and sday != '0229'"
        cursor.execute(
            f"""
            SELECT day, high, low, precip
            from {table} WHERE station = %s
            and day >= %s and day <= %s {sdaylimit}
            """,
            (ctx["stations"][0], sts, ets),
        )
        for row in cursor:
            ts = row["day"].replace(year=thisyear)
            extra[ts] = row
        if febtest not in extra:
            feb28 = datetime.date(thisyear, 2, 28)
            extra[febtest] = extra[feb28]
    cursor.execute(
        f"""
        SELECT day, high, low, precip,
        extract(doy from day) as doy
        from {table} WHERE station = %s
        and day >= %s and day <= %s ORDER by day ASC
    """,
        (ctx["stations"][0], ctx["sts"], ctx["ets"]),
    )
    sio = StringIO()
    sio.write("Daily Weather Data File (use extra weather drivers = 0):\n\n")
    for row in cursor:
        sio.write(
            ("%s %s %s %s %.2f %.2f %.2f\n")
            % (
                row["day"].day,
                row["day"].month,
                row["day"].year,
                int(row["doy"]),
                f2c(row["high"]),
                f2c(row["low"]),
                (row["precip"] * units("inch")).to(units("cm")).m,
            )
        )
    if extra:
        dec31 = datetime.date(thisyear, 12, 31)
        now = row["day"]
        while now <= dec31:
            row = extra[now]
            sio.write(
                ("%s %s %s %s %.2f %.2f %.2f\n")
                % (
                    now.day,
                    now.month,
                    now.year,
                    int(now.strftime("%j")),
                    f2c(row["high"]),
                    f2c(row["low"]),
                    (row["precip"] * units("inch")).to(units("cm")).m,
                )
            )
            now += datetime.timedelta(days=1)
    return sio.getvalue().encode("ascii")


def get_tablename(stations):
    """Figure out the table that has the data for these stations"""
    states = []
    for sid in stations:
        if sid[:2] not in states:
            states.append(sid[:2])
    if len(states) == 1:
        return "alldata_%s" % (states[0],)
    return "alldata"


def get_stationtable(stations):
    """Figure out our station table!"""
    states = []
    networks = []
    for sid in stations:
        if sid[:2] not in states:
            states.append(sid[:2])
            networks.append("%sCLIMATE" % (sid[:2],))
    return NetworkTable(networks, only_online=False)


def do_simple(cursor, ctx):
    """Generate Simple output"""

    table = get_tablename(ctx["stations"])

    nt = get_stationtable(ctx["stations"])
    thisyear = datetime.datetime.now().year
    if len(ctx["stations"]) == 1:
        ctx["stations"].append("X")

    limitrowcount = "LIMIT 1048000" if ctx["what"] == "excel" else ""
    sql = f"""
    WITH scenario as (
        SELECT station, high, low, precip, snow, snowd, narr_srad,
        era5land_srad, temp_estimated, precip_estimated,
        merra_srad, hrrr_srad,
        to_char(('{thisyear}-'||month||'-'||extract(day from day))::date,
        'YYYY/mm/dd') as day,
        extract(doy from day) as doy,
        gddxx(50, 86, high, low) as gdd_50_86,
        gddxx(40, 86, high, low) as gdd_40_86,
        round((5.0/9.0 * (high - 32.0))::numeric,1) as highc,
        round((5.0/9.0 * (low - 32.0))::numeric,1) as lowc,
        round((precip * 25.4)::numeric,1) as precipmm
        from {table} WHERE
        station IN {str(tuple(ctx["stations"]))} and
        day >= %s and day <= %s
    ), obs as (
        SELECT station, high, low, precip, snow, snowd, narr_srad,
        era5land_srad, temp_estimated, precip_estimated,
        merra_srad, hrrr_srad,
        to_char(day, 'YYYY/mm/dd') as day,
        extract(doy from day) as doy,
        gddxx(50, 86, high, low) as gdd_50_86,
        gddxx(40, 86, high, low) as gdd_40_86,
        round((5.0/9.0 * (high - 32.0))::numeric,1) as highc,
        round((5.0/9.0 * (low - 32.0))::numeric,1) as lowc,
        round((precip * 25.4)::numeric,1) as precipmm
        from {table} WHERE station IN {str(tuple(ctx["stations"]))} and
        day >= %s and day <= %s
    ), total as (
        SELECT * from obs UNION SELECT * from scenario
    )

    SELECT * from total ORDER by day ASC {limitrowcount}"""
    args = (ctx["scenario_sts"], ctx["scenario_ets"], ctx["sts"], ctx["ets"])

    cols = ["station", "station_name", "day", "doy"]
    if ctx["inclatlon"] == "yes":
        cols.insert(2, "lat")
        cols.insert(3, "lon")

    cols = cols + ctx["myvars"]

    if ctx["what"] == "excel":
        # Do the excel logic
        with get_sqlalchemy_conn("coop") as conn:
            df = pd.read_sql(sql, conn, params=args)
        # Convert day into a python date type
        df["day"] = pd.to_datetime(df["day"]).dt.date

        def _gs(x, y):
            return nt.sts[x][y]

        df["station_name"] = [_gs(x, "name") for x in df["station"]]
        if "lat" in cols:
            df["lat"] = [_gs(x, "lat") for x in df["station"]]
            df["lon"] = [_gs(x, "lon") for x in df["station"]]
        bio = BytesIO()
        df.to_excel(bio, columns=cols, index=False, engine="openpyxl")
        return bio.getvalue()

    cursor.execute(sql, args)
    sio = StringIO()
    if ctx["with_header"] != "no":
        sio.write("# Iowa Environmental Mesonet -- NWS Cooperative Data\n")
        sio.write(f"# Created: {utc():%d %b %Y %H:%M:%S} UTC\n")
        sio.write(
            "# Contact: daryl herzmann akrherz@iastate.edu 515-294-5978\n"
        )
        sio.write(f"# Data Period: {ctx['sts']} - {ctx['ets']}\n")
        if ctx["scenario"] == "yes":
            sio.write(
                "# !SCENARIO DATA! inserted after: %s replicating year: %s\n"
                % (ctx["ets"], ctx["scenario_year"])
            )

    p = {"comma": ",", "tab": "\t", "space": " "}
    d = p[ctx["delim"]]
    sio.write(d.join(cols) + "\r\n")

    for row in cursor:
        sid = row["station"]
        dc = row.copy()
        dc["station_name"] = nt.sts[sid]["name"]
        dc["lat"] = "%.4f" % (nt.sts[sid]["lat"],)
        dc["lon"] = "%.4f" % (nt.sts[sid]["lon"],)
        dc["doy"] = "%.0f" % (dc["doy"],)
        res = []
        for n in cols:
            res.append(str(dc[n]))
        sio.write((d.join(res)).replace("None", "M") + "\r\n")
    return sio.getvalue().encode("ascii")


def do_salus(cursor, ctx):
    """Generate SALUS
    StationID, Year, DOY, SRAD, Tmax, Tmin, Rain, DewP, Wind, Par, dbnum
    CTRL, 1981, 1, 5.62203, 2.79032, -3.53361, 5.43766, NaN, NaN, NaN, 2
    CTRL, 1981, 2, 3.1898, 1.59032, -6.83361, 1.38607, NaN, NaN, NaN, 3
    """
    if len(ctx["stations"]) > 1:
        return (
            "ERROR: SALUS output is only "
            "permitted for one station at a time."
        ).encode("ascii")

    scenario_year = 2030
    asts = datetime.date(2030, 1, 1)
    if ctx["scenario"] == "yes":
        # Tricky!
        scenario_year = ctx["scenario_year"]
        today = datetime.date.today()
        asts = datetime.date(scenario_year, today.month, today.day)

    table = get_tablename(ctx["stations"])
    station = ctx["stations"][0]
    thisyear = datetime.datetime.now().year
    cursor.execute(
        f"""
    WITH scenario as (
        SELECT
 ('{thisyear}-'||month||'-'||extract(day from day))::date
    as day,
        high, low, precip, station,
        coalesce(era5land_srad, narr_srad, merra_srad, hrrr_srad) as srad
        from {table} WHERE station = %s and
        day >= %s and year = %s
    ), obs as (
        SELECT day,
        high, low, precip,  station,
        coalesce(era5land_srad, narr_srad, merra_srad, hrrr_srad) as srad
        from {table} WHERE station = %s and
        day >= %s and day <= %s ORDER by day ASC
    ), total as (
        SELECT *, extract(doy from day) as doy from obs
        UNION SELECT *, extract(doy from day) as doy from scenario
    )

    SELECT * from total ORDER by day ASC
    """,
        (station, asts, scenario_year, station, ctx["sts"], ctx["ets"]),
    )
    sio = StringIO()
    sio.write(
        (
            "StationID, Year, DOY, SRAD, Tmax, Tmin, Rain, DewP, "
            "Wind, Par, dbnum\n"
        )
    )
    for i, row in enumerate(cursor):
        srad = -99 if row["srad"] is None else row["srad"]
        sio.write(
            ("%s, %s, %s, %.4f, %.2f, %.2f, %.2f, , , , %s\n")
            % (
                station[:4],
                row["day"].year,
                int(row["doy"]),
                srad,
                f2c(row["high"]),
                f2c(row["low"]),
                row["precip"] * 25.4,
                i + 2,
            )
        )
    return sio.getvalue().encode("ascii")


def do_dndc(cursor, ctx):
    """Process DNDC
    * One file per year! named StationName / StationName_YYYY.txt
    * julian day, tmax C , tmin C, precip cm seperated by space
    """

    table = get_tablename(ctx["stations"])

    nt = get_stationtable(ctx["stations"])

    if len(ctx["stations"]) == 1:
        ctx["stations"].append("X")

    scenario_year = 2030
    asts = datetime.date(2030, 1, 1)
    if ctx["scenario"] == "yes":
        # Tricky!
        scenario_year = ctx["scenario_year"]
        today = datetime.date.today()
        asts = datetime.date(scenario_year, today.month, today.day)

    thisyear = datetime.datetime.now().year
    cursor.execute(
        f"""
        WITH scenario as (
            SELECT
    ('{thisyear}-'||month||'-'||extract(day from day))::date as day,
            high, low, precip, station from {table}
            WHERE station = ANY(%s) and day >= %s and year = %s),
        obs as (
            SELECT day, high, low, precip, station from {table}
            WHERE station = ANY(%s) and day >= %s and day <= %s),
        total as (
            SELECT *, extract(doy from day) as doy from obs UNION
            SELECT *, extract(doy from day) as doy from scenario
        )
        SELECT * from total ORDER by day ASC
    """,
        (
            ctx["stations"],
            asts,
            scenario_year,
            ctx["stations"],
            ctx["sts"],
            ctx["ets"],
        ),
    )
    zipfiles = {}
    for row in cursor:
        station = row["station"]
        sname = nt.sts[station]["name"].replace(" ", "_")
        fn = f"{sname}/{sname}_{row['day'].year}.txt"
        if fn not in zipfiles:
            zipfiles[fn] = ""
        zipfiles[fn] += ("%s %.2f %.2f %.2f\n") % (
            int(row["doy"]),
            f2c(row["high"]),
            f2c(row["low"]),
            row["precip"] * 2.54,
        )

    sio = BytesIO()
    with zipfile.ZipFile(sio, "a") as zf:
        for fn, fp in zipfiles.items():
            zf.writestr(fn, fp)
    return sio.getvalue()


def do_swat(ctx):
    """SWAT

    Two files, one for precip [mm] and one for hi and low temperature [C]
    """
    table = get_tablename(ctx["stations"])

    if len(ctx["stations"]) == 1:
        ctx["stations"].append("X")

    scenario_year = 2030
    asts = datetime.date(2030, 1, 1)
    if ctx["scenario"] == "yes":
        # Tricky!
        scenario_year = ctx["scenario_year"]
        today = datetime.date.today()
        asts = datetime.date(scenario_year, today.month, today.day)

    thisyear = datetime.datetime.now().year
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                f"""
            WITH scenario as (
                SELECT
                ('{thisyear}-'||month||'-'||extract(day from day))::date as day,
                high, low, precip, station from {table}
                WHERE station = ANY(:sids) and
                day >= :asts and year = :scenario_year),
            obs as (
                SELECT day, high, low, precip, station from {table}
                WHERE station = ANY(:sids) and day >= :sts and day <= :ets),
            total as (
                SELECT *, extract(doy from day) as doy from obs UNION
                SELECT *, extract(doy from day) as doy from scenario
            )
            SELECT * from total ORDER by day ASC
        """
            ),
            conn,
            params={
                "sids": ctx["stations"],
                "asts": asts,
                "scenario_year": scenario_year,
                "sts": ctx["sts"],
                "ets": ctx["ets"],
            },
            index_col=None,
        )
    df["tmax"] = f2c(df["high"].values)
    df["tmin"] = f2c(df["low"].values)
    df["pcpn"] = (df["precip"].values * units("inch")).to(units("mm")).m
    zipfiles = {}
    for station, df2 in df.groupby(by="station"):
        pcpfn = f"swatfiles/{station}.pcp"
        tmpfn = f"swatfiles/{station}.tmp"
        zipfiles[pcpfn] = "IEM COOP %s\n\n\n\n" % (station,)
        zipfiles[tmpfn] = "IEM COOP %s\n\n\n\n" % (station,)
        for _i, row in df2.iterrows():
            zipfiles[pcpfn] += "%s%03i%5.1f\n" % (
                row["day"].year,
                row["doy"],
                row["pcpn"],
            )
            zipfiles[tmpfn] += ("%s%03i%5.1f%5.1f\n") % (
                row["day"].year,
                row["doy"],
                row["tmax"],
                row["tmin"],
            )
    sio = BytesIO()
    with zipfile.ZipFile(sio, "a") as zf:
        for fn, fp in zipfiles.items():
            zf.writestr(fn, fp)
    return sio.getvalue()


def application(environ, start_response):
    """go main go"""
    form = parse_formvars(environ)
    ctx = {}
    ctx["stations"] = get_cgi_stations(form)
    if not ctx["stations"]:
        start_response(
            "500 Internal Server Error", [("Content-type", "text/plain")]
        )
        return [b"No stations were specified for the request."]
    ctx["sts"], ctx["ets"] = get_cgi_dates(form)
    ctx["myvars"] = form.getall("vars[]")
    # Model specification trumps vars[]
    if form.get("model") is not None:
        ctx["myvars"] = [form.get("model")]
    ctx["what"] = form.get("what", "view")
    ctx["delim"] = form.get("delim", "comma")
    ctx["inclatlon"] = form.get("gis", "no")
    ctx["scenario"] = form.get("scenario", "no")
    ctx["scenario_year"] = 2099
    if ctx["scenario"] == "yes":
        ctx["scenario_year"] = int(form.get("scenario_year", 2099))
    ctx["scenario_sts"], ctx["scenario_ets"] = get_scenario_period(ctx)
    ctx["with_header"] = form.get("with_header", "yes")

    # TODO: this code stinks and is likely buggy
    headers = []
    if (
        "apsim" in ctx["myvars"]
        or "daycent" in ctx["myvars"]
        or "century" in ctx["myvars"]
        or "salus" in ctx["myvars"]
    ):
        headers.append(("Content-type", "text/plain"))
    elif "dndc" not in ctx["myvars"] and ctx["what"] != "excel":
        if ctx["what"] == "download":
            headers.append(("Content-type", "application/octet-stream"))
            dlfn = "changeme.txt"
            if len(ctx["stations"]) < 10:
                dlfn = f"{'_'.join(ctx['stations'])}.txt"
            headers.append(
                ("Content-Disposition", f"attachment; filename={dlfn}")
            )
        else:
            headers.append(("Content-type", "text/plain"))
    elif "dndc" in ctx["myvars"]:
        headers.append(("Content-type", "application/octet-stream"))
        headers.append(
            ("Content-Disposition", "attachment; filename=dndc.zip")
        )
    elif "swat" in ctx["myvars"]:
        headers.append(("Content-type", "application/octet-stream"))
        headers.append(
            ("Content-Disposition", "attachment; filename=swatfiles.zip")
        )
    elif ctx["what"] == "excel":
        headers.append(("Content-type", EXL))
        headers.append(
            ("Content-Disposition", "attachment; filename=nwscoop.xlsx")
        )

    conn, cursor = get_dbconnc("coop")
    start_response("200 OK", headers)
    # OK, now we fret
    if "daycent" in ctx["myvars"]:
        res = do_daycent(cursor, ctx)
    elif "century" in ctx["myvars"]:
        res = do_century(cursor, ctx)
    elif "apsim" in ctx["myvars"]:
        res = do_apsim(cursor, ctx)
    elif "dndc" in ctx["myvars"]:
        res = do_dndc(cursor, ctx)
    elif "salus" in ctx["myvars"]:
        res = do_salus(cursor, ctx)
    elif "swat" in ctx["myvars"]:
        res = do_swat(ctx)
    else:
        res = do_simple(cursor, ctx)
    conn.close()
    return [res]


def test_sane_date():
    """Test our sane_date() method"""
    assert sane_date(2000, 9, 31) == datetime.date(2000, 9, 30)
    assert sane_date(2000, 2, 31) == datetime.date(2000, 2, 29)
    assert sane_date(2000, 1, 15) == datetime.date(2000, 1, 15)
