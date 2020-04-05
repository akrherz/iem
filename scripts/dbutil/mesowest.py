"""Review mesowest station file for differences"""
import os
import pandas as pd
import requests


def cache_file():
    """Cache the upstream"""
    localfn = "/mesonet/tmp/mesowest_csv.tbl"
    if os.path.isfile(localfn):
        return
    req = requests.get("http://mesowest.utah.edu/data/mesowest_csv.tbl")
    with open(localfn, "wb") as fh:
        fh.write(req.content)


def main():
    """Go Main Go"""
    cache_file()
    fh = open("insert.sql", "w")
    df = pd.read_csv("/mesonet/tmp/mesowest_csv.tbl")
    # copy paste from /DCP/tomb.phtml
    for line in open("/tmp/tomb.txt"):
        nwsli = line.split()[0]
        if nwsli not in df["primary id"].values:
            continue
        df2 = df[df["primary id"] == nwsli]
        row = df2.iloc[0]
        sql = """INSERT into stations(id, name, network, country, state,
    plot_name, elevation, online, metasite, geom) VALUES ('%s', '%s', '%s',
    '%s', '%s', '%s', %s, 't', 'f', 'SRID=4326;POINT(%s %s)');
    """ % (
            nwsli,
            row["station name"],
            row["state"] + "_DCP",
            row["country"],
            row["state"],
            row["station name"],
            row["elevation"],
            row["longitude"],
            row["latitude"],
        )
        fh.write(sql)
        print(nwsli)

    fh.close()


if __name__ == "__main__":
    main()
