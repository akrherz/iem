"""
Ingest files provided by NLAE containing flux information
"""
import os
from io import StringIO
import datetime

import pytz
import pandas as pd
from pyiem.observation import Observation
from pyiem.util import get_dbconn, logger, utc, convert_value, c2f

LOG = logger()
BASEDIR = "/mesonet/home/mesonet/ot/ot0005/incoming/Fluxdata"
FILENAMES = {
    "NSTL10": ["Flux10_AF_15.dat", "Anc10_AF_15.dat"],
    "NSTL11": ["Flux11_AF_15.dat", "Anc11_AF_15.dat"],
    "NSTL30FT": ["30ft_15.dat"],
    "NSTLNSPR": ["NSP_Flux_15.dat"],
}

DBCOLS = [
    "station",
    "valid",
    "fc_wpl",
    "le_wpl",
    "hs",
    "tau",
    "u_star",
    "cov_uz_uz",
    "cov_uz_ux",
    "cov_uz_uy",
    "cov_uz_co2",
    "cov_uz_h2o",
    "cov_uz_ts",
    "cov_ux_ux",
    "cov_ux_uy",
    "cov_ux_co2",
    "cov_ux_h2o",
    "cov_ux_ts",
    "cov_uy_uy",
    "cov_uy_co2",
    "cov_uy_h2o",
    "cov_uy_ts",
    "cov_co2_co2",
    "cov_h2o_h2o",
    "cov_ts_ts",
    "ux_avg",
    "uy_avg",
    "uz_avg",
    "co2_avg",
    "h2o_avg",
    "ts_avg",
    "rho_a_avg",
    "press_avg",
    "panel_temp_avg",
    "wnd_dir_compass",
    "wnd_dir_csat3",
    "wnd_spd",
    "rslt_wnd_spd",
    "batt_volt_avg",
    "std_wnd_dir",
    "fc_irga",
    "le_irga",
    "co2_wpl_le",
    "co2_wpl_h",
    "h2o_wpl_le",
    "h2o_wpl_h",
    "h2o_hmp_avg",
    "t_hmp_avg",
    "par_avg",
    "solrad_avg",
    "rain_tot",
    "shf1_avg",
    "shf2_avg",
    "soiltc1_avg",
    "soiltc2_avg",
    "soiltc3_avg",
    "soiltc4_avg",
    "irt_can_avg",
    "irt_cb_avg",
    "incoming_sw",
    "outgoing_sw",
    "incoming_lw_tcor",
    "terrest_lw_tcor",
    "rn_short_avg",
    "rn_long_avg",
    "rn_total_avg",
    "rh_hmp_avg",
    "temps_c1_avg",
    "corrtemp_avg",
    "rn_total_tcor_avg",
    "incoming_lw_avg",
    "terrestrial_lw_avg",
    "wfv1_avg",
    "n_tot",
    "csat_warnings",
    "irga_warnings",
    "del_t_f_tot",
    "track_f_tot",
    "amp_h_f_tot",
    "amp_l_f_tot",
    "chopper_f_tot",
    "detector_f_tot",
    "pll_f_tot",
    "sync_f_tot",
    "agc_avg",
    "solarrad_mv_avg",
    "solarrad_w_avg",
    "par_mv_avg",
    "par_den_avg",
    "surftc_avg",
    "temp_c1_avg",
    "temp_k1_avg",
    "irr_can_corr_avg",
    "irr_body_avg",
    "vwc",
    "ec",
    "t",
    "p",
    "pa",
    "vr",
    "lithium_bv_avg",
    "solarrad_mj_tot",
    "par_tot_tot",
]
DROPCOLS = ["lithium_bv_avg", "utcyear", "fw_avg", "site"]
CONVERT = {
    "timestamp": "valid",
    "incoming_sw_avg": "incoming_sw",
    "outgoing_sw_avg": "outgoing_sw",
    "incoming_lw_tcor_avg": "incoming_lw_tcor",
    "terrest_lw_tcor_avg": "terrest_lw_tcor",
}


