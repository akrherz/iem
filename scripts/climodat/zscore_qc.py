"""Use a simple zscore system to null out suspect data"""
from __future__ import print_function
import sys
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn

PGCONN = get_dbconn("coop", user="nobody")


def do(state, vname):
    """do"""
    network = "%sCLIMATE" % (state,)
    table = "alldata_%s" % (state,)
    df = read_sql(
        """
    WITH mystations as (
    SELECT id from stations where network = %s and
    (temp24_hour is null or temp24_hour between 4 and 9) and
    substr(id, 3, 1) != 'C' and substr(id, 3, 4) != '0000'),
    stats as (
    SELECT day, avg("""
        + vname
        + """), stddev("""
        + vname
        + """) from
    """
        + table
        + """ o JOIN mystations t on (o.station = t.id) GROUP by day),
    agg as (
    SELECT o.day, abs((o."""
        + vname
        + """- s.avg) / s.stddev) as zscore,
    o."""
        + vname
        + """, s.avg, s.stddev, o.station from """
        + table
        + """ o,
    mystations t, stats s WHERE
    o.day = s.day and t.id = o.station)

    SELECT * from agg where zscore > 4 ORDER by day
    """,
        PGCONN,
        params=(network,),
        index_col=None,
    )
    print(df.groupby("day").count())


def main(argv):
    """Go Main Go"""
    state = argv[1]
    for vname in ["high", "low"]:
        do(state, vname)


if __name__ == "__main__":
    main(sys.argv)
