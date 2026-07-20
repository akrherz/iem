"""HRRR Reflectivity Jobs.

RUN from RUN_HRRR_REF.sh for previous hour and six hours ago
"""

import subprocess
import sys
import time
from datetime import datetime

import click
from pyiem.util import logger

LOG = logger()


@click.command()
@click.option("--valid", type=click.DateTime(), required=True)
@click.option("--is-realtime", "rt", is_flag=True)
def main(valid: datetime, rt: bool):
    """Stuff"""
    # The extended HRRR jobs take more time to finish, so pre-emptively sleep
    if rt and valid.hour % 6 == 0:
        LOG.info("Pre-emptively sleeping 20 minutes for RT HR%6")
        time.sleep(20 * 60)
    tstring = f"--valid={valid:%Y-%m-%dT%H:%M:%S}"
    for py in ["dl_hrrrref.py", "plot_ref.py", "hrrr_ref2raster.py"]:
        cmd = ["python", py, tstring]
        if rt:
            cmd.append("--is-realtime")
        # Abort processing if any of the subprocesses fail
        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            LOG.warning("Aborting as %s exited %s", py, result.returncode)
            sys.exit(1)


if __name__ == "__main__":
    main()
