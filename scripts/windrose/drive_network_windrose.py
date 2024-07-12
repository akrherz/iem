"""Generate a windrose for each site in the specified network..."""

import subprocess

import click
from pyiem.network import Table as NetworkTable
from pyiem.util import logger

LOG = logger()


@click.command()
@click.option("--network", required=True, help="Network Identifier")
@click.option(
    "--everything", is_flag=True, help="Generate for offline sites too"
)
def main(network, everything):
    """Go Main"""
    nt = NetworkTable(network, only_online=not everything)
    for sid in nt.sts:
        LOG.info("calling make_windrose.py network: %s sid: %s", network, sid)
        subprocess.call(
            [
                "python",
                "make_windrose.py",
                "--network",
                network,
                "--station",
                sid,
            ]
        )


if __name__ == "__main__":
    main()
