"""Climodat"""
import datetime

from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, get_autoplot_context
from pyiem.exceptions import NoDataFound

CWEEK = {1: '3/1-->3/7   ',
         2: '3/8-->3/14  ',
         3: '3/15-->3/21 ',
         4: '3/22-->3/28 ',
         5: '3/29-->4/4  ',
         6: '4/5-->4/11  ',
         7: '4/12-->4/18 ',
         8: '4/19-->4/25 ',
         9: '4/26-->5/2  ',
         10: '5/3-->5/9   ',
         11: '5/10-->5/16 ',
         12: '5/17-->5/23 ',
         13: '5/24-->5/30 ',
         14: '5/31-->6/6  ',
         15: '6/7-->6/13  ',
         16: '6/14-->6/20 ',
         17: '6/21-->6/27 ',
         18: '6/28-->7/4  ',
         19: '7/5-->7/11  ',
         20: '7/12-->7/18 ',
         21: '7/19-->7/25 ',
         22: '7/26-->8/1  ',
         23: '8/2-->8/8   ',
         24: '8/9-->8/15  ',
         25: '8/16-->8/22 ',
         26: '8/23-->8/29 ',
         27: '8/30-->9/5  ',
         28: '9/6-->9/12  ',
         29: '9/13-->9/19 ',
         30: '9/20-->9/26 ',
         31: '9/27-->10/3 ',
         32: '10/4-->10/10',
         33: '10/11-->10/17',
         34: '10/18-->10/24',
         35: '10/25-->10/31',
         36: '11/1-->11/7 ',
         37: '11/8-->11/14',
         38: '11/15-->11/21',
         39: '11/22-->11/28',
         40: '11/29-->12/5',
         41: '12/6-->12/12',
         42: '12/13-->12/19',
         43: '12/20-->12/26',
         44: '12/27-->1/2 ',
         45: '1/3-->1/9   ',
         46: '1/10-->1/16 ',
         47: '1/17-->1/23 ',
         48: '1/24-->1/30 ',
         49: '1/31-->2/6  ',
         50: '2/7-->2/13  ',
         51: '2/14-->2/20 ',
         52: '2/21-->2/27 ',
         53: '2/28-->2/29 '}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc['data'] = True
    desc['report'] = True
    desc['description'] = """ """
    desc['arguments'] = [
        dict(type='station', name='station', default='IATDSM',
             label='Select Station'),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn('coop')
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx['station']

    table = "alldata_%s" % (station[:2], )
    df = read_sql("""
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
    """, pgconn, params=(station,), index_col=None)
    if df.empty:
        raise NoDataFound("No Data Found.")

    res = """\
# IEM Climodat https://mesonet.agron.iastate.edu/climodat/
# Report Generated: %s
# Climate Record: %s -> %s
# Site Information: [%s] %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978
# Based on climoweek periods, this report summarizes liquid precipitation.
#                                     Number of precip events - (%% of total)
 CL                MAX         MEAN   0.01-    0.26-    0.51-    1.01-            TOTAL
 WK TIME PERIOD    VAL  YR     RAIN     0.25     0.50     1.00     2.00    >2.01  DAYS
""" % (datetime.date.today().strftime("%d %b %Y"),
       ctx['_nt'].sts[station]['archive_begin'].date(), datetime.date.today(), station,
       ctx['_nt'].sts[station]['name'])

    annEvents = 0
    cat1t = 0
    cat2t = 0
    cat3t = 0
    cat4t = 0
    cat5t = 0
    maxRain = 0
    totRain = 0
    lastcw = 0
    for _, row in df.iterrows():
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
        totRain += (totEvents * meanval)

        res += ("%3s %-13s %5.2f %i   %4.2f %4i(%2i) %4i(%2i) "
                "%4i(%2i) %4i(%2i) %4i(%2i)   %4i\n"
                ) % (cw, CWEEK[cw],
                     maxval, row['year'], meanval,
                     cat1, round((float(cat1) / float(totEvents)) * 100.0),
                     cat2, round((float(cat2) / float(totEvents)) * 100.0),
                     cat3, round((float(cat3) / float(totEvents)) * 100.0),
                     cat4, round((float(cat4) / float(totEvents)) * 100.0),
                     cat5, round((float(cat5) / float(totEvents)) * 100.0),
                     totEvents)

    res += ("%-17s %5.2f        %4.2f %4i(%2i) %4i(%2i) "
            "%4i(%2i) %4i(%2i) %4i(%2i)  %5i\n"
            ) % (
                 "ANNUAL TOTALS", maxRain, totRain / annEvents,
                 cat1t, (float(cat1t) / float(annEvents)) * 100,
                 cat2t, (float(cat2t) / float(annEvents)) * 100,
                 cat3t, (float(cat3t) / float(annEvents)) * 100,
                 cat4t, (float(cat4t) / float(annEvents)) * 100,
                 cat5t, (float(cat5t) / float(annEvents)) * 100, annEvents)

    return None, df, res


if __name__ == '__main__':
    plotter(dict())
