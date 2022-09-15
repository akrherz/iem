"""Provide some CSV Files

first four columns need to be
ID,Station,Latitude,Longitude
"""
import datetime
import re
import sys

try:
    from zoneinfo import ZoneInfo  # type: ignore
except ImportError:
    from backports.zoneinfo import ZoneInfo  # type: ignore

# third party
import requests
import ephem
import pytz
import pandas as pd
from pandas.io.sql import read_sql
from paste.request import parse_formvars
from pyiem.util import get_dbconn, utc

# DOT plows
# RWIS sensor data
# River gauges
# Ag data (4" soil temps)
# Moon


def figurePhase(p1, p2):
    """Return a string of the moon phase!"""
    if p2 < p1:  # Waning!
        if p1 < 0.1:
            return "New Moon"
        if p1 < 0.4:
            return "Waning Crescent"
        if p1 < 0.6:
            return "Last Quarter"
        if p1 < 0.9:
            return "Waning Gibbous"
        return "Full Moon"

    if p1 < 0.1:
        return "New Moon"
    if p1 < 0.4:
        return "Waxing Crescent"
    if p1 < 0.6:
        return "First Quarter"
    if p1 < 0.9:
        return "Waxing Gibbous"
    return "Full Moon"


def do_moon(lon, lat):
    """Moon fun."""
    moon = ephem.Moon()
    obs = ephem.Observer()
    obs.lat = str(lat)
    obs.long = str(lon)
    obs.date = utc().strftime("%Y/%m/%d %H:%M")
    r1 = obs.next_rising(moon).datetime().replace(tzinfo=datetime.timezone.utc)
    p1 = moon.moon_phase
    obs.date = r1.strftime("%Y/%m/%d %H:%M")
    s1 = (
        obs.next_setting(moon).datetime().replace(tzinfo=datetime.timezone.utc)
    )
    # Figure out the next rise time
    obs.date = s1.strftime("%Y/%m/%d %H:%M")
    r2 = obs.next_rising(moon).datetime().replace(tzinfo=datetime.timezone.utc)
    p2 = moon.moon_phase
    obs.date = r2.strftime("%Y/%m/%d %H:%M")
    s2 = (
        obs.next_setting(moon).datetime().replace(tzinfo=datetime.timezone.utc)
    )
    label = figurePhase(p1, p2)
    # Figure out the timezone
    cursor = get_dbconn("mesosite").cursor()
    cursor.execute(
        "select tzid from tz_world WHERE "
        "st_contains(geom, st_setsrid(ST_Point(%s, %s), 4326))",
        (lon, lat),
    )
    if cursor.rowcount == 0:
        tzid = "UTC"
    else:
        tzid = cursor.fetchone()[0]
    tz = ZoneInfo(tzid)
    return pd.DataFrame(
        {
            "longitude": lon,
            "latitude": lat,
            "moon_rise_date": r1.astimezone(tz).strftime("%Y/%m/%d"),
            "moon_rise_time": r1.astimezone(tz).strftime("%-I:%M %P"),
            "moon_set_date": s1.astimezone(tz).strftime("%Y/%m/%d"),
            "moon_set_time": s1.astimezone(tz).strftime("%-I:%M %P"),
            "percent_illum_at_rise": round(p1 * 100, 4),
            "phase": label,
            "next_moon_rise_date": r2.astimezone(tz).strftime("%Y/%m/%d"),
            "next_moon_rise_time": r2.astimezone(tz).strftime("%-I:%M %P"),
            "next_moon_set_date": s2.astimezone(tz).strftime("%Y/%m/%d"),
            "next_moon_set_time": s2.astimezone(tz).strftime("%-I:%M %P"),
            "next_percent_illum_at_rise": round(p2 * 100, 4),
            "timezone": tzid,
        },
        index=[0],
    )


def do_iaroadcond():
    """Iowa DOT Road Conditions as dots"""
    pgconn = get_dbconn("postgis")
    df = read_sql(
        """
    select b.idot_id as locationid,
    replace(b.longname, ',', ' ') as locationname,
    ST_y(ST_transform(ST_centroid(b.geom),4326)) as latitude,
    ST_x(ST_transform(ST_centroid(b.geom),4326)) as longitude, cond_code
    from roads_base b JOIN roads_current c on (c.segid = b.segid)
    """,
        pgconn,
    )
    return df


