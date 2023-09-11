"""Update mesosite with sts and ets"""

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger
from tqdm import tqdm

LOG = logger()


def main():
    """Go Main Go"""
    nt = NetworkTable("RAOB", only_online=False)
    pgconn = get_dbconn("raob")
    pcursor = pgconn.cursor()
    pgconn2 = get_dbconn("mesosite")
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
        current_sts = nt.sts[station]["archive_begin"]
        current_ets = nt.sts[station]["archive_end"]
        sts = row[0]
        ets = row[1]
        if sts is not None and current_sts is None or current_sts != sts:
            LOG.info("%s sts %s->%s", station, current_sts, sts)
            mcursor.execute(
                "UPDATE stations SET archive_begin = %s where id = %s and "
                "network = 'RAOB'",
                (sts, station),
            )
        if ets is not None and current_ets is None and ets.year < 2018:
            LOG.info("%s ets %s->%s", station, current_ets, ets)
            mcursor.execute(
                "UPDATE stations SET archive_end = %s where id = %s and "
                "network = 'RAOB'",
                (ets, station),
            )

    mcursor.close()
    pgconn2.commit()


if __name__ == "__main__":
    main()
