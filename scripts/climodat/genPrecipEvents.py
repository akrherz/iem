"""
 Generate Precip Event records!
"""

import constants 
import cweek

def write(cursor, out, station):
    """ Do our business """
    table = constants.get_table(station)
    cursor.execute("""
    with events as (
        SELECT c.climoweek, a.precip, a.year from """+table+""" a
        JOIN climoweek c on (c.sday = a.sday) WHERE a.station = %s
        and precip >= 0.01),
    ranks as (
        SELECT climoweek, year,
        rank() OVER (PARTITION by climoweek ORDER by precip DESC)
        from events), 
    stats as (
    SELECT climoweek, max(precip), avg(precip), 
    sum(case when precip >= 0.01 and precip < 0.26 then 1 else 0 end) as cat1, 
    sum(case when precip >= 0.26 and precip < 0.51 then 1 else 0 end) as cat2, 
    sum(case when precip >= 0.51 and precip < 1.01 then 1 else 0 end) as cat3, 
    sum(case when precip >= 1.01 and precip < 2.01 then 1 else 0 end) as cat4, 
    sum(case when precip >= 2.01 then 1 else 0 end) as cat5, 
    count(*) from events GROUP by climoweek)
    SELECT e.climoweek, e.max, r.year, e.avg, e.cat1, e.cat2, e.cat3, e.cat4,
    e.cat5 from 
    stats e JOIN ranks r on (r.climoweek = e.climoweek) WHERE r.rank = 1
    ORDER by e.climoweek ASC
    """, (station,))
    
    out.write("""\
# Based on climoweek periods, this report summarizes liquid precipitation.
#                                     Number of precip events - (% of total)
 CL                MAX         MEAN   0.01-    0.26-    0.51-    1.01-            TOTAL
 WK TIME PERIOD    VAL  YR     RAIN     0.25     0.50     1.00     2.00    >2.01  DAYS
""")

    annEvents = 0
    cat1t = 0
    cat2t = 0
    cat3t = 0
    cat4t = 0
    cat5t = 0
    maxRain = 0
    totRain = 0
    lastcw = 0
    for row in cursor:
        cw = int(row["climoweek"])
        # Skip ties
        if cw == lastcw:
            continue
        lastcw = cw
        cat1 = row["cat1"]
        cat2 = row["cat2"]
        cat3 = row["cat3"]
        cat4 = row["cat4"]
        cat5 = row["cat5"]
        cat1t += cat1
        cat2t += cat2
        cat3t += cat3
        cat4t += cat4
        cat5t += cat5
        maxval = row["max"]
        if maxval > maxRain:
            maxRain = maxval
        meanval = row["avg"]
        totEvents = cat1 + cat2 + cat3 + cat4 + cat5
        annEvents += totEvents
        totRain += ( totEvents * meanval)
    
        out.write(("%3s %-13s %5.2f %i   %4.2f %4i(%2i) %4i(%2i) "
                   +"%4i(%2i) %4i(%2i) %4i(%2i)   %4i\n") % (
                cw, cweek.cweek[cw], 
          maxval, row['year'], meanval, 
          cat1, round((float(cat1) / float(totEvents)) * 100.0), 
          cat2, round((float(cat2) / float(totEvents)) * 100.0), 
          cat3, round((float(cat3) / float(totEvents)) * 100.0), 
          cat4, round((float(cat4) / float(totEvents)) * 100.0), 
          cat5, round((float(cat5) / float(totEvents)) * 100.0), totEvents) )


    out.write("%-17s %5.2f        %4.2f %4i(%2i) %4i(%2i) %4i(%2i) %4i(%2i) %4i(%2i)  %5i\n" % (
            "ANNUAL TOTALS", maxRain, totRain / annEvents, 
            cat1t, (float(cat1t) / float(annEvents)) * 100, 
            cat2t, (float(cat2t) / float(annEvents)) * 100, 
            cat3t, (float(cat3t) / float(annEvents)) * 100, 
            cat4t, (float(cat4t) / float(annEvents)) * 100, 
            cat5t, (float(cat5t) / float(annEvents)) * 100, annEvents) )

