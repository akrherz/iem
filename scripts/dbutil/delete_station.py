"""Delete a station and all references to it!"""
from __future__ import print_function
import sys

from pyiem.util import get_dbconn


def main(argv):
    """Go Main Go"""
    if len(argv) != 3:
        print("Usage: python remove_realtime.py NETWORK SID")
        return
    network = sys.argv[1]
    station = sys.argv[2]
    iem_pgconn = get_dbconn("iem")
    icursor = iem_pgconn.cursor()
    mesosite_pgconn = get_dbconn("mesosite")
    mcursor = mesosite_pgconn.cursor()
    delete_logic(icursor, mcursor, network, station)
    icursor.close()
    iem_pgconn.commit()
    mcursor.close()
    mesosite_pgconn.commit()


def delete_logic(icursor, mcursor, network, station):
    """Do the work"""
    for table in ["current", "summary", "hourly"]:
        icursor.execute(
            f"DELETE from {table} where iemid = (select iemid from stations "
            "where id = %s and network = %s)",
            (station, network),
        )
        print(
            f"  Removed {icursor.rowcount} rows from IEMAccess table {table}"
        )

    mcursor.execute(
        """
        DELETE from station_attributes where iemid = (
            SELECT iemid from stations where id = %s and network = %s
        )
    """,
        (station, network),
    )
    mcursor.execute(
        """
        DELETE from stations where id = %s and network = %s
    """,
        (station, network),
    )
    print(
        ("Deleted %s row(s) from mesosite database stations table")
        % (mcursor.rowcount,)
    )


if __name__ == "__main__":
    main(sys.argv)
