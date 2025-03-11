"""Ingest from NCEI IGRA2 data.

At the moment, am unsure how often the upstream data is updated, so no
automation is in place.
"""

import os
import subprocess
import tempfile
from typing import Optional

import click
import httpx
from pyiem.database import get_dbconnc
from pyiem.ncei.igra import process_ytd
from pyiem.reference import igra2icao
from pyiem.util import logger

LOG = logger()


@click.command()
@click.option("--overwrite", is_flag=True, help="Overwrite existing data")
@click.option("--icao", help="Specific ICAO to ingest")
def main(overwrite: bool, icao: Optional[str]):
    """Go Main."""
    pgconn, cursor = get_dbconnc("raob")
    # meh
    cursor.close()
    for ncei_id, _icao in igra2icao.items():
        if icao and icao != _icao:
            continue
        url = (
            "https://www.ncei.noaa.gov/data/"
            "integrated-global-radiosonde-archive/access/data-y2d/"
            f"{ncei_id}-data-beg2021.txt.zip"
        )
        try:
            resp = httpx.get(url, timeout=30)
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


if __name__ == "__main__":
    main()