def do_webcams(network):
    """direction arrows"""
    pgconn = get_dbconn("mesosite")
    df = read_sql(
        """
    select cam as locationid, w.name as locationname, st_y(geom) as latitude,
    st_x(geom) as longitude, drct
    from camera_current c JOIN webcams w on (c.cam = w.id)
    WHERE c.valid > (now() - '30 minutes'::interval) and w.network = %s
    """,
        pgconn,
        params=(network,),
    )
    return df


def do_iowa_azos(date, itoday=False):
    """Dump high and lows for Iowa ASOS"""
    pgconn = get_dbconn("iem")
    df = read_sql(
        f"""
    select id as locationid, n.name as locationname, st_y(geom) as latitude,
    st_x(geom) as longitude, s.day, s.max_tmpf::int as high,
    s.min_tmpf::int as low, coalesce(pday, 0) as precip
    from stations n JOIN summary_{date.year} s on (n.iemid = s.iemid)
    WHERE n.network = 'IA_ASOS' and s.day = %s
    """,
        pgconn,
        params=(date,),
        index_col="locationid",
    )
    if itoday:
        # Additionally, piggy back rainfall totals
        df2 = read_sql(
            """
        SELECT id as station,
        sum(phour) as precip720,
        sum(case when valid >= (now() - '168 hours'::interval)
            then phour else 0 end) as precip168,
        sum(case when valid >= (now() - '72 hours'::interval)
            then phour else 0 end) as precip72,
        sum(case when valid >= (now() - '48 hours'::interval)
            then phour else 0 end) as precip48,
        sum(case when valid >= (now() - '24 hours'::interval)
            then phour else 0 end) as precip24
        from hourly h JOIN stations t on (h.iemid = t.iemid)
        where t.network = 'IA_ASOS' and valid >= now() - '720 hours'::interval
        and phour > 0.005 GROUP by id
        """,
            pgconn,
            index_col="station",
        )
        for col in [
            "precip24",
            "precip48",
            "precip72",
            "precip168",
            "precip720",
        ]:
            df[col] = df2[col]
            # make sure the new column is >= precip
            df.loc[df[col] < df["precip"], col] = df["precip"]
    df = df.reset_index()
    return df


def do_iarwis():
    """Dump RWIS data"""
    pgconn = get_dbconn("iem")
    df = read_sql(
        """
    select id as locationid, n.name as locationname, st_y(geom) as latitude,
    st_x(geom) as longitude, tsf0 as pavetmp1, tsf1 as pavetmp2,
    tsf2 as pavetmp3, tsf3 as pavetmp4
    from stations n JOIN current s on (n.iemid = s.iemid)
    WHERE n.network in ('IA_RWIS', 'WI_RWIS', 'IL_RWIS') and
    s.valid > (now() - '2 hours'::interval)
    """,
        pgconn,
    )
    # Compute simple average in whole degree F
    df["paveavg"] = (
        df[["pavetmp1", "pavetmp2", "pavetmp3", "pavetmp4"]]
        .mean(axis=1)
        .map(lambda x: f"{x:.0f}" if not pd.isna(x) else "")
    )
    df = df[df["paveavg"] != ""]

    for col in range(1, 5):
        df[f"pavetmp{col}"] = df[f"pavetmp{col}"].map(
            lambda x: f"{x:.0f}" if not pd.isna(x) else ""
        )
    return df


