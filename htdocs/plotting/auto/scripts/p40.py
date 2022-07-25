"""METAR cloudiness"""
import datetime

import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from pyiem.plot import get_cmap, figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, utc
from pyiem.exceptions import NoDataFound

PDICT = {"sky": "Sky Coverage + Visibility", "vsby": "Just Visibility"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 3600
    desc[
        "description"
    ] = """This chart is an attempted illustration of the
    amount of cloudiness that existed at a METAR site for a given month.
    The chart combines reports of cloud amount and level to provide a visual
    representation of the cloudiness.  Once the METAR site hits a cloud level
    of overcast, it can no longer sense clouds above that level.  So while the
    chart will indicate cloudiness up to the top, it may not have been like
    that in reality.
    """
    today = datetime.date.today()
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(
            type="month",
            name="month",
            label="Select Month:",
            default=today.month,
        ),
        dict(
            type="select",
            options=PDICT,
            name="ptype",
            default="sky",
            label="Available Plot Types",
        ),
        dict(
            type="year",
            name="year",
            label="Select Year:",
            default=today.year,
            min=1970,
        ),
    ]
    return desc


def plot_sky(days, vsby, data, ctx, sts):
    """Sky plot variant."""
    fig = figure(apctx=ctx)
    # vsby plot
    ax = fig.add_axes([0.1, 0.08, 0.8, 0.03])
    ax.set_xticks(np.arange(0, int(days * 24) - 1, 24))
    ax.set_xticklabels(np.arange(1, days + 1))
    ax.set_yticks([])
    cmap = get_cmap("gray")
    cmap.set_bad("white")
    res = ax.imshow(
        vsby,
        aspect="auto",
        extent=[0, days * 24, 0, 1],
        vmin=0,
        cmap=cmap,
        vmax=10,
    )
    cax = fig.add_axes([0.915, 0.08, 0.035, 0.2])
    fig.colorbar(res, cax=cax)
    fig.text(0.02, 0.09, "Visibility\n[miles]", va="center")

    # clouds
    ax = fig.add_axes([0.1, 0.16, 0.8, 0.7])
    ax.set_facecolor("skyblue")
    ax.set_xticks(np.arange(0, int(days * 24) - 1, 24))
    ax.set_xticklabels(np.arange(1, days + 1))

    fig.text(
        0.5,
        0.935,
        f"{ctx['_sname']}:: {sts:%b %Y} "
        "Clouds & Visibility\nbased on ASOS METAR Cloud Amount ",
        ha="center",
        fontsize=14,
    )

    cmap = get_cmap("gray_r")
    cmap.set_bad("white")
    cmap.set_under("skyblue")
    ax.imshow(
        np.flipud(data),
        aspect="auto",
        extent=[0, days * 24, 0, 250],
        cmap=cmap,
        vmin=1,
    )
    ax.set_yticks(range(0, 260, 50))
    ax.set_yticklabels(range(0, 26, 5))
    ax.set_ylabel("Cloud Levels [1000s feet]")
    fig.text(0.45, 0.02, f"Day of {sts:%b %Y} (UTC Timezone)")

    r1 = Rectangle((0, 0), 1, 1, fc="skyblue")
    r2 = Rectangle((0, 0), 1, 1, fc="white")
    r3 = Rectangle((0, 0), 1, 1, fc="k")
    r4 = Rectangle((0, 0), 1, 1, fc="#EEEEEE")

    ax.grid(True)

    ax.legend(
        [r1, r4, r2, r3],
        ["Clear", "Some", "Unknown", "Obscured by Overcast"],
        loc="lower center",
        fontsize=14,
        bbox_to_anchor=(0.5, 0.99),
        fancybox=True,
        shadow=True,
        ncol=4,
    )
    return fig


def plot_vsby(days, vsby, ctx, sts):
    """Sky plot variant."""
    fig = figure(apctx=ctx)

    # need to convert vsby to 2-d
    data = np.ones((100, days * 24)) * -3
    for i in range(days * 24):
        val = vsby[0, i]
        if np.ma.is_masked(val):
            continue
        val = min([int(val * 10), 100])
        data[val:, i] = val / 10.0
        data[:val, i] = -1
    data = np.ma.array(data, mask=np.where(data < -1, True, False))

    # clouds
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax.set_facecolor("skyblue")
    ax.set_xticks(np.arange(1, days * 24 + 1, 24))
    ax.set_xticklabels(np.arange(1, days + 1))

    fig.text(
        0.5,
        0.935,
        f"{ctx['_sname']}:: {sts:%b %Y} "
        "Visibility\nbased on hourly ASOS METAR Visibility Reports",
        ha="center",
        fontsize=14,
    )

    cmap = get_cmap("gray")
    cmap.set_bad("white")
    cmap.set_under("skyblue")
    res = ax.imshow(
        np.flipud(data),
        aspect="auto",
        extent=[0, days * 24, 0, 100],
        cmap=cmap,
        vmin=0,
        vmax=10,
    )
    cax = fig.add_axes([0.915, 0.08, 0.035, 0.2])
    fig.colorbar(res, cax=cax)
    ax.set_yticks(range(0, 101, 10))
    ax.set_yticklabels(range(0, 11, 1))
    ax.set_ylabel("Visibility [miles]")
    fig.text(0.45, 0.02, f"Day of {sts:%b %Y} (UTC Timezone)")

    ax.grid(True)

    return fig


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    year = ctx["year"]
    month = ctx["month"]
    ptype = ctx["ptype"]

    # Extract the range of forecasts for each day for approximately
    # the given month
    sts = utc(year, month, 1, 0, 0)
    ets = (sts + datetime.timedelta(days=35)).replace(day=1)
    days = (ets - sts).days
    data = np.ones((250, days * 24)) * -1
    vsby = np.ones((1, days * 24)) * -1
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            """
            SELECT valid at time zone 'UTC' as valid,
            skyc1, skyc2, skyc3, skyc4, skyl1, skyl2, skyl3, skyl4, vsby,
            extract(epoch from (valid - %s))/3600. as hours
            from alldata where station = %s and valid BETWEEN %s and %s
            and report_type = 3 ORDER by valid ASC
        """,
            conn,
            params=(sts, station, sts, ets),
            index_col=None,
        )

    lookup = {"CLR": 0, "FEW": 25, "SCT": 50, "BKN": 75, "OVC": 100}

    if df.empty:
        raise NoDataFound("No database entries found for station, sorry!")

    for _, row in df.iterrows():
        delta = int(row["hours"] - 1)
        data[:, delta] = 0
        if not np.isnan(row["vsby"]):
            vsby[0, delta] = row["vsby"]
        for i in range(1, 5):
            a = lookup.get(row[f"skyc{i}"], -1)
            if a >= 0:
                skyl = row[f"skyl{i}"]
                if skyl is not None and skyl > 0:
                    skyl = int(skyl / 100)
                    if skyl >= 250:
                        continue
                    data[skyl : skyl + 4, delta] = a
                    data[skyl + 3 :, delta] = min(a, 75)

    data = np.ma.array(data, mask=np.where(data < 0, True, False))
    vsby = np.ma.array(vsby, mask=np.where(vsby < 0, True, False))

    if ptype == "vsby":
        fig = plot_vsby(days, vsby, ctx, sts)
    else:
        fig = plot_sky(days, vsby, data, ctx, sts)

    return fig, df


if __name__ == "__main__":
    plotter(
        dict(
            zstation="RAS", year=2012, month=3, ptype="vsby", network="TX_ASOS"
        )
    )
