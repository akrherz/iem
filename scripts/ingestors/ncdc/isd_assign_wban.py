"""Rip the WBAN number out of the ISD station files and add to database

    ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-history.txt
"""

from pyiem.util import get_dbconn


def main():
    """Go"""
    pgconn = get_dbconn("mesosite", user="mesonet")
    cursor = pgconn.cursor()
    xref = {}
    for linenum, line in enumerate(open("isd-history.txt")):
        if linenum < 24:
            continue
        wban = int(line[7:12])
        if wban == 99999:
            continue
        faa = line[51:55]
        if faa.strip() == "":
            continue
        if faa[0] == "K":
            faa = faa[1:]
        if xref.get(faa) is not None and xref[faa] != wban:
            print("!! conflict %s wban: %s old: %s" % (faa, xref[faa], wban))
            del xref[faa]
        xref[faa] = wban
        # country = line[43:45]
        # state = line[48:50]
        cursor.execute(
            """
            SELECT iemid, synop from stations where
            id = %s and network ~* 'ASOS'
        """,
            (faa,),
        )
        if cursor.rowcount != 1:
            continue
        row = cursor.fetchone()
        if row[1] != wban:
            print("%s %s -> %s" % (faa, row[1], wban))
            cursor.execute(
                "UPDATE stations SET synop = %s where iemid = %s",
                (wban, row[0]),
            )
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
