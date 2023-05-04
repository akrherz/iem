"""Update the pday column

Some care has to be made here such that trace values do not accumulate when
there are actual measurable precip.  Eventually, the DSM or other summary
messages come and overwrite the trouble. Run from RUN_10MIN.sh
"""
import datetime

from pyiem.reference import TRACE_VALUE
from pyiem.util import get_dbconn


def main():
    """Go!"""
    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor()
    icursor2 = pgconn.cursor()

    now = datetime.datetime.now()
    yyyy = now.year

    # Run for the previous hour, so that we don't skip totaling up 11 PM
    icursor.execute(
        f"""
        WITH obs as (
            SELECT s.iemid, date(valid at time zone s.tzname) as d,
            max(phour) as rain,
            extract(hour from (valid - '1 minute'::interval)) as hour
            from current_log c, stations s
            WHERE s.network ~* 'ASOS' and c.iemid = s.iemid and
            date(valid at time zone s.tzname) =
                date((now() - '1 hour'::interval) at time zone s.tzname)
            and phour > 0
            GROUP by s.iemid, hour, d
        ), agg as (
            select o.iemid, o.d, sum(rain) as precip
            from obs o JOIN stations s on
            (s.iemid = o.iemid) GROUP by o.iemid, o.d
         ), agg2 as (
             SELECT iemid, d,
             case when precip > 0.009 then
               round(precip::numeric, 2) else precip end as pday
             from agg
         )
        UPDATE summary_{yyyy} s
        SET pday =
        case when a.pday < 0.009 and a.pday > 0 then %s else a.pday end
        FROM agg2 a
        WHERE s.iemid = a.iemid and s.day = a.d and
        (s.pday is null or s.pday != a.pday)
      """,
        (TRACE_VALUE,),
    )

    icursor2.close()
    icursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
