#!/usr/bin/env python
"""Provide some CSV Files

first four columns need to be
ID,Station,Latitude,Longitude
"""
import cgi
import datetime
import sys

import pytz
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, ssw

# DOT plows
# RWIS sensor data
# River gauges
# Ag data (4" soil temps)


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
    """Dump high and lows for Iowa ASOS + AWOS """
    table = "summary_%s" % (date.year,)
    pgconn = get_dbconn("iem")
    df = read_sql(
        """
    select id as locationid, n.name as locationname, st_y(geom) as latitude,
    st_x(geom) as longitude, s.day, s.max_tmpf::int as high,
    s.min_tmpf::int as low, pday as precip
    from stations n JOIN """
        + table
        + """ s on (n.iemid = s.iemid)
    WHERE n.network in ('IA_ASOS', 'AWOS') and s.day = %s
    """,
        pgconn,
        params=(date,),
        index_col="locationid",
    )
    if itoday:
        # Additionally, piggy back rainfall totals
        df2 = read_sql(
            """
        SELECT station,
        sum(phour) as precip720,
        sum(case when valid >= (now() - '168 hours'::interval)
            then phour else 0 end) as precip168,
        sum(case when valid >= (now() - '72 hours'::interval)
            then phour else 0 end) as precip72,
        sum(case when valid >= (now() - '48 hours'::interval)
            then phour else 0 end) as precip48,
        sum(case when valid >= (now() - '24 hours'::interval)
            then phour else 0 end) as precip24
        from hourly where network in ('IA_ASOS', 'AWOS')
        and valid >= now() - '720 hours'::interval
        and phour > 0.005 GROUP by station
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
    df.reset_index(inplace=True)
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
        .map(lambda x: "%.0f" % x if not pd.isna(x) else "")
    )
    return df


def do_ahps_obs(nwsli):
    """Create a dataframe with AHPS river stage and CFS information"""
    pgconn = get_dbconn("hads")
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
        ssw("Content-type: text/plain\n\n")
        ssw("NO DATA")
        sys.exit()
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
    ssw("Content-type: text/plain\n\n")
    ssw("Observed Data:,,\n")
    ssw("|Date|,|Stage|,|--Flow-|\n")
    odf = df[df["type"] == "O"]
    for _, row in odf.iterrows():
        ssw(
            "%s,%.2fft,%.1fkcfs\n"
            % (row["Time"], row["Stage[ft]"], row["Flow[kcfs]"])
        )
    sys.exit(0)


def do_ahps_fx(nwsli):
    """Create a dataframe with AHPS river stage and CFS information"""
    pgconn = get_dbconn("hads")
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
    y = "{}".format(generationtime.year)
    # Get the latest forecast
    df = read_sql(
        """
    SELECT valid at time zone 'UTC' as valid,
    primary_value, secondary_value, 'F' as type from
    hml_forecast_data_"""
        + y
        + """ WHERE hml_forecast_id = %s
    ORDER by valid ASC
    """,
        pgconn,
        params=(row[0],),
        index_col=None,
    )
    # Get the obs
    plabel = "{}[{}]".format(primaryname, primaryunits)
    slabel = "{}[{}]".format(secondaryname, secondaryunits)

    sys.stderr.write(str(primaryname))
    sys.stderr.write(str(secondaryname))

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
    ssw("Content-type: text/plain\n\n")
    ssw(
        "Forecast Data (Issued %s UTC):,\n"
        % (generationtime.strftime("%m-%d-%Y %H:%M:%S"),)
    )
    ssw("|Date|,|Stage|,|--Flow-|\n")
    odf = df[df["type"] == "F"]
    for _, row in odf.iterrows():
        ssw(
            "%s,%.2fft,%.1fkcfs\n"
            % (row["Time"], row["Stage[ft]"], row["Flow[kcfs]"])
        )

    sys.exit(0)


def feet(val, suffix="'"):
    """Make feet indicator"""
    if pd.isnull(val) or val == "":
        return ""
    return "%.1f%s" % (val, suffix)


def do_ahps(nwsli):
    """Create a dataframe with AHPS river stage and CFS information"""
    pgconn = get_dbconn("hads")
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
        ssw("Content-type: text/plain\n\n")
        ssw("NO DATA")
        sys.exit()
    row = cursor.fetchone()
    generationtime = row[2]
    y = "{}".format(generationtime.year)
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
        ssw("Content-type: text/plain\n\n")
        ssw("NO DATA")
        sys.exit()
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
        """
        SELECT valid at time zone 'UTC' as valid,
        primary_value, secondary_value, 'F' as type from
        hml_forecast_data_"""
        + y
        + """ WHERE hml_forecast_id = %s
        ORDER by valid ASC
    """,
        pgconn,
        params=(row[0],),
        index_col=None,
    )
    # Get the obs
    # plabel = "{}[{}]".format(primaryname, primaryunits)
    # slabel = "{}[{}]".format(secondaryname, secondaryunits)
    odf.rename({"value": "obstage"}, axis=1, inplace=True)
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
    ssw("Content-type: text/plain\n\n")
    ssw(
        (
            "locationid,locationname,latitude,longitude,obtime,obstage,"
            "obstage2,obstagetext,forecasttime,forecaststage,forecaststage1,"
            "forecaststage2,forecaststage3,highestvalue,highestvalue2,"
            "highestvaluedate\n"
        )
    )
    ssw(",,,,,,,,,,,,,,,\n,,,,,,,,,,,,,,,\n")

    maxrow = df.sort_values("forecaststage", ascending=False).iloc[0]
    for idx, row in df.iterrows():
        fs = (
            row["forecaststage"] if not pd.isnull(row["forecaststage"]) else ""
        )
        ssw(
            ("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n")
            % (
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
        )

    sys.exit(0)


def router(appname):
    """Process and return dataframe"""
    # elif appname == 'iadotplows':
    #    df = do_iadotplows()
    # elif appname == 'iariver':
    #    df = do_iariver()
    # elif appname == 'isusm':
    #    df = do_isusm()
    if appname.startswith("ahpsobs_"):
        do_ahps_obs(appname[8:].upper())  # we write ourselves and exit
    elif appname.startswith("ahpsfx_"):
        do_ahps_fx(appname[7:].upper())  # we write ourselves and exit
    elif appname.startswith("ahps_"):
        do_ahps(appname[5:].upper())  # we write ourselves and exit
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
    else:
        sys.stdout.write("""ERROR, unknown report specified""")
        sys.exit()
    return df


def main():
    """Do Something"""
    form = cgi.FieldStorage()
    appname = form.getfirst("q")
    df = router(appname)
    ssw("Content-type: text/plain\n\n")
    ssw(df.to_csv(None, index=False))
    ssw("\n")


def test_hml():
    """Can we do it?"""
    do_ahps("DBQI4")


if __name__ == "__main__":
    main()
