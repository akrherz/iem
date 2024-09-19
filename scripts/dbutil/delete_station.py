"""Delete a station and all references to it!"""

import click
from pyiem.database import get_dbconn


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
        "DELETE from station_attributes where iemid = ( "
        "SELECT iemid from stations where id = %s and network = %s)",
        (station, network),
    )
    mcursor.execute(
        "DELETE from stations where id = %s and network = %s",
        (station, network),
    )
    print(f"Deleted {mcursor.rowcount} row(s) from mesosite stations table")


@click.command()
@click.option("--network", required=True, help="Network Identifier")
@click.option("--station", required=True, help="Station Identifier")
def main(network: str, station: str):
    """Go Main Go"""
    iem_pgconn = get_dbconn("iem")
    icursor = iem_pgconn.cursor()
    mesosite_pgconn = get_dbconn("mesosite")
    mcursor = mesosite_pgconn.cursor()
    delete_logic(icursor, mcursor, network, station)
    icursor.close()
    iem_pgconn.commit()
    mcursor.close()
    mesosite_pgconn.commit()


if __name__ == "__main__":
    main()