def c(v):
    """convert"""
    if v in ["NAN", "-INF", "INF"]:
        return None
    return v


def make_time(string):
    """Convert a time in the file to a datetime"""
    tstamp = datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
    tstamp = tstamp.replace(tzinfo=pytz.FixedOffset(-360))
    return tstamp


def main():
    """Go Main Go"""
    pgconn = get_dbconn("other")
    ipgconn = get_dbconn("iem")
    cursor = pgconn.cursor()

    # Figure out max valid times
    maxts = {}
    cursor.execute(
        "SELECT station, max(valid) from flux_data GROUP by station"
    )
    for row in cursor:
        maxts[row[0]] = row[1]

    processed = 0
    for station, fns in FILENAMES.items():
        if station not in maxts:
            LOG.info("%s has no prior db archive", station)
            maxts[station] = utc(1980, 1, 1)
        dfs = []
        for fn in fns:
            myfn = os.path.join(BASEDIR, str(datetime.date.today().year), fn)
            if not os.path.isfile(myfn):
                LOG.info("missing file: %s", myfn)
                continue
            with open(myfn, encoding="ISO-8859-1") as fh:
                df = pd.read_csv(
                    fh,
                    skiprows=[0, 2, 3],
                    index_col=0,
                    na_values=["NAN"],
                )
            df = df.drop(columns="RECORD")
            if df.empty:
                LOG.info("file: %s has no data", fn)
                continue
            dfs.append(df)
        if not dfs:
            LOG.info("no data for: %s", station)
            continue
        df = dfs[0]
        if len(dfs) > 1:
            df = df.join(dfs[1]).copy()
        # get index back into a column
        df = df.reset_index()
        # lowercase all column names
        df.columns = [x.lower() for x in df.columns]
        df["timestamp"] = df["timestamp"].apply(make_time)
        df = df[df["timestamp"] > maxts[station]].copy()
        if df.empty:
            continue
        df = df.rename(columns=CONVERT)
        # We need a UTC year to allow for the database insert below to work
        df["utcyear"] = df["valid"].dt.tz_convert(pytz.utc).dt.year
        df["station"] = station
        for year, gdf in df.groupby("utcyear"):
            exclude = []
            for colname in gdf.columns:
                if colname not in DBCOLS:
                    exclude.append(colname)
                    if colname not in DROPCOLS:
                        LOG.info("%s has more cols: %s", station, exclude)
            gdf2 = gdf[gdf.columns.difference(exclude)]
            processed += len(gdf2.index)
            output = StringIO()
            gdf2.to_csv(output, sep="\t", header=False, index=False)

            cursor = pgconn.cursor()
            output.seek(0)
            cursor.copy_from(
                output, f"flux{year}", columns=gdf2.columns, null=""
            )
            cursor.close()
            pgconn.commit()
        icursor = ipgconn.cursor()
        for _i, row in df.iterrows():
            iemob = Observation(
                station, "NSTLFLUX", row["valid"].to_pydatetime()
            )
            if "t_hmp_avg" in df.columns:
                iemob.data["tmpf"] = c2f(row["t_hmp_avg"])
            if "wnd_spd" in df.columns:
                iemob.data["sknt"] = convert_value(
                    row["wnd_spd"], "meter / second", "knot"
                )
            if "press_avg" in df.columns:
                iemob.data["pres"] = convert_value(
                    row["press_avg"] * 1000.0, "pascal", "millibar"
                )
            for cvar, ivar in zip(
                ["solarrad_w_avg", "rh_hmp_avg", "wnd_dir_compass"],
                ["srad", "rh", "drct"],
            ):
                if cvar in df.columns:
                    iemob.data[ivar] = row[cvar]
            iemob.save(icursor)
        icursor.close()
        ipgconn.commit()
        LOG.debug("Processed %s rows for %s", processed, station)


if __name__ == "__main__":
    main()
