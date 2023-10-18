"""Provide some CSV Files

first four columns need to be
ID,Station,Latitude,Longitude
"""
import datetime
import re
from zoneinfo import ZoneInfo

# third party
import ephem
import numpy as np
import pandas as pd
import requests
from pyiem.util import get_dbconnc, get_sqlalchemy_conn, utc
from pyiem.webutil import iemapp
from sqlalchemy import text

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


def do_moonphase(lon, lat):
    """Get the next four phases of the moon."""
    obs = ephem.Observer()
    obs.lat = str(lat)
    obs.long = str(lon)
    obs.date = utc().strftime("%Y/%m/%d %H:%M")
    series = pd.Series(
        {
            "new_moon": ephem.next_new_moon(utc())
            .datetime()
            .replace(tzinfo=datetime.timezone.utc),
            "full_moon": ephem.next_full_moon(utc())
            .datetime()
            .replace(tzinfo=datetime.timezone.utc),
            "first_quarter": ephem.next_first_quarter_moon(utc())
            .datetime()
            .replace(tzinfo=datetime.timezone.utc),
            "last_quarter": ephem.next_last_quarter_moon(utc())
            .datetime()
            .replace(tzinfo=datetime.timezone.utc),
        }
    ).sort_values(ascending=True)
    # Figure out the timezone
    pgconn, cursor = get_dbconnc("mesosite")
    cursor.execute(
        "select tzid from tz_world WHERE "
        "st_contains(geom, st_setsrid(ST_Point(%s, %s), 4326))",
        (lon, lat),
    )
    if cursor.rowcount == 0:
        tzid = "UTC"
    else:
        tzid = cursor.fetchone()["tzid"]
    pgconn.close()
    tz = ZoneInfo(tzid)

    s = np.array(series)
    return pd.DataFrame(
        {
            "longitude": lon,
            "latitude": lat,
            "moon_phase1": series.index[0],
            "moon_phase1_date": s[0].astimezone(tz).strftime("%Y/%m/%d"),
            "moon_phase1_time": s[0].astimezone(tz).strftime("%-I:%M %P"),
            "moon_phase2": series.index[1],
            "moon_phase2_date": s[1].astimezone(tz).strftime("%Y/%m/%d"),
            "moon_phase2_time": s[1].astimezone(tz).strftime("%-I:%M %P"),
            "moon_phase3": series.index[2],
            "moon_phase3_date": s[2].astimezone(tz).strftime("%Y/%m/%d"),
            "moon_phase3_time": s[2].astimezone(tz).strftime("%-I:%M %P"),
            "moon_phase4": series.index[3],
            "moon_phase4_date": s[3].astimezone(tz).strftime("%Y/%m/%d"),
            "moon_phase4_time": s[3].astimezone(tz).strftime("%-I:%M %P"),
        },
        index=[0],
    )


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
    pgconn, cursor = get_dbconnc("mesosite")
    cursor.execute(
        "select tzid from tz_world WHERE "
        "st_contains(geom, st_setsrid(ST_Point(%s, %s), 4326))",
        (lon, lat),
    )
    if cursor.rowcount == 0:
        tzid = "UTC"
    else:
        tzid = cursor.fetchone()["tzid"]
    pgconn.close()
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
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            """
        select b.idot_id as locationid,
        replace(b.longname, ',', ' ') as locationname,
        ST_y(ST_transform(ST_centroid(b.geom),4326)) as latitude,
        ST_x(ST_transform(ST_centroid(b.geom),4326)) as longitude, cond_code
        from roads_base b JOIN roads_current c on (c.segid = b.segid)
        """,
            conn,
        )
    return df


def do_webcams(network):
    """direction arrows"""
    with get_sqlalchemy_conn("mesosite") as conn:
        df = pd.read_sql(
            text(
                """
        select cam as locationid, w.name as locationname,
        st_y(geom) as latitude,
        st_x(geom) as longitude, drct
        from camera_current c JOIN webcams w on (c.cam = w.id)
        WHERE c.valid > (now() - '30 minutes'::interval) and w.network = :net
        """
            ),
            conn,
            params={"net": network},
        )
    return df


