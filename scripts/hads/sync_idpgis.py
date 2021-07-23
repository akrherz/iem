"""See what metadata IDPGIS has to offer.

Run daily from RUN_2AM.sh
"""

import requests
from pyiem.util import get_dbconn, logger

LOG = logger()
SERVICE = (
    "https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Observations/"
    "ahps_riv_gauges/MapServer/0/query?where=1%3D1&"
    "geometryType=esriGeometryPoint&outFields=PEDTS%2CGaugeLID"
    "&returnGeometry=true&f=json"
)


def get_current(dbconn):
    """Get what we have."""
    current = {}
    cursor = dbconn.cursor()
    cursor.execute(
        "SELECT id, s.iemid, value from "
        "stations s LEFT JOIN station_attributes a "
        "on (s.iemid = a.iemid and a.attr = 'PEDTS') "
        "WHERE s.network ~* 'DCP'"
    )
    for row in cursor:
        current[row[0]] = {"pedts": row[2], "iemid": row[1]}
    cursor.close()
    return current


def get_idp():
    """See what AHPS has."""
    LOG.debug("Fetching %s", SERVICE)
    req = requests.get(SERVICE, timeout=60)
    jobj = req.json()
    idp = {}
    for feat in jobj["features"]:
        attrs = feat["attributes"]
        if attrs["pedts"] is None or attrs["pedts"] == "N/A":
            continue
        idp[attrs["gaugelid"]] = attrs["pedts"]
    return idp


def main():
    """Go Main Go."""
    idp = get_idp()
    with get_dbconn("mesosite") as dbconn:
        current = get_current(dbconn)
        for nwsli, pedts in idp.items():
            if nwsli not in current:
                LOG.info("station %s is unknown to IEM", nwsli)
                continue
            currentval = current[nwsli]["pedts"]
            if currentval == pedts:
                continue
            cursor = dbconn.cursor()
            if currentval is None:
                cursor.execute(
                    "INSERT into station_attributes(iemid, attr, value) "
                    "VALUES (%s, %s, %s)",
                    (current[nwsli]["iemid"], "PEDTS", pedts),
                )
            else:
                cursor.execute(
                    "UPDATE station_attributes SET value = %s WHERE "
                    "iemid = %s and attr = 'PEDTS'",
                    (pedts, current[nwsli]["iemid"]),
                )
            LOG.info("%s PEDTS %s -> %s", nwsli, currentval, pedts)
            cursor.close()
            dbconn.commit()


if __name__ == "__main__":
    main()
