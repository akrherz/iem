"""Non US domains, we have no climo inhouse to grid, so we do POR stuff."""

import click
from pyiem.iemre import get_daily_ncname, get_dailyc_ncname
from pyiem.util import ncopen
from tqdm import tqdm


@click.command()
@click.option("--domain", required=True)
def main(domain: str):
    """Go Main Go."""
    climofn = get_dailyc_ncname(domain)
    # 2007-2024 x 7 days is a population of ~140, so hopefully enough
    for doy in tqdm(list(range(365))):
        population = list(range(doy - 3, doy + 4))
        high_tmpk = None
        low_tmpk = None
        p01d = None
        power_swdn = None
        count = 0.0
        for year in range(2007, 2025):
            ncname = get_daily_ncname(year, domain)
            with ncopen(ncname) as nc:
                for _doy in population:
                    count += 1.0
                    if _doy > 364:
                        _doy -= 365
                    if high_tmpk is None:
                        high_tmpk = nc.variables["high_tmpk"][_doy, :]
                        low_tmpk = nc.variables["low_tmpk"][_doy, :]
                        p01d = nc.variables["p01d"][_doy, :]
                        power_swdn = nc.variables["swdn"][_doy, :]
                    else:
                        high_tmpk += nc.variables["high_tmpk"][_doy, :]
                        low_tmpk += nc.variables["low_tmpk"][_doy, :]
                        p01d += nc.variables["p01d"][_doy, :]
                        power_swdn += nc.variables["swdn"][_doy, :]
        with ncopen(climofn, "a") as climonc:
            climonc.variables["high_tmpk"][doy, :] = high_tmpk / count
            climonc.variables["low_tmpk"][doy, :] = low_tmpk / count
            climonc.variables["p01d"][doy, :] = p01d / count
            climonc.variables["swdn"][doy, :] = power_swdn / count
        if doy == 364:
            # Repeat
            with ncopen(climofn, "a") as climonc:
                climonc.variables["high_tmpk"][365, :] = high_tmpk / count
                climonc.variables["low_tmpk"][365, :] = low_tmpk / count
                climonc.variables["p01d"][365, :] = p01d / count
                climonc.variables["swdn"][365, :] = power_swdn / count


if __name__ == "__main__":
    main()
