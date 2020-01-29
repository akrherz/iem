"""Plot 2 day Timeseries from one Turbine"""
from io import BytesIO
import datetime

import pytz
from pandas.io.sql import read_sql
import matplotlib.dates as mdates
from paste.request import parse_formvars
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn


def workflow(turbinename, ts):
    """Go main()"""
    pgconn = get_dbconn("mec", user="mesonet")
    cursor = pgconn.cursor()
    cursor.execute(
        """SELECT unitnumber from turbines
    where turbinename = %s""",
        (turbinename,),
    )
    unitnumber = cursor.fetchone()[0]
    ts1 = ts.strftime("%Y-%m-%d")
    ts2 = (ts + datetime.timedelta(hours=73)).strftime("%Y-%m-%d")
    df = read_sql(
        """
    select coalesce(s.valid, d.valid) as stamp,
    s.power as s_power, s.pitch as s_pitch,
    s.yaw as s_yaw, s.windspeed as s_windspeed,
    d.power as d_power, d.pitch as d_pitch,
    d.yaw as d_yaw, d.windspeed as d_windspeed
    from sampled_data_"""
        + unitnumber
        + """ s FULL OUTER JOIN
    turbine_data_"""
        + unitnumber
        + """ d
    on (d.valid = s.valid)
    WHERE s.valid BETWEEN %s and %s
    ORDER by stamp ASC
    """,
        pgconn,
        params=[ts1, ts2],
    )

    (_, ax) = plt.subplots(4, 1, sharex=True, figsize=(8, 11))

    ax[0].set_title("%s - %s Plot for Turbine: %s" % (ts1, ts2, turbinename))

    ax[0].bar(
        df["stamp"],
        df["s_power"],
        width=1.0 / 1440.0,
        fc="tan",
        ec="tan",
        zorder=1,
        label="1 Minute Sampled",
    )
    data = df[df["d_power"] > -10]
    ax[0].scatter(
        data["stamp"].values,
        data["d_power"].values,
        zorder=2,
        marker="+",
        s=40,
        label="Observations",
    )
    ax[0].set_ylim(-50, 1600)
    ax[0].legend(loc=(0.0, -0.2), ncol=2)
    ax[0].set_ylabel("Power kW")
    ax[0].grid(True)
    # --------------------------------------------------------
    ax[1].bar(
        df["stamp"],
        df["s_pitch"],
        width=1.0 / 1440.0,
        fc="tan",
        ec="tan",
        zorder=1,
    )
    data = df[df["d_pitch"] > -10]
    ax[1].scatter(
        data["stamp"].values,
        data["d_pitch"].values,
        zorder=2,
        marker="+",
        s=40,
    )
    ax[1].set_ylim(bottom=-5)
    ax[1].set_ylabel("Pitch $^\circ$")
    ax[1].grid(True)
    # --------------------------------------------------------
    ax[2].bar(
        df["stamp"],
        df["s_yaw"],
        width=1.0 / 1440.0,
        fc="tan",
        ec="tan",
        zorder=1,
    )
    data = df[df["d_yaw"] > -10]
    ax[2].scatter(
        data["stamp"].values, data["d_yaw"].values, zorder=2, marker="+", s=40
    )
    ax[2].text(0.05, -0.1, "* Uncorrected Yaw", transform=ax[2].transAxes)
    ax[2].set_ylim(0, 360)
    ax[2].set_yticks([0, 90, 180, 270, 360])
    ax[2].set_yticklabels(["N", "E", "S", "W", "N"])
    ax[2].grid(True)
    ax[2].set_ylabel("Turbine Yaw")
    # -----------------------------------------------------------
    ax[3].bar(
        df["stamp"],
        df["s_windspeed"],
        width=1.0 / 1440.0,
        fc="tan",
        ec="tan",
        zorder=1,
    )
    data = df[df["d_windspeed"] > -10]
    ax[3].scatter(
        data["stamp"].values,
        data["d_windspeed"].values,
        zorder=2,
        marker="+",
        s=40,
    )
    ax[3].grid(True)
    ax[3].set_ylabel("Wind Speed mps")
    ax[3].set_ylim(bottom=0)
    ax[3].xaxis.set_major_formatter(
        mdates.DateFormatter(
            "%-I %p\n%-d/%b", tz=pytz.timezone("America/Chicago")
        )
    )


def application(environ, start_response):
    """Go Main Go"""
    headers = [("Content-type", "image/png")]
    start_response("200 OK", headers)
    form = parse_formvars(environ)
    turbinename = form.get("turbinename", "I 050-350")
    ts = datetime.datetime.strptime(form.get("date", "20100401"), "%Y%m%d")
    workflow(turbinename, ts)
    bio = BytesIO()
    plt.savefig(bio)
    return [bio.getvalue()]
