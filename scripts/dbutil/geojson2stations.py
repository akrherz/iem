"""One off"""
import requests
from pyiem.reference import nwsli2country, nwsli2state
from pyiem.datatypes import distance


def main():
    """Go Main Go"""
    fh = open("insert.sql", "w")

    req = requests.get("http://www.weather.gov/source/aprfc/nrcs_swe.json")
    j = req.json()
    for feature in j["features"]:
        nwsli = feature["properties"]["lid"]
        name = feature["properties"]["name"]
        elev = distance(float(feature["properties"]["elev"]), "FT").value("M")
        lon, lat = feature["geometry"]["coordinates"]
        country = nwsli2country.get(nwsli[3:])
        state = nwsli2state.get(nwsli[3:])
        network = "%s_DCP" % (state,)

        sql = """INSERT into stations(id, name, network, country, state,
        plot_name, elevation, online, metasite, geom) VALUES ('%s', '%s', '%s',
        '%s', '%s', '%s', %s, 't', 'f', 'SRID=4326;POINT(%s %s)');
        """ % (
            nwsli,
            name,
            network,
            country,
            state,
            name,
            float(elev),
            float(lon),
            float(lat),
        )
        fh.write(sql)
    fh.close()


if __name__ == "__main__":
    main()
