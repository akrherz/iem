""".. title:: IEM Climodat Data Export

Return to `API Services </api/#cgi>`_.  This service is the backend for the
`Climodat Download </request/coop/fe.phtml>`_ frontend.

Documentation for /cgi-bin/request/coop.py
------------------------------------------

This service is somewhat poorly named ``coop.py``, but is providing the IEM
Climodat data, which is a combination of NWS COOP and NWS ASOS/AWOS data. There
are a number of knobs here as this is one of the most popular datasets the IEM
produces.

Changelog
---------

- 2024-06-22: Initital documentation and backend conversion to pydantic.

"""

from datetime import date, datetime, timedelta
from io import BytesIO, StringIO
from zipfile import ZipFile

import pandas as pd
from metpy.units import units
from pydantic import Field
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.network import Table as NetworkTable
from pyiem.reference import state_names
from pyiem.util import utc
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy import text

DEGF = units.degF
DEGC = units.degC

DEGC = units.degC
DEGF = units.degF
EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class Schema(CGIModel):
    """See how we are called."""

    delim: str = Field(
        "comma",
        description=(
            "The delimiter to use in the output file.  "
            "Options: comma, tab, space"
        ),
    )
    gis: bool = Field(
        False,
        description="Include latitude and longitude columns in the output.",
    )
    inclatlon: bool = Field(
        False,
        description="Include latitude and longitude columns in the output.",
    )
    model: str = Field(
        None,
        description=(
            "The model to use for output.  Options: simple, apsim, "
            "century, daycent, salus, dndc, swat.  Specifying this will "
            "override the 'vars' option."
        ),
    )
    network: str = Field(
        "IACLIMATE", description="The network to use for station lookups."
    )
    scenario: bool = Field(
        False,
        description=(
            "Should data from a previous year, specified by scenario_year "
            "be used to fill out the present year."
        ),
    )
    scenario_year: int = Field(
        2020,
        description=(
            "The year to use as a scenario year, if scenario is true."
        ),
    )
    station: ListOrCSVType = Field(
        [], description="List of stations to include in the output."
    )
    stations: ListOrCSVType = Field(
        [],
        description=(
            "List of stations to include in the output. Legacy variable name."
        ),
    )
    vars: ListOrCSVType = Field(
        [], description="List of variables to include in the output."
    )
    what: str = Field("view", description="The type of output to generate.")
    with_header: bool = Field(
        True, description="Include a header row in the output."
    )
    year1: int = Field(
        date.today().year,
        description="The starting year for the data request.",
    )
    month1: int = Field(
        1,
        description="The starting month for the data request.",
    )
    day1: int = Field(
        1,
        description="The starting day for the data request.",
    )
    year2: int = Field(
        date.today().year,
        description="The ending year for the data request.",
    )
    month2: int = Field(
        date.today().month,
        description="The ending month for the data request.",
    )
    day2: int = Field(
        date.today().day,
        description="The ending day for the data request.",
    )


def get_scenario_period(ctx):
    """Compute the inclusive start and end dates to fetch scenario data for
    Arguments:
        ctx dictionary context this app was called with
    """
    if ctx["ets"].month == 2 and ctx["ets"].day == 29:
        sts = date(ctx["scenario_year"], ctx["ets"].month, 28)
    else:
        sts = date(ctx["scenario_year"], ctx["ets"].month, ctx["ets"].day)
    ets = date(ctx["scenario_year"], 12, 31)
    return sts, ets


def sane_date(year, month, day):
    """Attempt to account for usage of days outside of the bounds for
    a given month"""
    # Calculate the last date of the given month
    nextmonth = date(year, month, 1) + timedelta(days=35)
    lastday = nextmonth.replace(day=1) - timedelta(days=1)
    return date(year, month, min(day, lastday.day))


def get_cgi_dates(environ):
    """Figure out which dates are requested via the form, we shall attempt
    to account for invalid dates provided!"""

    ets = min(
        sane_date(environ["year2"], environ["month2"], environ["day2"]),
        date.today() - timedelta(days=1),
    )

    return [
        sane_date(environ["year1"], environ["month1"], environ["day1"]),
        ets,
    ]


