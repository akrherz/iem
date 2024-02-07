"""
 Squawk to daryl about unknown sites

Run from RUN_2AM.sh
"""

from pyiem.database import get_dbconn, get_dbconnc


def do_asos():
    """Print out METAR ingest unknown stations"""
    asos = get_dbconn("asos")
    acursor = asos.cursor()
    acursor2 = asos.cursor()

    print("----- Unknown IDs from METAR sites -----")
    acursor.execute(
        "select id, count(*), max(valid) from unknown GROUP by id "
        "ORDER by count DESC"
    )
    for row in acursor:
        print("ASOS %7s %5s %s" % (row[0], row[1], row[2]))
        acursor2.execute("DELETE from unknown where id = %s", (row[0],))

    asos.commit()


def check_asos_in_coop_network():
    """We don't want this situation for convoluted reasons."""
    pgconn, cursor = get_dbconnc("mesosite")
    cursor.execute(
        """
        with data as (
            select id,
            max(case when network ~* 'COOP' then 1 else 0 end) as is_coop,
            max(case when network ~* 'ASOS' then 1 else 0 end) as is_asos,
            max(case when network ~* 'DCP' then 1 else 0 end) as is_dcp
            from stations GROUP by id)
        select id from data where is_coop > 0 and is_asos > 0"""
    )
    if cursor.rowcount > 0:
        print("------ ASOS in COOP Network ------")
        for row in cursor:
            print(f"ASOS Site in COOP, not DCP: {row['id']}")
    cursor.close()
    pgconn.close()


def print_blank_sname():
    """Make sure stations have names"""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT id, network from stations "
        "WHERE name is null or name = '' ORDER by iemid ASC LIMIT 5"
    )
    if cursor.rowcount > 0:
        print("------ Sites with empty station names ------")
    for row in cursor:
        print("%10s %s" % (row[0], row[1]))


def do_hads():
    """Print out the hads stuff."""
    hads = get_dbconn("hads")
    access = get_dbconn("iem")
    hcursor = hads.cursor()
    acursor = access.cursor()

    print("----- Unknown NWSLIs from SHEF Ingest -----")
    hcursor.execute(
        """
        select nwsli, count(*) as tot, max(product) as maxp,
        count(distinct substr(product,1,8)),
        count(distinct product),
        max(case when substr(nwsli,4,2) = 'I4' then 2
        when substr(product, 14, 4) = 'KWOH' then 1
        else 0 end) as priority
        from unknown
        where nwsli ~ '^[A-Z]{4}[0-9]$' and
        substr(product, 1, 6) = to_char(now(), 'YYYYmm')
        GROUP by nwsli ORDER by priority DESC, tot DESC LIMIT 50
    """
    )
    for row in hcursor:
        print(
            ("%7s Tot:%4s Days:%2s Products: %s %s")
            % (row[0], row[1], row[3], row[4], row[2])
        )
        # Get vars reported for this site
        acursor.execute(
            "SELECT valid, physical_code || duration || source || "
            "extremum || probability as p, value from current_shef "
            "WHERE station = %s ORDER by p ASC",
            (row[0],),
        )
        for row2 in acursor:
            print(f"    {row2[0]} {row2[1]} {row2[2]}")


def main():
    """Go Main Go"""
    do_asos()
    do_hads()
    print_blank_sname()
    check_asos_in_coop_network()


if __name__ == "__main__":
    main()