def do_iowa_azos(date, itoday=False):
    """Dump high and lows for Iowa ASOS"""
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            text(
                f"""
        select id as locationid, n.name as locationname,
        st_y(geom) as latitude,
        st_x(geom) as longitude, s.day, s.max_tmpf::int as high,
        s.min_tmpf::int as low, coalesce(pday, 0) as precip
        from stations n JOIN summary_{date.year} s on (n.iemid = s.iemid)
        WHERE n.network = 'IA_ASOS' and s.day = :dt
        """
            ),
            conn,
            params={"dt": date},
            index_col="locationid",
        )
        if itoday:
            # Additionally, piggy back rainfall totals
            df2 = pd.read_sql(
                text(
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
            where t.network = 'IA_ASOS' and
            valid >= now() - '720 hours'::interval
            and phour > 0.005 GROUP by id
            """
                ),
                conn,
                index_col="station",
            )
            for col in [
                "precip24",
                "precip48",
                "precip72",
                "precip168",
                "precip720",
            ]:
                df[col] = df2[col].round(2)
                # make sure the new column is >= precip
                df.loc[df[col] < df["precip"], col] = df["precip"]
    df = df.reset_index()
    return df


def do_iarwis():
    """Dump RWIS data"""
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            text(
                """
        select id as locationid, n.name as locationname,
        st_y(geom) as latitude,
        st_x(geom) as longitude, tsf0 as pavetmp1, tsf1 as pavetmp2,
        tsf2 as pavetmp3, tsf3 as pavetmp4
        from stations n JOIN current s on (n.iemid = s.iemid)
        WHERE n.network in ('IA_RWIS', 'WI_RWIS', 'IL_RWIS') and
        s.valid > (now() - '2 hours'::interval)
        """
            ),
            conn,
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
    pgconn, cursor = get_dbconnc("hml")
    # Get metadata
    cursor.execute(
        """
        SELECT name, st_x(geom), st_y(geom), tzname from stations
        where id = %s and network ~* 'DCP'
    """,
        (nwsli,),
    )
    row = cursor.fetchone()
    latitude = row["st_y"]
    longitude = row["st_x"]
    stationname = row["name"]
    tzinfo = ZoneInfo(row["tzname"])
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
    if cursor.rowcount != 2:
        return "NO DATA"
    plabel = cursor.fetchone()["label"]
    slabel = cursor.fetchone()["label"]
    pgconn.close()
    with get_sqlalchemy_conn("hml") as conn:
        df = pd.read_sql(
            text(
                """
        WITH primaryv as (
        SELECT valid, value from hml_observed_data WHERE station = :nwsli
        and key = get_hml_observed_key(:plabel) and
        valid > now() - '1 day'::interval
        ), secondaryv as (
        SELECT valid, value from hml_observed_data WHERE station = :nwsli
        and key = get_hml_observed_key(:slabel) and
        valid > now() - '1 day'::interval
        )
        SELECT p.valid at time zone 'UTC' as valid,
        p.value as primary_value, s.value as secondary_value,
        'O' as type
        from primaryv p LEFT JOIN secondaryv s ON (p.valid = s.valid)
        WHERE p.valid > (now() - '72 hours'::interval)
        ORDER by p.valid DESC
        """
            ),
            conn,
            params={"nwsli": nwsli, "plabel": plabel, "slabel": slabel},
            index_col=None,
        )
    if df.empty:
        return "NO DATA"
    df["locationid"] = nwsli
    df["locationname"] = stationname
    df["latitude"] = latitude
    df["longitude"] = longitude
    df["Time"] = (
        df["valid"]
        .dt.tz_localize(ZoneInfo("UTC"))
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
    pgconn, cursor = get_dbconnc("hml")
    # Get metadata
    cursor.execute(
        "SELECT name, st_x(geom), st_y(geom), tzname from stations "
        "where id = %s and network ~* 'DCP'",
        (nwsli,),
    )
    row = cursor.fetchone()
    latitude = row["st_y"]
    longitude = row["st_x"]
    stationname = row["name"]
    tzinfo = ZoneInfo(row["tzname"])
    # Get the last forecast
    cursor.execute(
        """
        select id, forecast_sts at time zone 'UTC' as fts,
        generationtime at time zone 'UTC' as gts, primaryname, primaryunits,
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
    primaryname = row["primaryname"]
    generationtime = row["gts"]
    primaryunits = row["primaryunits"]
    secondaryname = row["secondaryname"]
    secondaryunits = row["secondaryunits"]
    pgconn.close()
    # Get the latest forecast
    with get_sqlalchemy_conn("hml") as conn:
        df = pd.read_sql(
            text(
                f"""
        SELECT valid at time zone 'UTC' as valid,
        primary_value, secondary_value, 'F' as type from
        hml_forecast_data_{generationtime.year} WHERE hml_forecast_id = :sid
        ORDER by valid ASC
        """
            ),
            conn,
            params={"sid": row["id"]},
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
        .dt.tz_localize(ZoneInfo("UTC"))
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
            f"{row['Flow[kcfs]']:.1f}kcfs\n"
        )
    return res


def feet(val, suffix="'"):
    """Make feet indicator"""
    if pd.isnull(val) or val == "":
        return ""
    return f"{val:.1f}{suffix}"


def do_ahps(nwsli):
    """Create a dataframe with AHPS river stage and CFS information"""
    pgconn, cursor = get_dbconnc("hml")
    # Get metadata
    cursor.execute(
        "SELECT name, st_x(geom), st_y(geom), tzname from stations "
        "where id = %s and network ~* 'DCP'",
        (nwsli,),
    )
    row = cursor.fetchone()
    latitude = row["st_y"]
    longitude = row["st_x"]
    stationname = row["name"].replace(",", " ")
    tzinfo = ZoneInfo(row["tzname"])
    # Get the last forecast
    cursor.execute(
        """
        select id, forecast_sts at time zone 'UTC' as fts,
        generationtime at time zone 'UTC' as gts, primaryname, primaryunits,
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
    generationtime = row["gts"]
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
        if _row["label"].find("[ft]") > 0:
            lookupkey = _row["id"]
            break
    pgconn.close()
    # get observations
    with get_sqlalchemy_conn("hml") as conn:
        odf = pd.read_sql(
            text(
                """
        SELECT valid at time zone 'UTC' as valid,
        value from hml_observed_data WHERE station = :nwsli
        and key = :lookupkey and valid > now() - '3 day'::interval
        and extract(minute from valid) = 0
        ORDER by valid DESC
        """
            ),
            conn,
            params={"nwsli": nwsli, "lookupkey": lookupkey},
            index_col=None,
        )
    # hoop jumping to get a timestamp in the local time of this sensor
    # see akrherz/iem#187
    odf["obtime"] = (
        odf["valid"]
        .dt.tz_localize(ZoneInfo("UTC"))
        .dt.tz_convert(tzinfo)
        .dt.strftime("%a. %-I %p")
    )
    # Get the latest forecast
    with get_sqlalchemy_conn("hml") as conn:
        df = pd.read_sql(
            text(
                f"""
            SELECT valid at time zone 'UTC' as valid,
            primary_value, secondary_value, 'F' as type from
            hml_forecast_data_{y} WHERE hml_forecast_id = :fid
            ORDER by valid ASC
        """
            ),
            conn,
            params={"fid": row["id"]},
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
        .dt.tz_localize(ZoneInfo("UTC"))
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
        vals = [
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
        ]
        res += ",".join(str(x) for x in vals) + "\n"

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
    elif appname.startswith("moonphase"):
        tokens = appname.replace(".txt", "").split("_")
        df = do_moonphase(float(tokens[1]), float(tokens[2]))
    elif appname.startswith("moon"):
        tokens = appname.replace(".txt", "").split("_")
        df = do_moon(float(tokens[1]), float(tokens[2]))
    else:
        df = "ERROR, unknown report specified"
    return df


@iemapp()
def application(environ, start_response):
    """Do Something"""
    appname = environ.get("q", "moonphase_-95_42")
    res = router(appname)
    start_response("200 OK", [("Content-type", "text/plain")])
    if isinstance(res, pd.DataFrame):
        return [res.to_csv(None, index=False).encode("ascii")]
    return [res.encode("ascii")]


def test_hml():
    """Can we do it?"""
    do_ahps("DBQI4")
    do_ahps_obs("ESSV1")