def do_ahps_obs(nwsli):
    """Create a dataframe with AHPS river stage and CFS information"""
    pgconn = get_dbconn("hml")
    cursor = pgconn.cursor()
    # Get metadata
    cursor.execute(
        """
        SELECT name, st_x(geom), st_y(geom), tzname from stations
        where id = %s and network ~* 'DCP'
    """,
        (nwsli,),
    )
    row = cursor.fetchone()
    latitude = row[2]
    longitude = row[1]
    stationname = row[0]
    tzinfo = pytz.timezone(row[3])
    # Figure out which keys we have
    cursor.execute(
        """
    with obs as (
        select distinct key from hml_observed_data where station = %s
        and valid > now() - '3 days'::interval)
    SELECT k.id, k.label from hml_observed_keys k JOIN obs o on (k.id = o.key)
    """,
        (nwsli,),
    )
    if cursor.rowcount == 0:
        return "NO DATA"
    plabel = cursor.fetchone()[1]
    slabel = cursor.fetchone()[1]
    df = read_sql(
        """
    WITH primaryv as (
      SELECT valid, value from hml_observed_data WHERE station = %s
      and key = get_hml_observed_key(%s) and valid > now() - '1 day'::interval
    ), secondaryv as (
      SELECT valid, value from hml_observed_data WHERE station = %s
      and key = get_hml_observed_key(%s) and valid > now() - '1 day'::interval
    )
    SELECT p.valid at time zone 'UTC' as valid,
    p.value as primary_value, s.value as secondary_value,
    'O' as type
    from primaryv p LEFT JOIN secondaryv s ON (p.valid = s.valid)
    WHERE p.valid > (now() - '72 hours'::interval)
    ORDER by p.valid DESC
    """,
        pgconn,
        params=(nwsli, plabel, nwsli, slabel),
        index_col=None,
    )
    sys.stderr.write(str(plabel))
    sys.stderr.write(str(slabel))
    df["locationid"] = nwsli
    df["locationname"] = stationname
    df["latitude"] = latitude
    df["longitude"] = longitude
    df["Time"] = (
        df["valid"]
        .dt.tz_localize(pytz.UTC)
        .dt.tz_convert(tzinfo)
        .dt.strftime("%m/%d/%Y %H:%M")
    )
    df[plabel] = df["primary_value"]
    df[slabel] = df["secondary_value"]
    # we have to do the writing from here
    res = "Observed Data:,,\n"
    res += "|Date|,|Stage|,|--Flow-|\n"
    odf = df[df["type"] == "O"]
    for _, row in odf.iterrows():
        res += (
            f"{row['Time']},{row['Stage[ft]']:.2f}ft,"
            f"{row['Flow[kcfs]']:.1f}kcfs\n"
        )
    return res


def do_ahps_fx(nwsli):
    """Create a dataframe with AHPS river stage and CFS information"""
    pgconn = get_dbconn("hml")
    cursor = pgconn.cursor()
    # Get metadata
    cursor.execute(
        "SELECT name, st_x(geom), st_y(geom), tzname from stations "
        "where id = %s and network ~* 'DCP'",
        (nwsli,),
    )
    row = cursor.fetchone()
    latitude = row[2]
    longitude = row[1]
    stationname = row[0]
    tzinfo = pytz.timezone(row[3])
    # Get the last forecast
    cursor.execute(
        """
        select id, forecast_sts at time zone 'UTC',
        generationtime at time zone 'UTC', primaryname, primaryunits,
        secondaryname, secondaryunits
        from hml_forecast where station = %s
        and generationtime > now() - '7 days'::interval
        ORDER by issued DESC LIMIT 1
    """,
        (nwsli,),
    )
    row = cursor.fetchone()
    primaryname = row[3]
    generationtime = row[2]
    primaryunits = row[4]
    secondaryname = row[5]
    secondaryunits = row[6]
    # Get the latest forecast
    df = read_sql(
        f"""
    SELECT valid at time zone 'UTC' as valid,
    primary_value, secondary_value, 'F' as type from
    hml_forecast_data_{generationtime.year} WHERE hml_forecast_id = %s
    ORDER by valid ASC
    """,
        pgconn,
        params=(row[0],),
        index_col=None,
    )
    # Get the obs
    plabel = f"{primaryname}[{primaryunits}]"
    slabel = f"{secondaryname}[{secondaryunits}]"

    df["locationid"] = nwsli
    df["locationname"] = stationname
    df["latitude"] = latitude
    df["longitude"] = longitude
    df["Time"] = (
        df["valid"]
        .dt.tz_localize(pytz.UTC)
        .dt.tz_convert(tzinfo)
        .dt.strftime("%m/%d/%Y %H:%M")
    )
    df[plabel] = df["primary_value"]
    df[slabel] = df["secondary_value"]
    # we have to do the writing from here
    res = f"Forecast Data (Issued {generationtime:%m-%d-%Y %H:%M:%S} UTC):,\n"
    res += "|Date|,|Stage|,|--Flow-|\n"
    odf = df[df["type"] == "F"]
    for _, row in odf.iterrows():
        res += (
            f"{row['Time']},{row['Stage[ft]']:.2f}ft,"
            f"{row['Fow[kcfs']:.1f}kcfs\n"
        )
    return res


