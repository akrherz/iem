"""See if we can get metadata dynmically from NDBC
      var currentstnlat = 29.789;
      var currentstnlng = -90.42;
      var currentstnname = '8762482 - West Bank 1, Bayou Gauche, LA';

      <b>Site elevation:</b> sea level<br />
"""
import requests

from pyiem.reference import nwsli2country, nwsli2state
from pyiem.util import get_dbconn

OUTPUT = open("insert.sql", "w")


def compute_network(nwsli):
    """Figure out the IEM network based on a NWSLI"""
    country = nwsli2country.get(nwsli[3:])
    state = nwsli2state.get(nwsli[3:])
    if country == "US" and state is not None:
        return "US", state, "%s_DCP" % (state,)
    if country != "US" and state is not None:
        return country, state, "%s_%s_DCP" % (country, state)
    print(
        ("Failure to compute state for nwsli: %s [country:%s, state:%s]")
        % (nwsli, country, state)
    )
    return None, None, None


def dowork(nwsli):
    """do work!"""
    uri = "http://www.ndbc.noaa.gov/station_page.php?station=%s" % (nwsli,)
    req = requests.get(uri)
    if req.status_code != 200:
        print("do(%s) failed with status code: %s" % (nwsli, req.status_code))
        return
    html = req.content
    meta = {"elevation": -999}
    for line in html.split("\n"):
        if line.strip().startswith("var currentstn"):
            tokens = line.strip().split()
            meta[tokens[1]] = (
                " ".join(tokens[3:])
                .replace('"', "")
                .replace(";", "")
                .replace("'", "")
            )
        if line.find("<b>Site elevation:</b>") > -1:
            elev = (
                line.strip()
                .replace("<b>Site elevation:</b>", "")
                .replace("<br />", "")
                .replace("above mean sea level", "")
                .strip()
            )
            meta["elevation"] = (
                float(elev.replace("m", "")) if elev != "sea level" else 0
            )
    if "currentstnlng" not in meta:
        print("Failure to scrape: %s" % (nwsli,))
        return
    tokens = meta["currentstnname"].split("-")
    name = "%s - %s" % (tokens[1].strip(), tokens[0].strip())
    country, state, network = compute_network(nwsli)
    if network is None:
        return
    lon = float(meta["currentstnlng"])
    lat = float(meta["currentstnlat"])
    sql = """INSERT into stations(id, name, network, country, state,
    plot_name, elevation, online, metasite, geom) VALUES ('%s', '%s', '%s',
    '%s', '%s', '%s', %s, 't', 'f', 'SRID=4326;POINT(%s %s)');
    """ % (
        nwsli,
        name[:64],
        network,
        country,
        state,
        name[:64],
        meta["elevation"],
        lon,
        lat,
    )
    OUTPUT.write(sql)


def main():
    """Go Main Go!"""
    pgconn = get_dbconn("hads", user="nobody")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT distinct nwsli from unknown where "
        "product ~* 'OSO' ORDER by nwsli"
    )
    for row in cursor:
        dowork(row[0])

    OUTPUT.close()


if __name__ == "__main__":
    main()
