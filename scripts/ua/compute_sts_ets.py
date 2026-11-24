"""Update mesosite with sts and ets"""

from pyiem.database import get_dbconn
from pyiem.network import Table as NetworkTable
from pyiem.util import logger, utc
from tqdm import tqdm

LOG = logger()
OFFLINE_YR = utc().year - 1


def main():
    """Go Main Go"""
    nt = NetworkTable("RAOB", only_online=False)
    pgconn = get_dbconn("raob", rw=False)
    pcursor = pgconn.cursor()
    pgconn2 = get_dbconn("mesosite", rw=True)
    mcursor = pgconn2.cursor()

    progress = tqdm(list(nt.sts.keys()))
    for station in progress:
        progress.set_description(station)
        stations = [station]
        if station.startswith("_"):
            # Magic
            stations = nt.sts[station]["name"].split("--")[1].strip().split()
        pcursor.execute(
            "SELECT min(date(valid)), max(date(valid)), count(*) "
            "from raob_flights WHERE station = ANY(%s)",
            (stations,),
        )
        row = pcursor.fetchone()
        if row is None:
            progress.write(f"{station} returned no data?!?")
            continue
        current_sts = nt.sts[station]["archive_begin"]
        current_ets = nt.sts[station]["archive_end"]
        current_online = nt.sts[station]["online"]
        sts = row[0]
        ets = row[1]
        if sts is None or ets is None:
            progress.write(f"{station} has no valid sts or ets?!?!")
            continue
        if current_sts is None or current_sts != sts:
            progress.write(f"{station} sts {current_sts}->{sts}")
            mcursor.execute(
                "UPDATE stations SET archive_begin = %s where id = %s and "
                "network = 'RAOB'",
                (sts, station),
            )
        if current_ets is None or current_ets != ets:
            # branch one, station is online
            if ets.year >= OFFLINE_YR:
                if current_online and current_ets is None:
                    continue
                newets = None
                online = "t"
            else:
                newets = ets
                online = "f"
            progress.write(
                f"{station} ets {current_ets}->{newets} set online {online}"
            )
            mcursor.execute(
                "UPDATE stations SET archive_end = %s, online = %s "
                "where id = %s and network = 'RAOB'",
                (newets, online, station),
            )

    mcursor.close()
    pgconn2.commit()
    LOG.info("Completed.")


if __name__ == "__main__":
    main()
