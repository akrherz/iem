"""Remove any duplicated rows with differenting temperatures

A stop gap hack to remove some bad data from the database.  Sadly, gonna be
tough to resolve how these obs appeared in the database to behind with :(
"""

from pyiem.util import get_dbconn


def do_year(year):
    """Process this year"""
    pgconn = get_dbconn("asos")
    cursor1 = pgconn.cursor()
    cursor2 = pgconn.cursor()
    table = "t%s" % (year,)
    cursor1.execute(
        """
    with data as (select station, valid, max(tmpf), min(tmpf), count(*)
    from """
        + table
        + """ GROUP by station, valid)
    select station, valid, count, max, min from data
    where count > 1 and max != min ORDER by valid
    """
    )
    removed = 0
    for row in cursor1:
        cursor2.execute(
            """
        DELETE from """
            + table
            + """ WHERE station = %s and valid = %s
        """,
            (row[0], row[1]),
        )
        removed += cursor2.rowcount
    print(
        ("%s found %s duplicated rows, deleted %s rows")
        % (year, cursor1.rowcount, removed)
    )
    cursor2.close()
    pgconn.commit()


def main():
    """Go Main"""
    for year in range(1928, 2017):
        do_year(year)


if __name__ == "__main__":
    main()
