"""See what metadata IDPGIS has to offer.

Run daily from RUN_2AM.sh
"""

import requests
from pyiem.reference import nwsli2state
from pyiem.util import get_dbconn, logger

LOG = logger()
SERVICE = (
    "https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Observations/"
    "ahps_riv_gauges/MapServer/0/query?where=1%3D1&"
    "geometryType=esriGeometryPoint&"
    "outFields=PEDTS%2CGaugeLID%2CLocation%2CState&returnGeometry=true&f=json"
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
        attrs["lon"] = feat["geometry"]["x"]
        attrs["lat"] = feat["geometry"]["y"]
        idp[attrs["gaugelid"]] = attrs
    return idp


def add_station(dbconn, nwsli, attrs):
    """Add the station."""
    if len(nwsli) != 5 or nwsli2state.get(nwsli[-2:]) != attrs["state"]:
        LOG.info("Skipping %s as un-rectified metadata", nwsli)
        return None
    cursor = dbconn.cursor()
    cursor.execute(
        "INSERT into stations(id, name, plot_name, state, country, geom, "
        "network, online, metasite) VALUES "
        "(%s, %s, %s, %s, 'US', 'SRID=4326;POINT(%s %s)', "
        "%s, %s, %s) RETURNING iemid",
        (
            nwsli,
            attrs["location"],
            attrs["location"],
            attrs["state"],
            attrs["lon"],
            attrs["lat"],
            f"{attrs['state']}_DCP",
            True,
            False,
        ),
    )
    iemid = cursor.fetchone()[0]
    cursor.close()
    dbconn.commit()
    return iemid


def main():
    """Go Main Go."""
    idp = get_idp()
    with get_dbconn("mesosite") as dbconn:
        current = get_current(dbconn)
        for nwsli, attrs in idp.items():
            if nwsli not in current:
                iemid = add_station(dbconn, nwsli, attrs)
                if iemid is None:
                    continue
                LOG.info("Adding station %s[%s]", nwsli, iemid)
                current[nwsli] = {"pedts": "", "iemid": iemid}
            currentval = current[nwsli]["pedts"]
            if attrs["pedts"] is None or attrs["pedts"] == "N/A":
                continue
            if currentval == attrs["pedts"]:
                continue
            cursor = dbconn.cursor()
            if currentval is None:
                cursor.execute(
                    "INSERT into station_attributes(iemid, attr, value) "
                    "VALUES (%s, %s, %s)",
                    (current[nwsli]["iemid"], "PEDTS", attrs["pedts"]),
                )
            else:
                cursor.execute(
                    "UPDATE station_attributes SET value = %s WHERE "
                    "iemid = %s and attr = 'PEDTS'",
                    (attrs["pedts"], current[nwsli]["iemid"]),
                )
            LOG.info("%s PEDTS %s -> %s", nwsli, currentval, attrs["pedts"])
            cursor.close()
            dbconn.commit()


if __name__ == "__main__":
    main()
