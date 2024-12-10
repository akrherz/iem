"""Update mesosite station table station names

HML files provide station names that are likely better than what I manually
hacked into the database previously..."""

import sys

from pyiem.database import get_dbconn
from pyiem.nws.products.hml import parser
from pyiem.reference import nwsli2state

sys.path.insert(0, "../dbutil")
from delete_station import delete_logic  # noqa


def build_stations():
    """Build the cross reference"""
    xref = {}
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor("streamer")
    cursor.execute(
        "SELECT data from products WHERE entered > 'YESTERDAY' "
        "and substr(pil, 1, 3) = 'HML'"
    )
    for row in cursor:
        hml = parser(row[0])
        for _hml in hml.data:
            xref[_hml.station] = _hml.stationname
    return xref


def should_delete_coop(rwcursor, icursor, nwsli):
    """Should this site be moved from COOP to DCP"""
    icursor.execute(
        """SELECT distinct physical_code || duration
    from current_shef WHERE station = %s""",
        (nwsli,),
    )
    codes = [row[0] for row in icursor]
    iscoop = True in [c[2] == "D" for c in codes]
    if iscoop:
        # Leave as is...
        print(" - Site is a COOP, will not delete it")
        return
    network = "%s_COOP" % (nwsli2state[nwsli[3:5]],)
    print(" -> Removing %s %s" % (network, nwsli))
    # remove COOP
    delete_logic(icursor, rwcursor, network, nwsli)


def should_switch_2dcp(rwcursor, icursor, nwsli, iemid):
    """Should this site be moved from COOP to DCP"""
    icursor.execute(
        """SELECT distinct physical_code || duration
    from current_shef WHERE station = %s""",
        (nwsli,),
    )
    codes = [row[0] for row in icursor]
    iscoop = True in [c[2] == "D" for c in codes]
    network = "%s_DCP" % (nwsli2state[nwsli[3:5]],)
    if iscoop:
        print("Site is a COOP, adding DCP...")
        rwcursor.execute(
            """INSERT into stations select id, synop, name,
        state, country, elevation, %s, online, geom, params, county, plot_name,
        climate_site, nwn_id, wfo, archive_end, remote_id,
        modified, spri, tzname, nextval('stations_iemid_seq'::regclass),
        archive_begin, metasite, sigstage_low, sigstage_action,
        sigstage_bankfull,
        sigstage_flood, sigstage_moderate, sigstage_major,
        sigstage_record, ugc_county, ugc_zone, ncdc81, temp24_hour,
        precip24_hour from stations where iemid = %s
        """,
            (network, iemid),
        )
        return
    print(" -> Switching site: %s to network: %s" % (nwsli, network))
    rwcursor.execute(
        "UPDATE stations SET network = %s where iemid = %s", (network, iemid)
    )


def merge(xref):
    """Do some logic here to clean things up!"""
    pgconn = get_dbconn("mesosite", user="mesonet")
    ipgconn = get_dbconn("iem", user="mesonet")
    for nwsli, name_in in xref.items():
        cursor = pgconn.cursor()
        rwcursor = pgconn.cursor()
        icursor = ipgconn.cursor()
        name = name_in[:64]  # database name size limitation
        cursor.execute(
            "SELECT id, name, network, iemid from stations WHERE "
            "id = %s and (network ~* 'COOP' or network ~* 'DCP')",
            (nwsli,),
        )
        if cursor.rowcount == 0:
            print("Unknown station: %s" % (nwsli,))
        elif cursor.rowcount == 1:
            row = cursor.fetchone()
            if row[2].find("DCP") == -1:
                print("Site is listed as only COOP: %s" % (nwsli,))
                should_switch_2dcp(rwcursor, icursor, nwsli, row[3])
            if row[1] != name:
                print(" -> Update %s |%s| -> |%s|" % (nwsli, row[1], name))
                rwcursor.execute(
                    "UPDATE stations SET name = %s WHERE iemid = %s",
                    (name, row[3]),
                )
        elif cursor.rowcount == 2:
            row = cursor.fetchone()
            row2 = cursor.fetchone()
            print(
                "DCP/COOP Duplicate: %s |%s| |%s|" % (nwsli, row[1], row2[1])
            )
            should_delete_coop(rwcursor, icursor, nwsli)
            # Fix DCP name
            for _r in [row, row2]:
                if _r[2].find("DCP") > -1 and _r[1] != name:
                    print(" -> Updating Name to |%s|" % (name,))
                    rwcursor.execute(
                        "UPDATE stations SET name = %s WHERE iemid = %s",
                        (name, _r[3]),
                    )
        else:
            print("Too many rows for: %s" % (nwsli,))

        pgconn.commit()
        rwcursor.close()
        ipgconn.commit()
        icursor.close()

    pgconn.close()
    ipgconn.close()


def main():
    """Go Main Go"""
    xref = build_stations()
    merge(xref)


if __name__ == "__main__":
    main()
