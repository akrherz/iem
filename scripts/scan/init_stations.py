"""Pull in what NRCS has for stations."""

import httpx
from pyiem.database import get_dbconnc
from pyiem.network import Table as NetworkTable
from pyiem.util import convert_value, logger

ATTRNAME = "AWDB.DATA_TIME_ZONE"
LOG = logger()


def main():
    """Go Main Go."""
    mesosite, mcursor = get_dbconnc("mesosite")
    nt = NetworkTable("SCAN", only_online=False)
    entries = httpx.get(
        "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/stations?"
        "activeOnly=true&returnForecastPointMetadata=false&"
        "returnReservoirMetadata=false&returnStationElements=false",
        timeout=30,
    ).json()
    for meta in entries:
        if meta["networkCode"] != "SCAN":
            continue
        station = f"S{int(meta['stationId']):04d}"
        data_time_zone = int(meta["dataTimeZone"])
        if station in nt.sts:
            # Ensure that the data timezone is correct
            curval = int(nt.sts[station]["attributes"].get(ATTRNAME, -99))
            if curval != data_time_zone:
                LOG.info("New %s %s %s", station, ATTRNAME, data_time_zone)
                mcursor.execute(
                    "DELETE from station_attributes where "
                    "iemid = %s and attr = %s",
                    (nt.sts[station]["iemid"], ATTRNAME),
                )
                mcursor.execute(
                    "INSERT into station_attributes(iemid, attr, value) "
                    "VALUES (%s, %s, %s)",
                    (nt.sts[station]["iemid"], ATTRNAME, data_time_zone),
                )

            continue
        print(f"Adding {station} {meta['name']}")
        mcursor.execute(
            "INSERT into stations(id, name, network, online, country, "
            "state, plot_name, elevation, metasite, geom) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, "
            "ST_Point(%s, %s, 4326))",
            (
                station,
                meta["name"],
                "SCAN",
                "t",
                "US",
                meta["stateCode"],
                meta["name"],
                convert_value(meta["elevation"], "foot", "meter"),
                "f",
                meta["longitude"],
                meta["latitude"],
            ),
        )
    mcursor.close()
    mesosite.commit()
    mesosite.close()


if __name__ == "__main__":
    main()
