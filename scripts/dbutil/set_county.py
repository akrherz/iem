"""Need to set station metadata for county name for a given site."""

from pyiem.util import get_dbconn


def set_county(mcursor2, iemid, ugc, ugcname):
    """set the county"""
    mcursor2.execute(
        "UPDATE stations SET county = %s, ugc_county = %s WHERE iemid = %s",
        (ugcname, ugc, iemid),
    )


def set_zone(mcursor2, iemid, ugc):
    """set the zone"""
    mcursor2.execute(
        "UPDATE stations SET ugc_zone = %s WHERE iemid = %s", (ugc, iemid)
    )


def logic(
    pcursor, mcursor2, ugccode, iemid, station, network, lon, lat, state
):
    """Our logic"""
    giswkt = f"Point({lon} {lat})"
    pcursor.execute(
        """
        SELECT ugc, name from ugcs WHERE
        ST_Contains(geom, ST_GeomFromText(%s,4326))
        and substr(ugc,1,3) = %s and end_ts is null
    """,
        (giswkt, state + ugccode),
    )

    result = False
    if pcursor.rowcount != 1:
        # Okay, so perhaps this site is offshore slightly, lets look for the
        # nearest county
        pcursor.execute(
            """
            SELECT ugc, name,
            ST_Distance(geom, ST_GeomFromText(%s,4326)) as d
            from ugcs WHERE substr(ugc,1,3) = %s and end_ts is null and
            ST_Distance(geom, ST_GeomFromText(%s,4326)) < 2
            ORDER by d ASC LIMIT 1
        """,
            (giswkt, state + ugccode, giswkt),
        )
        if pcursor.rowcount == 1:
            (ugc, ugcname, dist) = pcursor.fetchone()
            print(
                (
                    "OK set_county[%s] ID: %s Net: %s: St: %s "
                    "UGC: %s Dist: %.2f"
                )
                % (ugccode, station, network, state, ugc, dist)
            )
            if ugccode == "C":
                set_county(mcursor2, iemid, ugc, ugcname)
            else:
                set_zone(mcursor2, iemid, ugc)
            result = True
        else:
            print(
                (
                    "FAIL set_county[%s] ID:%s Net:%s St:%s "
                    "Lon:%.4f Lat:%.4f\n"
                    "https://mesonet.agron.iastate.edu/sites/"
                    "site.php?station=%s&network=%s"
                    ""
                )
                % (
                    ugccode,
                    station,
                    network,
                    state,
                    lon,
                    lat,
                    station,
                    network,
                )
            )
            result = False

    else:
        (ugc, ugcname) = pcursor.fetchone()
        print(
            ("OK %s IEMID: %s SID: %s Network: %s to: %s [%s]")
            % (ugccode, iemid, station, network, ugcname, ugc)
        )
        if ugccode == "C":
            set_county(mcursor2, iemid, ugc, ugcname)
        else:
            set_zone(mcursor2, iemid, ugc)
        result = True
    return result


def main():
    """Go Main Go"""
    # Get listing of stations without a county set
    mesosite = get_dbconn("mesosite")
    postgis = get_dbconn("postgis")
    mcursor = mesosite.cursor()
    mcursor2 = mesosite.cursor()
    pcursor = postgis.cursor()
    mcursor.execute(
        """
        SELECT iemid, id, name, network, ST_x(geom), ST_y(geom),
        state from stations WHERE (county is null or ugc_county is null
        or ugc_zone is null) and country = 'US' and state is not null
        and state not in ('PR', 'DC', 'GU', 'PU', 'P1', 'P2', 'P3', 'P4', 'P5')
        ORDER by modified DESC
        """
    )

    failures = 0
    for row in mcursor:
        iemid = row[0]
        station = row[1]
        network = row[3]
        lon = row[4]
        lat = row[5]
        state = row[6]
        if not logic(
            pcursor, mcursor2, "C", iemid, station, network, lon, lat, state
        ):
            failures += 1
        if not logic(
            pcursor, mcursor2, "Z", iemid, station, network, lon, lat, state
        ):
            failures += 1

        if failures > 10:
            break

    mcursor.close()
    mcursor2.close()
    pcursor.close()
    mesosite.commit()


if __name__ == "__main__":
    main()
