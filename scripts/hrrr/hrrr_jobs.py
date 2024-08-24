"""HRRR Reflectivity Jobs.

RUN from RUN_HRRR_REF.sh for previous hour and six hours ago
"""

import subprocess
from datetime import datetime

import click


@click.command()
@click.option("--valid", type=click.DateTime(), required=True)
@click.option("--is-realtime", "rt", is_flag=True)
def main(valid: datetime, rt: bool):
    """Stuff"""
    tstring = f"--valid={valid:%Y-%m-%dT%H:%M:%S}"
    for py in ["dl_hrrrref.py", "plot_ref.py", "hrrr_ref2raster.py"]:
        cmd = ["python", py, tstring]
        if rt:
            cmd.append("--is-realtime")
        subprocess.call(cmd)


if __name__ == "__main__":
    main()
