"""Generate analysis of visibility."""

from pyiem.util import utc, web2ldm


def main():
    """GO!"""
    pqstr = (
        f"plot ac {utc():%Y%m%d%H}00 iowa_vsby.png "
        f"iowa_vsby_{utc():%H}.png png"
    )
    web2ldm(
        "https://mesonet.agron.iastate.edu/plotting/auto/plot/192/"
        "t:state::state:IA::v:vsby::cmap:gray::_cb:1.png",
        pqstr,
    )


if __name__ == "__main__":
    main()
