# Parse Harry Hillakers data into the database!

import sys, re, mx.DateTime, string

# We need to convert some station IDs to other IDs, somewhat yucky
stconv = {
  'ia6199': 'ia6200', # Oelwein
  'ia3288': 'ia3290', # Glenwood
}

year = int(sys.argv[1])
month = int(sys.argv[2])
fp = "/mnt/mesonet/data/harry/%s/SCIA%s%02i.txt" % (year, str(year)[2:], month)
print "Processing File: ", fp

lines = open(fp, 'r').readlines()

alldata = open('/tmp/harry.sql', 'w')
alldata.write("""BEGIN;
-- Remove anything old that may be in alldata_tmp
DELETE from alldata_tmp;
COPY alldata_tmp from STDIN with null as 'Null';
""")

for line in lines:
  tokens = re.split(",", line)
  if len(tokens[0]) == 23:
    stid = tokens[0]
    dbid = "%s%04.0f" % ("ia", int(stid))
    if stconv.has_key(dbid):
      dbid = stconv[dbid]
    yr = int(tokens[2])
    mo = int(tokens[3])
    dy = int(tokens[4])
    hi = string.strip(tokens[6])
    lo = string.strip(tokens[8])
    pr = string.strip(tokens[12])
    sf = string.strip(tokens[14])
    sd = string.strip(tokens[16])
    if (pr == "T"): pr = 0.0001
    if (sf == "T"): sf = 0.0001
    if (sd == "T"): sd = 0.0001
    if (sf == "M"): sf = ""
    if (sd == "M"): sd = ""
    if (hi == "M"): hi = ""
    if (lo == "M"): lo = ""
    if (pr == "M"): pr = ""
    if (pr == "C"): pr = ""
    if (sf == "C"): sf = ""
    if (sd == "C"): sd = ""

    if (sf == ""): sf = 0
    if (sd == ""): sd = 0
    if (pr == ""): pr = 0
    if (hi == ""): hi = "Null"
    if (lo == ""): lo = "Null"
    if (len(dbid) > 6): print dbid

    ts = mx.DateTime.DateTime(yr, mo, dy)
    day = ts.strftime("%Y-%m-%d")
    sday = ts.strftime("%m%d")
    # Compute the climate week
    jday = int( ts.strftime("%j") )
    if jday < 61:
      jday += 366
    jday -= 54
    cw = jday / 7
 
    alldata.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\tf\n" % \
        (dbid, day, cw, hi, lo, pr, sf, sday, yr, mo,sd) )


alldata.write("""\.
-- Now we need to clear the old estimates away
INSERT into alldata_estimates SELECT * from alldata WHERE year = %s
 and month = %s;
DELETE from alldata WHERE year = %s and month = %s;
INSERT into alldata SELECT * from alldata_tmp;

-- Now we print out some estimation stats
SELECT
  round(avg( e.rainfall - o.rainfall)::numeric,4) as rain_bias,
  round(avg( e.avghigh - o.avghigh)::numeric,4) as high_bias,
  round(avg( e.avglow - o.avglow)::numeric,4) as low_bias,
  round(avg( e.snowfall - o.snowfall)::numeric,4) as snowfall_bias,

  round(avg( abs(e.rainfall - o.rainfall) )::numeric,4) as rain_me,
  round(avg( abs(e.avghigh - o.avghigh) )::numeric,4) as high_me,
  round(avg( abs(e.avglow - o.avglow) )::numeric,4) as low_me,
  round(avg( abs(e.snowfall - o.snowfall) )::numeric,4) as snowfall_me

FROM
  (select stationid, sum(precip) as rainfall, sum(snow) as snowfall,
          avg(high) as avghigh, avg(low) as avglow
   from alldata
   WHERE month = %s and year = %s GROUP by stationid) as o,
  (select stationid, sum(precip) as rainfall, sum(snow) as snowfall,
          avg(high) as avghigh, avg(low) as avglow
   from alldata_estimates
   WHERE month = %s and year = %s GROUP by stationid) as e
WHERE
  o.stationid = e.stationid
;
COMMIT;
""" % (year, month, year, month, month, year, month, year) )
alldata.close()