def feet(val, suffix="'"):
    """Make feet indicator"""
    if pd.isnull(val) or val == "":
        return ""
    return f"{val:.1f}{suffix}"


def do_ahps(nwsli):
    """Create a dataframe with AHPS river stage and CFS information"""
    pgconn = get_dbconn("hml")
    cursor = pgconn.cursor()
    # Get metadata
    cursor.execute(
        "SELECT name, st_x(geom), st_y(geom), tzname from stations "
        "where id = %s and network ~* 'DCP'",
        (nwsli,),
    )
    row = cursor.fetchone()
    latitude = row[2]
    longitude = row[1]
    stationname = row[0].replace(",", " ")
    tzinfo = pytz.timezone(row[3])
    # Get the last forecast
    cursor.execute(
        """
        select id, forecast_sts at time zone 'UTC',
        generationtime at time zone 'UTC', primaryname, primaryunits,
        secondaryname, secondaryunits
        from hml_forecast where station = %s
        and generationtime > now() - '7 days'::interval
        ORDER by issued DESC LIMIT 1
    """,
        (nwsli,),
    )
    if cursor.rowcount == 0:
        return "NO DATA"
    row = cursor.fetchone()
    generationtime = row[2]
    y = f"{generationtime.year}"
    # Figure out which keys we have
    cursor.execute(
        """
    with obs as (
        select distinct key from hml_observed_data where station = %s
        and valid > now() - '3 days'::interval)
    SELECT k.id, k.label from hml_observed_keys k JOIN obs o on (k.id = o.key)
    """,
        (nwsli,),
    )
    if cursor.rowcount == 0:
        return "NO DATA"
    lookupkey = 14
    for _row in cursor:
        if _row[1].find("[ft]") > 0:
            lookupkey = _row[0]
            break

    # get observations
    odf = read_sql(
        """
    SELECT valid at time zone 'UTC' as valid,
    value from hml_observed_data WHERE station = %s
    and key = %s and valid > now() - '3 day'::interval
    and extract(minute from valid) = 0
    ORDER by valid DESC
    """,
        pgconn,
        params=(nwsli, lookupkey),
        index_col=None,
    )
    # hoop jumping to get a timestamp in the local time of this sensor
    # see akrherz/iem#187
    odf["obtime"] = (
        odf["valid"]
        .dt.tz_localize(pytz.UTC)
        .dt.tz_convert(tzinfo)
        .dt.strftime("%a. %-I %p")
    )
    # Get the latest forecast
    df = read_sql(
        f"""
        SELECT valid at time zone 'UTC' as valid,
        primary_value, secondary_value, 'F' as type from
        hml_forecast_data_{y} WHERE hml_forecast_id = %s
        ORDER by valid ASC
    """,
        pgconn,
        params=(row[0],),
        index_col=None,
    )
    # Get the obs
    # plabel = "{}[{}]".format(primaryname, primaryunits)
    # slabel = "{}[{}]".format(secondaryname, secondaryunits)
    odf = odf.rename(columns={"value": "obstage"})
    df = df.join(odf[["obtime", "obstage"]], how="outer")
    # hoop jumping to get a timestamp in the local time of this sensor
    # see akrherz/iem#187
    df["forecasttime"] = (
        df["valid"]
        .dt.tz_localize(pytz.UTC)
        .dt.tz_convert(tzinfo)
        .dt.strftime("%a. %-I %p")
    )
    df["forecaststage"] = df["primary_value"]
    # df[slabel] = df['secondary_value']
    # we have to do the writing from here
    res = (
        "locationid,locationname,latitude,longitude,obtime,obstage,"
        "obstage2,obstagetext,forecasttime,forecaststage,forecaststage1,"
        "forecaststage2,forecaststage3,highestvalue,highestvalue2,"
        "highestvaluedate\n"
    )
    res += ",,,,,,,,,,,,,,,\n,,,,,,,,,,,,,,,\n"

    maxrow = df.sort_values("forecaststage", ascending=False).iloc[0]
    for idx, row in df.iterrows():
        fs = (
            row["forecaststage"] if not pd.isnull(row["forecaststage"]) else ""
        )
        res += ("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n") % (
            nwsli if idx == 0 else "",
            stationname if idx == 0 else "",
            latitude if idx == 0 else "",
            longitude if idx == 0 else "",
            row["obtime"],
            row["obstage"],
            feet(row["obstage"]),
            "Unknown" if idx == 0 else "",
            (row["forecasttime"] if row["forecasttime"] != "NaT" else ""),
            feet(row["forecaststage"], "ft"),
            fs,
            feet(row["forecaststage"]),
            fs,
            "" if idx > 0 else maxrow["forecaststage"],
            "" if idx > 0 else feet(maxrow["forecaststage"]),
            "" if idx > 0 else maxrow["forecasttime"],
        )

    return res


