#		extractPrecip.py
# Extract Precipitation from DB
# Daryl Herzmann 19 Jul 2001
# 30 Jul 2001:	Fixed Problem when no precip data is reported
#		By adding the station FWD to the GEMPAK file
#		the generated plot will not fail
# 27 Jan 2002:	use t2002
# 28 Aug 2002:	coop DB is now on db1.mesonet
# 16 Jan 2003:	Lots of updates to this script, I am not sure
#		if it is even used though :)
#		Write out a shapefile with data in it...
# 16 Mar 2004:	Lets use IEM Access
# 23 Jul 2004	Cleanup, geez
# 14 Feb 2005	Fix summary stuff
###################################

from pyIEM import stationTable
import  mx.DateTime, shapelib, dbflib
import iemdb
import psycopg2.extras
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

now = mx.DateTime.now()
dateStr = now.strftime("%y%m%d/1200")
ts = now.strftime('%Y%m%d')
yyyy = now.strftime('%Y')

#icursor.execute("""update summary_%s SET max_tmpf = -99 WHERE 
# day = 'TODAY' and max_tmpf > 200""" % (yyyy,) )

cob = {}
#for id in st.ids:
#	cob[id] = {'TMPX': -99, 'TMPN': -99, 'P24I': -99, 'PMOI': -99,
#				'SMOI': -99, 'SNOW': -99, 'SNOD': -99}

icursor.execute("""SELECT c.station, c.pday, 
  coalesce(c.snow,-99) as snow, coalesce(c.snowd,-99) as snowd, 
  c.max_tmpf, 
	case when c.min_tmpf < 99 THEN c.min_tmpf ELSE -99 END as min_tmpf, 
	x(s.geom) as lon, y(s.geom) as lat, s.name 
	from summary c, current c2, stations s WHERE 
	c.station = s.id and s.id = c2.station and 
	c.network = s.network and s.network = c2.network and 
    s.network ~* 'COOP' and min_tmpf > -99 and c2.valid > 'TODAY' 
	and day = 'TODAY'""")

for row in icursor:
	thisStation = row["station"]
	cob[ thisStation ] = {}
	thisPrec = row["pday"]
	thisSnow = row["snow"]
	thisSnowD = row["snowd"]
	thisHigh  = row["max_tmpf"]
	thisLow   = row["min_tmpf"]

	# First we update our cobs dictionary
	cob[ thisStation ]["TMPX"] = float(thisHigh)
	cob[ thisStation ]["TMPN"] = float(thisLow)
	cob[ thisStation ]["P24I"] = round(float(thisPrec),2)
	cob[ thisStation ]["SNOW"] = float(thisSnow)
	cob[ thisStation ]["SNOD"] = float(thisSnowD)
	cob[ thisStation ]["LAT"] = row['lat']
	cob[ thisStation ]["LON"] = row['lon']
	cob[ thisStation ]["NAME"] = row['name']
	cob[ thisStation ]["PMOI"] = 0.
	cob[ thisStation ]["SMOI"] = 0.

icursor.execute("""SELECT station, sum(pday) as tprec, 
	sum( case when snow > 0 THEN snow ELSE 0 END) as tsnow 
	from summary_%s WHERE 
  date_part('month', day) = date_part('month', CURRENT_TIMESTAMP::date) 
	and date_part('year', day) = %s 
  and pday >= 0.00 and network ~* 'COOP' GROUP by station""" % (
								now.year, now.year) )

for row in icursor:
	thisStation = row["station"]
	thisPrec = row["tprec"]
	thisSnow = row["tsnow"]
	if (not cob.has_key(thisStation)):
		continue
	cob[ thisStation ]["PMOI"] = round(float(thisPrec),2)
	cob[ thisStation ]["SMOI"] = round(float(thisSnow),2)

dbf = dbflib.create("coop_"+ts)
dbf.add_field("SID", dbflib.FTString, 5, 0)
dbf.add_field("SITE_NAME", dbflib.FTString, 40, 0)
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

o = open('coop_obs.fil', 'w')
o.write(' PARM = TMPX;TMPN;P24I;PMOI;SMOI;SNOW;SNOD\n\n')
o.write('    STN     YYMMDD/HHMM    TMPX    TMPN      P24I      PMOI      SMOI      SNOW      SNOD\n')

j = 0
for id in cob.keys():

	obj = shapelib.SHPObject(shapelib.SHPT_POINT, j, \
		[[(cob[id]["LON"], cob[id]["LAT"])]] )
	shp.write_object(-1, obj)
	#print id, cob[id]
	o.write("%7s%16s%8.0f%8.0f%10.2f%10.2f%10.2f%10.2f%10.2f\n" % \
		(id, dateStr, cob[id]["TMPX"], cob[id]["TMPN"], \
		cob[id]["P24I"], cob[id]["PMOI"], cob[id]["SMOI"], cob[id]["SNOW"], \
		cob[id]["SNOD"]) )
        if (cob[id]["TMPX"] < 0): cob[id]["TMPX"] = -99.
        if (cob[id]["TMPN"] < 0): cob[id]["TMPN"] = -99.
        if (cob[id]["P24I"] < 0): cob[id]["P24I"] = -99.
        if (cob[id]["SNOW"] < 0): cob[id]["SNOW"] = -99.
        if (cob[id]["SNOD"] < 0): cob[id]["SNOD"] = -99.
        if (cob[id]["PMOI"] < 0): cob[id]["PMOI"] = -99.
        if (cob[id]["SMOI"] < 0): cob[id]["SMOI"] = -99.
	#print cob[id], id
	dbf.write_record(j, (id, cob[id]["NAME"], ts,"1200",\
		cob[id]["TMPX"], cob[id]["TMPN"], cob[id]["P24I"], \
		cob[id]["SNOW"], cob[id]["SNOD"], cob[id]["PMOI"], \
		cob[id]["SMOI"]) )
	del(obj)
	j += 1
o.close()

icursor.close()
IEM.commit()
IEM.close()