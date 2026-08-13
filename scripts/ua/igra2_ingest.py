"""Ingest from NCEI IGRA2 data.

Observation seems to indicate that the archive updates every Sunday, so we
run once per week from RUN_2AM.sh on Mondays.
"""

import os
import subprocess
import tempfile
from datetime import date

import click
import requests
from pyiem.database import get_dbconnc
from pyiem.ncei.igra import process_ytd
from pyiem.reference import igra2icao
from pyiem.util import logger

LOG = logger()


@click.command()
@click.option("--overwrite", is_flag=True, help="Overwrite existing data")
@click.option("--icao", help="Specific ICAO to ingest")
@click.option("--por", is_flag=True, help="Ingest the Period of Record.")
def main(overwrite: bool, icao: str | None, por: bool):
    """Go Main."""
    pgconn, cursor = get_dbconnc("raob")
    # meh
    cursor.close()
    for ncei_id, _icao in igra2icao.items():
        if icao and icao != _icao:
            continue
        beg = f"-beg{date.today().year}" if not por else ""
        url = (
            "https://www.ncei.noaa.gov/data/"
            "integrated-global-radiosonde-archive/access/"
            f"data-{'por' if por else 'y2d'}/"
            f"{ncei_id}-data{beg}.txt.zip"
        )
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
        except Exception as exp:
            LOG.info("Failed to fetch %s: %s", url, exp)
            continue
        with tempfile.NamedTemporaryFile(
            "wb", delete=False, suffix=".zip"
        ) as tmp:
            tmp.write(resp.content)
        # Unzip the file
        subprocess.call(
            [
                "unzip",
                "-o",
                "-q",
                tmp.name,
                "-d",
                os.path.dirname(tmp.name),
            ]
        )
        fn = f"/tmp/{ncei_id}-data.txt"
        for sounding in process_ytd(fn):
            cursor = pgconn.cursor()
            sounding.sql(cursor, overwrite=overwrite)
            cursor.close()
            pgconn.commit()
        os.unlink(fn)
        os.unlink(tmp.name)


if __name__ == "__main__":
    main()
