"""
Migrate IEM Access data to the archive database.

Called from RUN_20MIN.sh
"""
import datetime
import sys

# third party
from pyiem.reference import ISO8601
from pyiem.util import get_dbconnc, get_properties, logger, set_property, utc

LOG = logger()
PROPERTY_NAME = "ot2archive_last"


def dowork(sts, ets):
    """Process between these two timestamps please"""
    # Delete any obs from yesterday
    OTHER, ocursor = get_dbconnc("other")
    IEM, icursor = get_dbconnc("iem")
    # Get obs from Access
    icursor.execute(
        """
        SELECT c.*, t.id from current_log c JOIN stations t on
        (t.iemid = c.iemid) WHERE t.network in ('OT', 'WMO_BUFR_SRF') and
        updated >= %s and updated < %s ORDER by updated ASC
        """,
        (sts, ets),
    )
    if icursor.rowcount == 0:
        LOG.warning("found no results for ts: %s ts2: %s", sts, ets)

    deletes = 0
    inserts = 0
    for row in icursor:
        # delete any previous obs
        ocursor.execute(
            "DELETE from alldata where station = %s and valid = %s",
            (row["id"], row["valid"]),
        )
        deletes += ocursor.rowcount
        args = (
            row["id"],
            row["valid"],
            row["tmpf"],
            row["dwpf"],
            row["drct"],
            row["sknt"],
            row["alti"],
            row["pday"],
            row["gust"],
            row["srad"],
            row["relh"],
            row["skyl1"],
            row["skyl2"],
            row["skyl3"],
            row["skyl4"],
            row["skyc1"],
            row["skyc2"],
            row["skyc3"],
            row["skyc4"],
            row["srad_1h_j"],
        )
        ocursor.execute(
            """
            INSERT into alldata(station, valid, tmpf, dwpf, drct, sknt,
            alti, pday, gust, srad, relh, skyl1, skyl2, skyl3, skyl4,
            skyc1, skyc2, skyc3, skyc4, srad_1h_j) values
            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            args,
        )
        inserts += 1

    LOG.info("%s->%s deletes: %s inserts: %s", sts, ets, deletes, inserts)
    ocursor.close()
    OTHER.commit()


def get_first_updated():
    """Figure out which is the last updated timestamp we ran for."""
    props = get_properties()
    propvalue = props.get(PROPERTY_NAME)
    if propvalue is None:
        LOG.warning("iem property %s is not set, abort!", PROPERTY_NAME)
        sys.exit()

    dt = datetime.datetime.strptime(propvalue, ISO8601)
    return dt.replace(tzinfo=datetime.timezone.utc)


def main():
    """Run for a given 6z to 6z period."""
    last_updated = utc()
    first_updated = get_first_updated()

    dowork(first_updated, last_updated)
    set_property(PROPERTY_NAME, last_updated)


if __name__ == "__main__":
    main()