def get_cgi_stations(environ):
    """Figure out which stations the user wants, return a list of them"""
    reqlist = environ["station"]
    if not reqlist:
        reqlist = environ["stations"]
    if not reqlist:
        return []
    if "_ALL" in reqlist:
        network = environ["network"]
        nt = NetworkTable(network, only_online=False)
        return list(nt.sts.keys())

    return reqlist


def f2c(val):
    """Convert F to C."""
    return (val * DEGF).to(DEGC).m


def get_tablename(stations):
    """Figure out the table that has the data for these stations"""
    states = []
    for sid in stations:
        if sid[:2] not in states and sid[:2].lower() in state_names:
            states.append(sid[:2])
    if len(states) == 1:
        return f"alldata_{states[0]}"
    return "alldata"


def get_stationtable(stations):
    """Figure out our station table!"""
    states = []
    networks = []
    for sid in stations:
        if sid[:2] not in states:
            states.append(sid[:2])
            networks.append(f"{sid[:2]}CLIMATE")
    return NetworkTable(networks, only_online=False)


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
    network = f"{station[:2]}CLIMATE"
    nt = NetworkTable(network, only_online=False)
    if station not in nt.sts:
        raise IncompleteWebRequest("Unknown station provided")

    thisyear = ctx["ets"].year
    extra = {}
    if ctx["scenario"]:
        sts = datetime(int(ctx["scenario_year"]), 1, 1)
        ets = datetime(int(ctx["scenario_year"]), 12, 31)
        febtest = date(thisyear, 3, 1) - timedelta(days=1)
        sdaylimit = ""
        if febtest.day == 28:
            sdaylimit = " and sday != '0229'"
        cursor.execute(
            f"""
            SELECT day, high, low, precip, 1 as doy,
            coalesce(era5land_srad, narr_srad, merra_srad, hrrr_srad) as srad
            from alldata WHERE station = %s
            and day >= %s and day <= %s {sdaylimit}""",
            (ctx["stations"][0], sts, ets),
        )
        for row in cursor:
            ts = row["day"].replace(year=thisyear)
            extra[ts] = row
            extra[ts]["doy"] = int(ts.strftime("%j"))
        if febtest not in extra:
            feb28 = date(thisyear, 2, 28)
            if feb28 in extra:
                extra[febtest] = extra[feb28]

    sio = StringIO()
    sio.write("! Iowa Environmental Mesonet -- NWS Cooperative Data\n")
    sio.write(f"! Created: {utc():%d %b %Y %H:%M:%S} UTC\n")
    sio.write("! Contact: daryl herzmann akrherz@iastate.edu 515-294-5978\n")
    sio.write(f"! Station: {station} {nt.sts[station]['name']}\n")
    sio.write(f"! Data Period: {ctx['sts']} - {ctx['ets']}\n")
    if ctx["scenario"]:
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
        f"tav = {f2c(-99 if row['avgt'] is None else row['avgt']):.3f} (oC) "
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
    if row["h"] is not None:
        sio.write(
            f"amp = {f2c(row['h']) - f2c(row['l']):.3f} (oC) ! "
            "annual amplitude in mean monthly temperature\n"
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
    lastday = ctx["sts"]
    for row in cursor:
        lastday = row["day"]
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
        dec31 = date(lastday.year, 12, 31)
        now = lastday + timedelta(days=1)
        while now <= dec31:
            row = extra.get(now)
            if row is None:
                raise IncompleteWebRequest("Missing data for scenario year!")
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
            now += timedelta(days=1)
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
    sts = date(ctx["sts"].year, 1, 1)
    ets = date(ctx["ets"].year, 12, 31)
    if ets >= date.today():
        ets = date.today() - timedelta(days=1)

    thisyear = datetime.now().year
    cursor.execute(
        f"""
    WITH scenario as (
        SELECT {thisyear}::int as year, month, high, low, precip
        from alldata
        WHERE station = %s and day > %s and day <= %s and sday != '0229'
    ), obs as (
      select year, month, high, low, precip from alldata
      WHERE station = %s and day >= %s and day <= %s
    ), data as (
      SELECT * from obs UNION select * from scenario
    )

    SELECT year, month, avg(high) as tmax, avg(low) as tmin,
    sum(precip) as prec from data where high is not null and low is not null
    and precip is not null GROUP by year, month
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
    if ctx["scenario"]:
        sio.write(
            "# !SCENARIO DATA! inserted after: %s replicating year: %s\n"
            % (ctx["ets"], ctx["scenario_year"])
        )
    idxs = ["prec", "tmin", "tmax"]
    for year in range(sts.year, ets.year + 1):
        if year not in data:
            continue
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

    extra = {}
    thisyear = ctx["ets"].year
    if ctx["scenario"]:
        sts = datetime(int(ctx["scenario_year"]), 1, 1)
        ets = datetime(int(ctx["scenario_year"]), 12, 31)
        febtest = date(thisyear, 3, 1) - timedelta(days=1)
        sdaylimit = ""
        if febtest.day == 28:
            sdaylimit = " and sday != '0229'"
        cursor.execute(
            f"""
            SELECT day, high, low, precip
            from alldata WHERE station = %s
            and day >= %s and day <= %s {sdaylimit}
            """,
            (ctx["stations"][0], sts, ets),
        )
        for row in cursor:
            ts = row["day"].replace(year=thisyear)
            extra[ts] = row
        if febtest not in extra:
            feb28 = date(thisyear, 2, 28)
            if feb28 in extra:
                extra[febtest] = extra[feb28]
    cursor.execute(
        """
        SELECT day, high, low, precip,
        extract(doy from day) as doy
        from alldata WHERE station = %s
        and day >= %s and day <= %s ORDER by day ASC
    """,
        (ctx["stations"][0], ctx["sts"], ctx["ets"]),
    )
    sio = StringIO()
    sio.write("Daily Weather Data File (use extra weather drivers = 0):\n\n")
    lastday = ctx["sts"]
    for row in cursor:
        lastday = row["day"]
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
        dec31 = date(lastday.year, 12, 31)
        now = lastday + timedelta(days=1)
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
            now += timedelta(days=1)
    return sio.getvalue().encode("ascii")


def do_simple(cursor, ctx):
    """Generate Simple output"""

    table = get_tablename(ctx["stations"])

    nt = get_stationtable(ctx["stations"])
    thisyear = ctx["ets"].year

    limitrowcount = "LIMIT 1048000" if ctx["what"] == "excel" else ""
    sql = f"""
    WITH scenario as (
        SELECT station, high, low, precip, snow, snowd, narr_srad,
        era5land_srad, temp_estimated, precip_estimated, power_srad,
        era5land_soilt4_avg, era5land_soilm4_avg, era5land_soilm1m_avg,
        nldas_soilt4_avg, nldas_soilm4_avg, nldas_soilm1m_avg,
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
        station = ANY(%s) and
        day >= %s and day <= %s
    ), obs as (
        SELECT station, high, low, precip, snow, snowd, narr_srad,
        era5land_srad, temp_estimated, precip_estimated, power_srad,
        era5land_soilt4_avg, era5land_soilm4_avg, era5land_soilm1m_avg,
        nldas_soilt4_avg, nldas_soilm4_avg, nldas_soilm1m_avg,
        merra_srad, hrrr_srad,
        to_char(day, 'YYYY/mm/dd') as day,
        extract(doy from day) as doy,
        gddxx(50, 86, high, low) as gdd_50_86,
        gddxx(40, 86, high, low) as gdd_40_86,
        round((5.0/9.0 * (high - 32.0))::numeric,1) as highc,
        round((5.0/9.0 * (low - 32.0))::numeric,1) as lowc,
        round((precip * 25.4)::numeric,1) as precipmm
        from {table} WHERE station = ANY(%s) and
        day >= %s and day <= %s
    ), total as (
        SELECT * from obs UNION SELECT * from scenario
    )

    SELECT * from total ORDER by day ASC {limitrowcount}"""
    args = (
        ctx["stations"],
        ctx["scenario_sts"],
        ctx["scenario_ets"],
        ctx["stations"],
        ctx["sts"],
        ctx["ets"],
    )

    cols = ["station", "station_name", "day", "doy"]
    if ctx["inclatlon"]:
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
    if ctx["with_header"]:
        sio.write("# Iowa Environmental Mesonet -- NWS Cooperative Data\n")
        sio.write(f"# Created: {utc():%d %b %Y %H:%M:%S} UTC\n")
        sio.write(
            "# Contact: daryl herzmann akrherz@iastate.edu 515-294-5978\n"
        )
        sio.write(f"# Data Period: {ctx['sts']} - {ctx['ets']}\n")
        if ctx["scenario"]:
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
        res = [str(dc[n]) for n in cols]
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
    asts = date(2030, 1, 1)
    if ctx["scenario"]:
        # Tricky!
        scenario_year = ctx["scenario_year"]
        today = date.today()
        asts = date(scenario_year, today.month, today.day)

    table = get_tablename(ctx["stations"])
    station = ctx["stations"][0]
    thisyear = datetime.now().year
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

    scenario_year = 2030
    asts = date(2030, 1, 1)
    if ctx["scenario"]:
        # Tricky!
        scenario_year = ctx["scenario_year"]
        today = date.today()
        asts = date(scenario_year, today.month, today.day)

    thisyear = datetime.now().year
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
    with ZipFile(sio, "a") as zf:
        for fn, fp in zipfiles.items():
            zf.writestr(fn, fp)
    return sio.getvalue()


def do_swat(_cursor, ctx):
    """SWAT

    Two files, one for precip [mm] and one for hi and low temperature [C]
    """
    table = get_tablename(ctx["stations"])

    scenario_year = 2030
    asts = date(2030, 1, 1)
    if ctx["scenario"]:
        # Tricky!
        scenario_year = ctx["scenario_year"]
        today = date.today()
        asts = date(scenario_year, today.month, today.day)

    thisyear = datetime.now().year
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                f"""
            WITH scenario as (
                SELECT
                ('{thisyear}-'||month||'-'||extract(day from day))::date
                    as day, high, low, precip, station from {table}
                WHERE station = ANY(:sids) and
                day >= :asts and year = :scenario_year and
                high is not null and low is not null),
            obs as (
                SELECT day, high, low, precip, station from {table}
                WHERE station = ANY(:sids) and day >= :sts and day <= :ets
                and high is not null and low is not null),
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
    with ZipFile(sio, "a") as zf:
        for fn, fp in zipfiles.items():
            zf.writestr(fn, fp)
    return sio.getvalue()


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """go main go"""
    ctx = {}
    ctx["stations"] = get_cgi_stations(environ)
    if not ctx["stations"]:
        raise IncompleteWebRequest("No stations were specified.")
    ctx["sts"], ctx["ets"] = get_cgi_dates(environ)
    ctx["myvars"] = environ["vars"]
    # Model specification trumps vars[]
    if environ["model"] is not None:
        ctx["myvars"] = [environ["model"]]
    ctx["what"] = environ["what"]
    ctx["delim"] = environ["delim"]
    ctx["inclatlon"] = environ["gis"]
    ctx["scenario"] = environ["scenario"]
    ctx["scenario_year"] = 2099
    if ctx["scenario"]:
        ctx["scenario_year"] = environ["scenario_year"]
    ctx["scenario_sts"], ctx["scenario_ets"] = get_scenario_period(ctx)
    ctx["with_header"] = environ["with_header"]

    # TODO: this code stinks and is likely buggy
    headers = []
    if (
        "apsim" in ctx["myvars"]
        or "daycent" in ctx["myvars"]
        or "century" in ctx["myvars"]
        or "salus" in ctx["myvars"]
    ):
        if ctx["what"] == "download":
            headers.append(("Content-type", "application/octet-stream"))
            headers.append(
                ("Content-Disposition", "attachment; filename=metdata.txt")
            )
        else:
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
        res = do_swat(None, ctx)
    else:
        res = do_simple(cursor, ctx)
    cursor.close()
    conn.close()
    return [res]
