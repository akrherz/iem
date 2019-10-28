""" Get the time of ob set in Harry's file"""
from __future__ import print_function
import sys

from pyiem.util import get_dbconn


def main(argv):
    """Go Main Go"""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()

    year = argv[1]
    month = argv[2]

    stconv = {
        "IA6199": "IA6200",  # Oelwein
        "IA3288": "IA3290",  # Glenwood
        "IA4963": "IA8266",  # Lowden becomes Tipton
        "IA7892": "IA4049",  # Stanley becomes Independence
        "IA0214": "IA0213",  # Anamosa
        "IA2041": "IA3980",  # Dakota City becomes Humboldt
    }

    temp_val = None
    prec_val = None
    for line in open(
        "/mesonet/data/harry/%s/SCIA%s%s.txt" % (year, year[2:], month)
    ):
        tokens = line.strip().split(",")
        if len(tokens) < 5:
            continue
        if "".join(tokens) == "":
            continue
        if "".join(tokens[:5]) == "":
            temp_val = tokens[8] if tokens[8] != "24" else "0"
            prec_val = tokens[10] if tokens[10] != "24" else "0"
            continue
        if len(tokens[0]) >= 3 and temp_val is not None:
            dbid = "IA%04i" % (int(tokens[0]),)
            dbid = stconv.get(dbid, dbid)
            print("%s T:%s P:%s" % (dbid, temp_val, prec_val))
            cursor.execute(
                """UPDATE stations SET temp24_hour = %s,
            precip24_hour = %s WHERE id = %s and network = 'IACLIMATE'
            """,
                (
                    temp_val if temp_val != "" else None,
                    prec_val if prec_val != "" else None,
                    dbid,
                ),
            )
            if cursor.rowcount == 0:
                print("No UPDATE! %s" % (dbid,))
            temp_val = None
            prec_val = None

    cursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main(sys.argv)
