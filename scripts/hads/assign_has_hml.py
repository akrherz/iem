"""Update metadata to assign HAS_HML property to DCP sites with HML data.

Run from RUN_0Z.sh
"""

import httpx
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.util import logger
from sqlalchemy import text

LOG = logger()


def deal_with_unknown(station: str):
    """Figure out what to do."""
    LOG.info("Unknown station %s logic is running", station)
    # 1. Is this site a COOP?
    with get_sqlalchemy_conn("mesosite") as conn:
        res = conn.execute(
            text("""
            SELECT iemid, network from stations where id = :station
            and network ~* 'COOP'
        """),
            {"station": station},
        )
        if res.rowcount == 1:
            LOG.warning("Station %s is a COOP only?", station)
            return
    # 2. Does this site exist upstream
    try:
        resp = httpx.get(
            f"https://api.water.noaa.gov/nwps/v1/gauges/{station}"
        )
        resp.raise_for_status()
    except Exception:
        LOG.warning("Station %s does not exist in NWPS", station)
        return
    meta = resp.json()
    with get_sqlalchemy_conn("mesosite") as conn:
        state = meta["state"]["abbreviation"]
        res = conn.execute(
            text("""
            insert into stations
            (id, name, state, country, network, online, metasite,
            plot_name, geom)
            values (:station, :name, :state, 'US', :network, 't', 'f', :name,
            ST_Point(:lon, :lat, 4326)) returning iemid
            """),
            {
                "station": station,
                "name": meta["name"],
                "state": state,
                "network": f"{state}_DCP",
                "lon": meta["longitude"],
                "lat": meta["latitude"],
            },
        )
        iemid = res.first()[0]
        LOG.warning("Adding mesosite entry %s for %s", iemid, station)
        conn.execute(
            text("""
            INSERT into station_attributes(iemid, attr, value)
            VALUES (:iemid, 'HAS_HML', '1')
            """),
            {"iemid": iemid},
        )
        conn.commit()


def load_sites() -> pd.DataFrame:
    """Figure out what we have."""
    with get_sqlalchemy_conn("mesosite") as conn:
        df = pd.read_sql(
            text("""
    SELECT id, network from stations s JOIN station_attributes a ON
    (s.iemid = a.iemid) WHERE a.attr = 'HAS_HML'
            """),
            conn,
            index_col="id",
        )
    return df


def load_obs() -> pd.DataFrame:
    """Figure out who has HML data."""
    with get_sqlalchemy_conn("hml") as conn:
        df = pd.read_sql(
            text("""
    select distinct station from hml_observed_data where
    valid > now() - '7 days'::interval
                 """),
            conn,
            index_col="station",
        )
    return df


def main():
    """Go."""
    currentdf = load_sites()
    LOG.info("mesosite has %s sites with HAS_HML", len(currentdf.index))
    obsdf = load_obs()
    LOG.info("hml has %s sites with HML data", len(obsdf.index))
    # Find the difference
    addsites = obsdf.index.difference(currentdf.index)
    LOG.info("Adding %s sites to mesosite", len(addsites))
    if addsites.empty:
        return
    with get_sqlalchemy_conn("mesosite") as conn:
        for station in addsites:
            res = conn.execute(
                text(
                    """
            INSERT into station_attributes(iemid, attr, value)
            SELECT iemid, 'HAS_HML', '1' from stations where id = :station
            and network ~* 'DCP' returning iemid
            """
                ),
                {"station": station},
            )
            if res.rowcount == 0:
                deal_with_unknown(station)
            else:
                LOG.warning("Added HAS_HML for %s to mesosite", station)
        conn.commit()


if __name__ == "__main__":
    main()