def do_uvi():
    """UVI index."""
    PATTERN = re.compile(
        r"(?P<c1>[A-Z\s]+)\s+(?P<s1>[A-Z][A-Z])\s+(?P<u1>\d+)\s+"
        r"(?P<c2>[A-Z\s]+)\s+(?P<s2>[A-Z][A-Z])\s+(?P<u2>\d+)",
    )
    URL = (
        "https://www.cpc.ncep.noaa.gov/"
        "products/stratosphere/uv_index/bulletin.txt"
    )
    req = requests.get(URL, timeout=20)
    rows = []
    for line in req.content.decode("ascii").split("\n"):
        m = PATTERN.match(line)
        if not m:
            continue
        data = m.groupdict()
        for i in ["1", "2"]:
            rows.append(
                {
                    "City": data[f"c{i}"].strip(),
                    "State": data[f"s{i}"].strip(),
                    "UVI": data[f"u{i}"].strip(),
                }
            )
    return pd.DataFrame(rows)


def router(appname):
    """Process and return dataframe"""
    if appname.startswith("ahpsobs_"):
        df = do_ahps_obs(appname[8:].upper())  # we write ourselves and exit
    elif appname.startswith("ahpsfx_"):
        df = do_ahps_fx(appname[7:].upper())  # we write ourselves and exit
    elif appname.startswith("ahps_"):
        df = do_ahps(appname[5:].upper())  # we write ourselves and exit
    elif appname == "iaroadcond":
        df = do_iaroadcond()
    elif appname == "iarwis":
        df = do_iarwis()
    elif appname == "iowayesterday":
        df = do_iowa_azos(datetime.date.today() - datetime.timedelta(days=1))
    elif appname == "iowatoday":
        df = do_iowa_azos(datetime.date.today(), True)
    elif appname == "kcrgcitycam":
        df = do_webcams("KCRG")
    elif appname == "uvi":
        df = do_uvi()
    elif appname.startswith("moon"):
        tokens = appname.replace(".txt", "").split("_")
        df = do_moon(float(tokens[1]), float(tokens[2]))
    else:
        df = "ERROR, unknown report specified"
    return df


def application(environ, start_response):
    """Do Something"""
    form = parse_formvars(environ)
    appname = form.get("q")
    res = router(appname)
    start_response("200 OK", [("Content-type", "text/plain")])
    if isinstance(res, pd.DataFrame):
        return [res.to_csv(None, index=False).encode("ascii")]
    return [res.encode("ascii")]


def test_hml():
    """Can we do it?"""
    do_ahps("DBQI4")
