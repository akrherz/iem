"""Generate current plot of Temperature"""

from pyiem.util import utc, web2ldm


def main():
    """GO!"""
    for sector in ["iowa", "conus"]:
        for varname in ["tmpf", "wetbulb"]:
            pqstr = (
                f"plot ac {utc():%Y%m%d%H}00 {sector}_{varname}.png "
                f"{sector}_{varname}_{utc():%H}.png png"
            )
            ss = "state" if sector == "iowa" else sector
            web2ldm(
                f"https://mesonet.agron.iastate.edu/plotting/auto/plot/192/"
                f"t:{ss}::state:IA::v:{varname}::cmap:jet::_cb:1.png",
                pqstr,
            )


if __name__ == "__main__":
    main()
