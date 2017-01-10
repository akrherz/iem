"""Update the pday column

Some care has to be made here such that trace values do not accumulate when
there are actual measurable precip.  Eventually, the DSM or other summary
messages come and overwrite the trouble. Run from RUN_10MIN.sh
"""
import psycopg2
import datetime
IEM = psycopg2.connect(database='iem', host='iemdb')
icursor = IEM.cursor()
icursor2 = IEM.cursor()

now = datetime.datetime.now()
yyyy = now.year

icursor.execute("""
    WITH obs as (
        SELECT s.iemid, date(valid at time zone s.tzname) as d,
        max(phour) as rain,
        extract(hour from (valid - '1 minute'::interval)) as hour
        from current_log c, stations s
        WHERE (s.network IN ('AWOS') or s.network ~* 'ASOS') and
        c.iemid = s.iemid and
        date(valid at time zone s.tzname) = date(now() at time zone s.tzname)
        and phour > 0
        GROUP by s.iemid, hour, d
    ), agg as (
        select o.iemid, o.d, sum(rain) as precip from obs o JOIN stations s on
        (s.iemid = o.iemid) GROUP by o.iemid, o.d
     ), agg2 as (
         SELECT iemid, d,
         case when precip >= 0.01 then
           round(precip::numeric, 2) else precip end as pday
         from agg
     )
    UPDATE summary_"""+str(yyyy)+""" s SET pday = a.pday FROM agg2 a
    WHERE s.iemid = a.iemid and s.day = a.d and
    (s.pday is null or s.pday != a.pday)
  """)

icursor2.close()
icursor.close()
IEM.commit()
