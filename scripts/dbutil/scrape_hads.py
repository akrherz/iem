"""see what station info can be gleaned from HADS website"""
from io import StringIO

import pandas as pd
import requests
from pandas import read_sql
from pyiem.reference import nwsli2country, nwsli2state
from pyiem.util import get_dbconn, get_dbconnstr


def main():
    """Go Main Go"""
    mesosite_pgconn = get_dbconn("mesosite")
    mcursor = mesosite_pgconn.cursor()
    udf = read_sql(
        "select distinct nwsli from unknown where length(nwsli) = 5 "
        "ORDER by nwsli",
        get_dbconnstr("hads"),
        index_col=None,
    )
    udf["stcode"] = udf["nwsli"].str.slice(3, 5)
    for stcode, gdf in udf.groupby("stcode"):
        if stcode not in nwsli2country:
            continue
        country = nwsli2country[stcode]
        state = nwsli2state.get(stcode)
        hadscode = country if country != "US" else state
        if country == "US":
            network = "%s_DCP" % (state,)
        elif country == "CA":
            hadscode = "CN"
            network = "%s_%s_DCP" % (country, state)
        else:
            network = "%s__DCP" % (country,)
        print("Processing country:%s state:%s" % (country, state))
        uri = (
            "https://hads.ncep.noaa.gov/"
            "compressed_defs/%s_dcps_compressed.txt"
        ) % (hadscode,)
        req = requests.get(uri, timeout=60)
        if req.status_code != 200:
            print("uri: %s failed" % (uri,))
            continue
        sio = StringIO()
        sio.write(req.content.decode("ascii", "ignore"))
        sio.seek(0)
        hads = pd.read_csv(sio, sep="|", usecols=range(10), header=None)
        hads.columns = [
            "nesdis_id",
            "nwsli",
            "owner",
            "unsure",
            "hsa",
            "lat",
            "lon",
            "dt",
            "int",
            "location",
        ]
        sio.close()
        if hads.empty or "nwsli" not in hads.columns:
            continue
        for nwsli in gdf["nwsli"]:
            df2 = hads[hads["nwsli"] == nwsli]
            if df2.empty:
                continue
            row = df2.iloc[0]
            tokens = row["lon"].split()
            lon = "%.0f.%04i" % (
                float(tokens[0]),
                (float(tokens[1]) + float(tokens[2]) / 60.0) / 60.0 * 10000.0,
            )
            tokens = row["lat"].split()
            lat = "%.0f.%04i" % (
                float(tokens[0]),
                (float(tokens[1]) + float(tokens[2]) / 60.0) / 60.0 * 10000.0,
            )
            state = state if country in ["US", "CA"] else None
            print(
                (" HADS adding NWSLI:%s network:%s country:%s state:%s")
                % (nwsli, network, country, state)
            )
            mcursor.execute(
                "SELECT online from stations where network = %s and id = %s",
                (network, nwsli),
            )
            if mcursor.rowcount == 1:
                dbrow = mcursor.fetchone()
                print(
                    (" %s already in database online:%s") % (nwsli, dbrow[0])
                )
                continue
            sname = row["location"].strip()[:64].replace(",", " ")
            mcursor.execute(
                """
            INSERT into stations(id, name, network, country, state,
            plot_name, elevation, online, metasite, geom)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 't', 'f',
            ST_POINT(%s, %s, 4326));
            """,
                (
                    nwsli,
                    sname,
                    network,
                    country,
                    state,
                    sname,
                    -999,
                    float(lon),
                    float(lat),
                ),
            )
    mcursor.close()
    mesosite_pgconn.commit()


if __name__ == "__main__":
    main()
