"""Generate analysis of Peak Wind Gust.

Called from RUN_10MIN.sh
"""

from datetime import datetime

from pyiem.util import web2ldm


def main():
    """Go Main Go"""
    now = datetime.now()

    service = (
        "http://iem.local/plotting/auto/plot/206/t:state::network:WFO"
        f"::wfo:DMX::state:IA::v:max_gust::p:both::day:{now:%Y-%m-%d}::"
        "cmap:gist_stern_r::_cb:1.png"
    )
    pqstr = (
        "plot ac {now:%Y%m%d%H%M} summary/today_gust.png "
        "iowa_wind_gust.png png"
    )
    web2ldm(service, pqstr, md5_from_name=True)


if __name__ == "__main__":
    main()
