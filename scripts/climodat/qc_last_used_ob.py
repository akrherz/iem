"""Report any climodat sites without recent observations."""
# stdlib
import datetime

# Third Party
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, logger

LOG = logger()
FLOOR = datetime.date.today() - datetime.timedelta(days=365)


def remove_track(iemid):
    """Cull the defunct tracks."""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute(
        "DELETE from station_attributes where iemid = %s and "
        "attr = 'TRACKS_STATION'",
        (iemid,),
    )
    cursor.close()
    pgconn.commit()


def check_last(station, row):
    """Do the work."""
    trackstation, tracknetwork = row["tracks"].split("|")
    df = read_sql(
        "SELECT max(day) from summary s JOIN stations t on "
        "(s.iemid = t.iemid) WHERE t.id = %s and t.network = %s and "
        "s.day > %s and (s.max_tmpf is not null or "
        "s.pday is not null)",
        get_dbconn("iem"),
        index_col=None,
        params=(trackstation, tracknetwork, FLOOR),
    )
    lastdate = df.iloc[0]["max"]
    if lastdate is not None:
        return
    LOG.info(
        "%s %s %.2fE %.2fN tracks non-reporting %s[%s], removing track",
        station,
        row["name"],
        row["lon"],
        row["lat"],
        trackstation,
        tracknetwork,
    )
    remove_track(row["iemid"])


def set_offline(iemid):
    """Set the station to being offline."""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute(
        "UPDATE stations SET online = 'f', archive_end = 'TODAY' WHERE "
        "iemid = %s",
        (iemid,),
    )
    cursor.close()
    pgconn.commit()


def main():
    """Go Main Go."""
    sdf = read_sql(
        """
        with locs as (
            select s.iemid, id, network, value from stations s LEFT
            JOIN station_attributes a on (s.iemid = a.iemid and
            a.attr = 'TRACKS_STATION'))
        select s.id, s.iemid, s.network, st_x(geom) as lon, st_y(geom) as lat,
        s.name, l.value as tracks from stations S LEFT JOIN locs l on
        (s.iemid = l.iemid) WHERE s.network ~* 'CLIMATE' and
        substr(s.id, 3, 4) != '0000' and
        substr(s.id, 3, 1) != 'C' ORDER by s.id ASC
        """,
        get_dbconn("mesosite"),
        index_col="id",
    )
    for station, row in sdf.iterrows():
        if row["tracks"] is None:
            LOG.info("%s tracks no station, setting offline.", station)
            set_offline(row["iemid"])
            continue
        check_last(station, row)


if __name__ == "__main__":
    main()
