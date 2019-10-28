"""util dumper"""
import sys
import datetime

from pandas.io.sql import read_sql
from pyiem.util import get_dbconn


def main(argv):
    """Go"""
    pgconn = get_dbconn("asos", user="nobody")

    station = argv[1]

    df = read_sql(
        """
        select date_trunc('hour', valid at time zone 'America/New_York') as hr,
        max(valid) as max_v, min(valid) as min_v,
        extract(minute from valid)::int / 15 as mi, sum(precip)
        from alldata_1minute
        WHERE station = %s and precip > 0 and precip < 0.5
        GROUP by hr, mi ORDER by hr, mi ASC
        """,
        pgconn,
        params=(station,),
        index_col=None,
    )

    df["valid"] = df.apply(
        lambda x: x["hr"] + datetime.timedelta(minutes=(15 * x["mi"])), axis=1
    )
    df[["valid", "sum"]].to_csv("%s.csv" % (station,), index=False)


if __name__ == "__main__":
    main(sys.argv)
