"""See what metadata IDPGIS has to offer.

Run daily from RUN_2AM.sh
"""

import os
import subprocess

import httpx
from pyiem.database import get_dbconn
from pyiem.reference import nwsli2state
from pyiem.util import logger

LOG = logger()
SERVICE = (
    "https://mapservices.weather.noaa.gov/eventdriven/rest/services/water/"
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


def get_idp() -> dict:
    """See what AHPS has."""
    LOG.info("Fetching %s", SERVICE)
    req = httpx.get(SERVICE, timeout=60)
    if req.status_code != 200:
        LOG.info("Got %s fetching %s", req.status_code, SERVICE)
        return {}
    jobj = req.json()
    idp = {}
    for feat in jobj.get("features", []):
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
        "(%s, %s, %s, %s, 'US', ST_POINT(%s, %s, 4326), "
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
    added = 0
    with get_dbconn("mesosite") as dbconn:
        current = get_current(dbconn)
        for nwsli, attrs in idp.items():
            if nwsli not in current:
                iemid = add_station(dbconn, nwsli, attrs)
                if iemid is None:
                    continue
                added += 1
                LOG.warning("Adding station %s[%s]", nwsli, iemid)
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

    if added > 0:
        LOG.warning("Added %s stations, syncing stations table", added)
        os.chdir("/opt/iem/scripts/dbutil")
        subprocess.call(["sh", "SYNC_STATIONS.sh"])


if __name__ == "__main__":
    main()
