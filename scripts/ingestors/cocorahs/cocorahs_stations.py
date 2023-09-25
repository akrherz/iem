"""Sync CoCoRaHS station details.

Run from RUN_40_AFTER.sh
"""
import sys

import requests
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger

LOG = logger()


def main(argv):
    """Go Main Go"""
    state = argv[1]
    network = f"{state}COCORAHS"
    nt = NetworkTable(network, only_online=False)
    pgconn = get_dbconn("mesosite")
    mcursor = pgconn.cursor()

    url = (
        "http://data.cocorahs.org/cocorahs/export/exportstations.aspx?"
        f"State={state}&Format=CSV&country=usa"
    )
    try:
        data = (
            requests.get(url, timeout=30).content.decode("ascii").split("\r\n")
        )
    except Exception as exp:
        LOG.exception(exp)
        sys.exit(1)

    # Process Header
    header = {}
    h = data[0].split(",")
    for i, _h in enumerate(h):
        header[_h] = i

    if "StationNumber" not in header:
        sys.exit(0)

    for row in data[1:]:
        cols = row.split(", ")
        if len(cols) < 4:
            continue
        if cols[header["StationStatus"]].strip() == "Closed":
            continue
        sid = cols[header["StationNumber"]]
        name = cols[header["StationName"]].strip().replace("'", " ").strip()
        if name == "":
            name = sid
        cnty = cols[header["County"]].strip().replace("'", " ")
        lat = float(cols[header["Latitude"]].strip())
        lon = float(cols[header["Longitude"]].strip())
        # Always puzzled by this
        if abs(lon - 0) < 0.1 or abs(lat - 0) < 0.1:
            continue
        if sid in nt.sts:
            olat = nt.sts[sid]["lat"]
            olon = nt.sts[sid]["lon"]
            dist = ((olat - lat) ** 2 + (olon - lon) ** 2) ** 0.5
            if dist < 0.01:
                continue
            LOG.info(
                "%s is %.3f distance: %s->%s %s->%s",
                sid,
                dist,
                olon,
                lon,
                olat,
                lat,
            )
            mcursor.execute(
                "UPDATE stations SET geom = ST_Point(%s, %s, 4326), "
                "elevation = -999, ugc_county = null, ugc_zone = null, "
                "ncdc81 = null, climate_site = null, ncei91 = null WHERE "
                "id = %s and network = %s",
                (lon, lat, sid, network),
            )
            if name != nt.sts[sid]["name"]:
                LOG.warning(
                    "Updating %s name '%s' -> '%s'",
                    sid,
                    nt.sts[sid]["name"],
                    name,
                )
                mcursor.execute(
                    "UPDATE stations SET name = %s, plot_name = %s where "
                    "id = %s and network = %s",
                    (name, name, sid, network),
                )
            continue

        LOG.warning(
            "ADD COCORAHS SID:%s Name:%s County:%s %.3f %.3f",
            sid,
            name,
            cnty,
            lat,
            lon,
        )

        mcursor.execute(
            "INSERT into stations(id, synop, name, state, country, network, "
            "online, geom, county, plot_name , metasite) "
            "VALUES (%s, 99999, %s, %s, 'US', %s, 't', "
            "ST_POINT(%s, %s, 4326), %s, %s, 'f')",
            (
                sid,
                name,
                state,
                network,
                lon,
                lat,
                cnty,
                name,
            ),
        )
    mcursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
