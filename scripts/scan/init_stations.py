"""Pull in what NRCS has for stations."""

import requests
from pyiem.database import get_dbconnc
from pyiem.network import Table as NetworkTable
from pyiem.util import convert_value


def main():
    """Go Main Go."""
    mesosite, mcursor = get_dbconnc("mesosite")
    nt = NetworkTable("SCAN", only_online=False)
    entries = requests.get(
        "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/stations?"
        "activeOnly=true&returnForecastPointMetadata=false&"
        "returnReservoirMetadata=false&returnStationElements=false",
        timeout=30,
    ).json()
    for meta in entries:
        if meta["networkCode"] != "SCAN":
            continue
        station = f"S{int(meta['stationId']):04d}"
        if station in nt.sts:
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
