#!/usr/bin/env python
"""Report on our second tipping bucket"""
from io import StringIO

from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, ssw


def main():
    """Go Main Go"""
    pgconn = get_dbconn("iem")
    amsi4 = read_sql(
        """
    SELECT to_char(day + '16 hours'::interval, 'YYYY-MM-DD HH:MI AM') as valid,
    pday as coop
    from summary s JOIN stations t on (s.iemid = t.iemid)
    where t.id = 'AMSI4' and day > '2017-07-25' and pday >= 0
    ORDER by day ASC
    """,
        pgconn,
        index_col="valid",
    )

    pgconn = get_dbconn("isuag")
    df = read_sql(
        """
    SELECT to_char(valid, 'YYYY-MM-DD HH:MI AM') as valid,
    rain_mm_tot / 25.4 as bucket1,
    rain_mm_2_tot / 25.4 as bucket2 from sm_hourly where station = 'BOOI4'
    and valid > '2017-07-25' and (rain_mm_tot > 0 or rain_mm_2_tot > 0)
    ORDER by valid ASC
    """,
        pgconn,
        index_col="valid",
    )
    df2 = amsi4.join(df, how="outer")
    sio = StringIO()
    df2.to_html(
        sio, classes="table table-striped", na_rep="-", float_format="%.2f"
    )
    sio.seek(0)
    ssw("Content-type: text/html\n\n")
    ssw(sio.getvalue())


if __name__ == "__main__":
    main()
