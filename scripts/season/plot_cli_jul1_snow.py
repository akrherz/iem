"""Plot CLI snow"""
import datetime

from pandas import read_sql
from pyiem.plot import MapPlot
from pyiem.util import get_dbconnstr


def main():
    """Go Main Go"""
    df = read_sql(
        """
     select station, st_x(geom), st_y(geom), snow_jul1, snow_jul1_normal
     from cli_data c JOIN stations t on (t.id = c.station)
     WHERE c.valid = 'YESTERDAY' and t.network = 'NWSCLI'
     and snow_jul1 is not null and snow_jul1_normal is not null
     and t.id not in ('RAP', 'DVN', 'FGF', 'OAX', 'MPX')
    """,
        get_dbconnstr("iem"),
        index_col="station",
    )
    df["departure"] = df["snow_jul1"] - df["snow_jul1_normal"]
    df["colors"] = df["departure"].apply(
        lambda x: "#ff0000" if x < 0 else "#0000ff"
    )

    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    year = yesterday.year if yesterday.month > 6 else yesterday.year - 1

    mp = MapPlot(
        sector="midwest",
        axisbg="white",
        title="NWS Total Snowfall (inches) thru %s"
        % (yesterday.strftime("%-d %B %Y"),),
        subtitle=("1 July %s - %s")
        % (year, datetime.datetime.today().strftime("%-d %B %Y")),
    )
    mp.plot_values(
        df["st_x"].values,
        df["st_y"].values,
        df["snow_jul1"].values,
        fmt="%.1f",
        labelbuffer=5,
    )
    pqstr = (
        "data ac %s0000 summary/mw_season_snowfall.png "
        "mw_season_snowfall.png png"
    ) % (datetime.datetime.today().strftime("%Y%m%d"),)
    mp.postprocess(view=False, pqstr=pqstr)
    mp.close()

    # Depature
    mp = MapPlot(
        sector="midwest",
        axisbg="white",
        title="NWS Total Snowfall Departure (inches) thru %s"
        % (yesterday.strftime("%-d %B %Y"),),
        subtitle=("1 July %s - %s")
        % (year, datetime.datetime.today().strftime("%-d %B %Y")),
    )
    mp.plot_values(
        df["st_x"].values,
        df["st_y"].values,
        df["departure"].values,
        color=df["colors"].values,
        fmt="%.1f",
        labelbuffer=5,
    )
    pqstr = (
        "data ac %s0000 summary/mw_season_snowfall_departure.png "
        "mw_season_snowfall_departure.png png"
    ) % (datetime.datetime.today().strftime("%Y%m%d"),)
    mp.postprocess(view=False, pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main()
