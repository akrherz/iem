"""Update the pday column

Some care has to be made here such that trace values do not accumulate when
there are actual measurable precip.  Eventually, the DSM or other summary
messages come and overwrite the trouble. Run from RUN_10MIN.sh
"""

import time
from datetime import datetime

from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.reference import TRACE_VALUE
from pyiem.util import logger
from sqlalchemy.engine import Connection

LOG = logger()


@with_sqlalchemy_conn("iem")
def main(conn: Connection | None = None) -> None:
    """Go!"""
    now = datetime.now()
    yyyy = now.year

    # Run for the previous hour, so that we don't skip totaling up 11 PM
    res = conn.execute(
        sql_helper(
            """
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
        UPDATE {table} s
        SET pday =
        case when a.pday < 0.009 and a.pday > 0 then :tv else a.pday end
        FROM agg2 a
        WHERE s.iemid = a.iemid and s.day = a.d and
        (s.pday is null or s.pday != a.pday)
      """,
            table=f"summary_{yyyy}",
        ),
        {"tv": TRACE_VALUE},
    )
    LOG.info("Updated %s rows", res.rowcount)
    conn.commit()


def frontend() -> None:
    """Proxy."""
    for _ in range(2):
        try:
            main()
            return
        except Exception as exp:
            LOG.info("Failed to update summary: %s", exp)
            time.sleep(60)
    LOG.warning("Both attempts failed")


if __name__ == "__main__":
    frontend()
