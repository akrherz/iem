"""Center Weather Advisory (CWA) Infographic."""
from datetime import timezone, timedelta

# third party
from geopandas import read_postgis
from pyiem.plot.geoplot import MapPlot
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, utc
from pyiem.exceptions import NoDataFound
from pyiem.reference import Z_OVERLAY2


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["defaults"] = {"_r": "t"}
    desc["cache"] = 3600
    desc["data"] = True
    desc[
        "description"
    ] = """This plot is not meant for interactive use, but a backend for
    CWA plots.
    """
    desc["arguments"] = [
        dict(
            type="networkselect",
            network="CWSU",
            default="ZME",
            name="cwsu",
            label="Select CWSU:",
        ),
        dict(
            type="int",
            default=101,
            name="num",
            label="CWA Number:",
        ),
        dict(
            type="datetime",
            default=f"{utc():%Y/%m/%d %H%M}",
            name="issue",
            label=(
                "UTC Timestamp of the CWA Issuance "
                "(or will search backwards < 1 day):"
            ),
            min="2021/03/01 0000",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    num = ctx["num"]

    # Compute a population estimate
    with get_sqlalchemy_conn("postgis") as conn:
        df = read_postgis(
            "select geom, expire at time zone 'UTC' as expire, "
            "issue at time zone 'UTC' as issue, narrative from cwas "
            "where center = %s and num = %s and "
            "issue > %s and issue <= %s ORDER by issue DESC LIMIT 1",
            conn,
            params=(
                ctx["cwsu"],
                num,
                ctx["issue"] - timedelta(hours=24),
                ctx["issue"],
            ),
            index_col=None,
            geom_col="geom",
        )
    if df.empty:
        raise NoDataFound("CWA Event was not found, sorry.")
    for col in ["issue", "expire"]:
        df[col] = df[col].dt.tz_localize(timezone.utc)
    bounds = df["geom"].total_bounds
    row = df.iloc[0]
    mp = MapPlot(
        apctx=ctx,
        title=(
            f"{ctx['cwsu']} Center Weather Advisory (CWA) #{ctx['num']} "
            f"till {row['expire']:%Y-%m-%d %H:%M} UTC"
        ),
        subtitle=row["narrative"],
        sector="custom",
        west=bounds[0] - 1.2,
        south=bounds[1] - 1.2,
        east=bounds[2] + 1.2,
        north=bounds[3] + 1.2,
    )
    df.to_crs(mp.panels[0].crs).plot(
        ax=mp.panels[0].ax,
        aspect=None,
        facecolor="None",
        edgecolor="k",
        linewidth=4,
        zorder=Z_OVERLAY2,
    )
    mp.drawcities()
    mp.drawcounties()
    radtime = mp.overlay_nexrad(
        df["issue"][0].to_pydatetime(),
        product="N0Q",
        caxpos=[-0.6, 0.05, 0.35, 0.04],  # TODO make this appear nicer
    )
    if radtime is not None:
        mp.fig.text(
            0.65,
            0.02,
            f"RADAR Valid: {radtime:%Y-%m-%d %H:%M} UTC",
            ha="center",
        )

    return mp.fig, df.drop("geom", axis=1)


if __name__ == "__main__":
    plotter({"cwsu": "ZME", "segnum": 102, "date": "2002/03/03"})
