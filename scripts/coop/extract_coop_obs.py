""" Dump out obs from the database for use by other apps """

import mx.DateTime
import shapelib
import dbflib
import psycopg2.extras
import subprocess
import os

IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

now = mx.DateTime.now()
dateStr = now.strftime("%y%m%d/1200")
ts = now.strftime('%Y%m%d')
yyyy = now.strftime('%Y')

cob = {}

icursor.execute("""SELECT s.id, coalesce(c.pday, 0) as pday,
    coalesce(c.snow,-99) as snow, coalesce(c.snowd,-99) as snowd,
    coalesce(c.max_tmpf, -99) as max_tmpf,
    case when c.min_tmpf < 99 THEN c.min_tmpf ELSE -99 END as min_tmpf,
    ST_x(s.geom) as lon, ST_y(s.geom) as lat, s.name,
    c2.valid at time zone 'UTC' as vvv, s.elevation
    from summary_%s c, current c2, stations s WHERE
    c.iemid = c2.iemid and s.iemid = c.iemid and
    s.network ~* 'COOP' and min_tmpf > -99 and c2.valid > 'TODAY'
    and day = 'TODAY'""" % (yyyy,))

for row in icursor:
    thisStation = row["id"]
    cob[thisStation] = {}
    thisPrec = row["pday"]
    thisSnow = row["snow"]
    thisSnowD = row["snowd"]
    thisHigh = row["max_tmpf"]
    thisLow = row["min_tmpf"]

    # First we update our cobs dictionary
    cob[thisStation]["TMPX"] = float(thisHigh)
    cob[thisStation]["TMPN"] = float(thisLow)
    cob[thisStation]["P24I"] = round(float(thisPrec), 2)
    cob[thisStation]["SNOW"] = float(thisSnow)
    cob[thisStation]["SNOD"] = float(thisSnowD)
    cob[thisStation]["LAT"] = row['lat']
    cob[thisStation]["LON"] = row['lon']
    cob[thisStation]["NAME"] = row['name']
    cob[thisStation]['ELEV_M'] = row['elevation']
    cob[thisStation]["PMOI"] = 0.
    cob[thisStation]["SMOI"] = 0.
    cob[thisStation]['HHMM'] = row['vvv'].strftime('%H%M')

icursor.execute("""
    SELECT t.id, sum(pday) as tprec,
    sum( case when snow > 0 THEN snow ELSE 0 END) as tsnow
    from summary_%s s, stations t WHERE
    date_part('month', day) = date_part('month', CURRENT_TIMESTAMP::date)
    and date_part('year', day) = %s
    and pday >= 0.00 and t.network ~* 'COOP' and t.iemid = s.iemid
    GROUP by id
    """ % (now.year, now.year))

for row in icursor:
    thisStation = row["id"]
    thisPrec = row["tprec"]
    thisSnow = row["tsnow"]
    if thisStation not in cob:
        continue
    cob[thisStation]["PMOI"] = round(float(thisPrec), 2)
    cob[thisStation]["SMOI"] = round(float(thisSnow), 2)

csv = open('coop.csv', 'w')
csv.write('nwsli,site_name,longitude,latitude,date,time,high_f,low_f,prec_in,')
csv.write('snow_in,snow_depth_in,prec_mon_in,snow_mon_in,elevation_m\n')

dbf = dbflib.create("coop_"+ts)
dbf.add_field("SID", dbflib.FTString, 5, 0)
dbf.add_field("SITE_NAME", dbflib.FTString, 40, 0)
dbf.add_field("ELEV_M", dbflib.FTDouble, 10, 2)
dbf.add_field("YYYYMMDD", dbflib.FTString, 8, 0)
dbf.add_field("HHMM", dbflib.FTString, 4, 0)
dbf.add_field("HI_T_F", dbflib.FTInteger, 10, 0)
dbf.add_field("LO_T_F", dbflib.FTInteger, 10, 0)
dbf.add_field("PREC", dbflib.FTDouble, 10, 2)
dbf.add_field("SNOW", dbflib.FTDouble, 10, 2)
dbf.add_field("SDEPTH", dbflib.FTDouble, 10, 2)
dbf.add_field("PMONTH", dbflib.FTDouble, 10, 2)
dbf.add_field("SMONTH", dbflib.FTDouble, 10, 2)

shp = shapelib.create("coop_"+ts, shapelib.SHPT_POINT)

j = 0
for sid in cob.keys():

    obj = shapelib.SHPObject(shapelib.SHPT_POINT, j,
                             [[(cob[sid]["LON"], cob[sid]["LAT"])]])
    shp.write_object(-1, obj)
    # print id, cob[sid]
    if cob[sid]["TMPX"] < 0:
        cob[sid]["TMPX"] = -99.
    if cob[sid]["TMPN"] < 0:
        cob[sid]["TMPN"] = -99.
    if cob[sid]["P24I"] < 0:
        cob[sid]["P24I"] = -99.
    if cob[sid]["SNOW"] < 0:
        cob[sid]["SNOW"] = -99.
    if cob[sid]["SNOD"] < 0:
        cob[sid]["SNOD"] = -99.
    if cob[sid]["PMOI"] < 0:
        cob[sid]["PMOI"] = -99.
    if cob[sid]["SMOI"] < 0:
        cob[sid]["SMOI"] = -99.
    # print cob[sid], id
    dbf.write_record(j, (sid, cob[sid]["NAME"], cob[sid]['ELEV_M'], ts, "1200",
                         cob[sid]["TMPX"], cob[sid]["TMPN"], cob[sid]["P24I"],
                         cob[sid]["SNOW"], cob[sid]["SNOD"], cob[sid]["PMOI"],
                         cob[sid]["SMOI"]))

    csv.write(("%s,%s,%.4f,%.4f,%s,%s,%s,%s,%s,%s,%s,%s,%s,%.1f\n"
               ) % (sid, cob[sid]["NAME"].replace(",", " "),
                    cob[sid]['LON'], cob[sid]["LAT"],
                    ts, cob[sid]['HHMM'], cob[sid]["TMPX"], cob[sid]["TMPN"],
                    cob[sid]["P24I"],
                    cob[sid]["SNOW"], cob[sid]["SNOD"], cob[sid]["PMOI"],
                    cob[sid]["SMOI"], cob[sid]['ELEV_M']))

    del(obj)
    j += 1

icursor.close()
IEM.commit()
IEM.close()

# Ship csv file
csv.close()
pqstr = "plot c %s csv/coop.csv bogus csv" % (
                            mx.DateTime.now().strftime("%Y%m%d%H%M"),)
subprocess.call("/home/ldm/bin/pqinsert -p '%s' coop.csv" % (pqstr,),
                shell=True)
os.unlink('coop.csv')
