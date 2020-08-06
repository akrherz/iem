"""Report on our second tipping bucket"""
from io import StringIO

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn


def application(_environ, start_response):
    """Go Main Go"""
    pgconn = get_dbconn("iem")
    amsi4 = read_sql(
        """
    SELECT to_char(day + '16 hours'::interval, 'YYYY-MM-DD HH24:MI') as valid,
    pday as coop, day
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
    SELECT to_char(valid, 'YYYY-MM-DD HH24:MI') as valid,
    case when extract(hour from valid) > 16 then
        date(valid + '8 hours'::interval) else date(valid) end as coop_date,
    rain_mm_tot / 25.4 as bucket1_hourly,
    coalesce(rain_in_2_tot, rain_mm_2_tot / 25.4) as bucket2_hourly
    from sm_hourly where station = 'BOOI4'
    and valid > '2017-07-25' and (rain_mm_tot > 0 or rain_mm_2_tot > 0)
    ORDER by valid ASC
    """,
        pgconn,
        index_col="valid",
    )
    aggobs = df.groupby("coop_date").sum(numeric_only=True)
    aggobs.columns = [
        s.replace("_hourly", "") + "_total" for s in aggobs.columns
    ]
    df = df.drop("coop_date", axis=1)

    df2 = amsi4.join(df, how="outer")
    df2 = df2.merge(aggobs, how="outer", left_on="day", right_index=True)
    df2 = df2.drop("day", axis=1)
    df2 = df2.sort_index(ascending=True).reset_index()
    df2["valid"] = pd.to_datetime(df2["index"]).dt.strftime("%Y-%m-%d %-I %p")
    sio = StringIO()
    df2.to_html(
        sio,
        columns=[
            "valid",
            "coop",
            "bucket1_total",
            "bucket2_total",
            "bucket1_hourly",
            "bucket2_hourly",
        ],
        classes="table table-striped tableFixHead",
        na_rep="-",
        float_format="%.2f",
        index=False,
    )
    sio.seek(0)
    headers = [("Content-type", "text/html")]
    start_response("200 OK", headers)
    return [sio.getvalue().encode("ascii")]
