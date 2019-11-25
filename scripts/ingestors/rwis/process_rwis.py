"""Process the IDOT RWIS Data files"""
from __future__ import print_function
import datetime
import os
import sys
import smtplib
import ftplib
import subprocess
from email.mime.text import MIMEText

import pandas as pd
import pytz
import numpy as np
from metpy.units import units
import metpy.calc as mcalc
from pyiem.tracker import TrackerEngine
from pyiem.datatypes import temperature, speed
from pyiem.network import Table as NetworkTable
from pyiem.observation import Observation
from pyiem import util

GTS = sys.argv[1]
NT = NetworkTable("IA_RWIS")
IEM = util.get_dbconn("iem")
PORTFOLIO = util.get_dbconn("portfolio")
INCOMING = "/mesonet/data/incoming/rwis"
RWIS2METAR = {
    "00": "XADA",
    "01": "XALG",
    "02": "XATN",
    "03": "XALT",
    "04": "XAME",
    "05": "XANK",
    "06": "XAVO",
    "07": "XBUR",
    "08": "XCAR",
    "09": "XCDR",
    "10": "XCID",
    "11": "XCEN",
    "12": "XCOU",
    "13": "XCRE",
    "14": "XDAV",
    "15": "XDEC",
    "16": "XDSM",
    "17": "XDES",
    "18": "XDST",
    "19": "XDEW",
    "20": "XDUB",
    "21": "XFOD",
    "22": "XGRI",
    "23": "XIAC",
    "24": "XIOW",
    "25": "XJEF",
    "26": "XLEO",
    "27": "XMAN",
    "28": "XMAQ",
    "29": "XMAR",
    "30": "XMCW",
    "31": "XMIS",
    "32": "XMOU",
    "33": "XNEW",
    "34": "XONA",
    "35": "XOSC",
    "36": "XOTT",
    "37": "XPEL",
    "38": "XRED",
    "39": "XSID",
    "40": "XSIG",
    "41": "XSIO",
    "42": "XSPE",
    "43": "XSTO",
    "44": "XTIP",
    "45": "XURB",
    "46": "XWAT",
    "47": "XWIL",
    "48": "XWBG",
    "49": "XHAN",
    "50": "XSBI",
    "51": "XIGI",
    "52": "XCRI",
    "53": "XCFI",
    "54": "XSYI",
    "55": "XBFI",
    "56": "XDYI",
    "57": "XTMI",
    "58": "XPFI",
    "59": "XCTI",
    "60": "XDNI",
    "61": "XQCI",
    "62": "XSMI",
    "63": "XRWI",
    "64": "XETI",
    "65": "XCCI",
    "66": "XKSI",
    "67": "XKNI",
    "68": "XCMI",
    "69": "XRGI",
    "70": "XKYI",
    "72": "XCTI",
}

KNOWN_UNKNOWNS = []


def get_nwsli(rpuid):
    """Lookup a rpuid and return the NWSLI"""
    rpuid = int(rpuid)
    for sid in NT.sts:
        if NT.sts[sid]["remote_id"] == rpuid:
            return sid
    return None


def get_temp(val):
    """Attempt to convert a RWIS temperature into F"""
    if val in ["", 32767]:
        return None
    return temperature(val / 100.0, "C").value("F")


def get_speed(val):
    """ Convert a speed value """
    if val in ["", 255]:
        return None
    return speed(val, "KMH").value("KT")


def merge(atmos, surface):
    """Create a dictionary of data based on these two dataframes

    Args:
      atmos (DataFrame): atmospherics
      surface (DataFrame): surface data

    Returns:
      dictionary of values
    """
    data = {}
    # Do what we can with the atmospheric data
    for _, row in atmos.iterrows():
        nwsli = get_nwsli(row["Rpuid"])
        if nwsli is None:
            if int(row["Rpuid"]) not in KNOWN_UNKNOWNS:
                print(
                    ("process_rwis: Unknown Rpuid: %s in atmos" "")
                    % (row["Rpuid"],)
                )
            continue
        if nwsli not in data:
            data[nwsli] = {}
        # Timestamp
        ts = datetime.datetime.strptime(row["DtTm"], "%m/%d/%y %H:%M")
        data[nwsli]["valid"] = ts.replace(tzinfo=pytz.UTC)
        data[nwsli]["tmpf"] = get_temp(row["AirTemp"])
        data[nwsli]["dwpf"] = get_temp(row["Dewpoint"])
        if data[nwsli]["tmpf"] is not None and data[nwsli]["dwpf"] is not None:
            data[nwsli]["relh"] = (
                mcalc.relative_humidity_from_dewpoint(
                    data[nwsli]["tmpf"] * units("degF"),
                    data[nwsli]["dwpf"] * units("degF"),
                ).magnitude
                * 100.0
            )
        # Rh is unused
        data[nwsli]["sknt"] = get_speed(row["SpdAvg"])
        data[nwsli]["gust"] = get_speed(row["SpdGust"])
        if row["DirMin"] not in ["", 32767, np.nan]:
            data[nwsli]["drct"] = row["DirMin"]
        # DirMax is unused
        # Pressure is not reported
        # PcIntens
        # PcType
        # PcRate
        if row["PcAccum"] not in ["", -1, 32767, np.nan]:
            data[nwsli]["pday"] = row["PcAccum"] * 0.00098425
        if row["Visibility"] not in ["", -1, 32767, np.nan]:
            data[nwsli]["vsby"] = row["Visibility"] / 1609.344

    # Do what we can with the surface data
    for _, row in surface.iterrows():
        nwsli = get_nwsli(row["Rpuid"])
        if nwsli is None:
            if int(row["Rpuid"]) not in KNOWN_UNKNOWNS:
                print(
                    ("process_rwis: Unknown Rpuid: %s in sfc" "")
                    % (row["Rpuid"],)
                )
            continue
        ts = datetime.datetime.strptime(row["DtTm"], "%m/%d/%y %H:%M")
        ts = ts.replace(tzinfo=pytz.UTC)
        if nwsli not in data:
            data[nwsli] = {"valid": ts}
        sensorid = int(row["Senid"])
        key = "sfvalid%s" % (sensorid,)
        data[nwsli][key] = ts
        key = "scond%s" % (sensorid,)
        data[nwsli][key] = row["sfcond"]
        # sftemp                   -150
        key = "tsf%s" % (sensorid,)
        data[nwsli][key] = get_temp(row["sftemp"])
        # frztemp                 32767
        # chemfactor                  0
        # chempct                   101
        # depth                   32767
        # icepct                    101
        # subsftemp                 NaN
        key = "tsub%s" % (sensorid,)
        data[nwsli][key] = get_temp(row["subsftemp"])
        # waterlevel                NaN
        # Unnamed: 13               NaN
        # Unnamed: 14               NaN

    return data


def do_windalerts(obs):
    """Iterate through the obs and do wind alerts where appropriate"""
    for sid in obs:
        # Problem sites with lightning issues
        if sid in [
            "RBFI4",
            "RTMI4",
            "RWII4",
            "RCAI4",
            "RDYI4",
            "RDNI4",
            "RCDI4",
            "RCII4",
            "RCLI4",
            "VCTI4",
            "RGAI4",
            "RAVI4",
        ]:
            continue
        ob = obs[sid]
        # screening
        if ob.get("gust") is None or ob["gust"] < 40:
            continue
        if np.isnan(ob["gust"]):
            continue
        smph = speed(ob["gust"], "KT").value("MPH")
        if smph < 50:
            continue
        if smph > 100:
            print(
                ("process_rwis did not relay gust %.1f MPH from %s" "")
                % (smph, sid)
            )
            continue
        # Use a hacky tmp file to denote a wind alert that was sent
        fn = "/tmp/iarwis.%s.%s" % (sid, ob["valid"].strftime("%Y%m%d%H%M"))
        if os.path.isfile(fn):
            continue
        o = open(fn, "w")
        o.write(" ")
        o.close()
        lts = ob["valid"].astimezone(pytz.timezone("America/Chicago"))
        stname = NT.sts[sid]["name"]
        msg = (
            "At %s, a wind gust of %.1f mph (%.1f kts) was recorded "
            "at the %s (%s) Iowa RWIS station"
            ""
        ) % (lts.strftime("%I:%M %p %d %b %Y"), smph, ob["gust"], stname, sid)
        mt = MIMEText(msg)
        mt["From"] = "akrherz@iastate.edu"
        # mt['To'] = 'akrherz@iastate.edu'
        mt["To"] = "iarwis-alert@mesonet.agron.iastate.edu"
        mt["Subject"] = "Iowa RWIS Wind Gust %.0f mph %s" % (smph, stname)
        s = smtplib.SMTP("mailhub.iastate.edu")
        s.sendmail(mt["From"], [mt["To"]], mt.as_string())
        s.quit()


def do_iemtracker(obs):
    """Iterate over the obs and do IEM Tracker related activities """
    threshold = datetime.datetime.utcnow() - datetime.timedelta(hours=3)
    threshold = threshold.replace(tzinfo=pytz.UTC)

    tracker = TrackerEngine(IEM.cursor(), PORTFOLIO.cursor())
    tracker.process_network(obs, "iarwis", NT, threshold)
    tracker.send_emails()
    IEM.commit()
    PORTFOLIO.commit()


def METARtemp(val):
    """convert temp to METAR"""
    f_temp = float(val)
    i_temp = int(round(f_temp, 0))
    f1_temp = int(round(f_temp * 10.0, 0))
    if i_temp < 0:
        i_temp = 0 - i_temp
        m_temp = "M%02i" % (i_temp,)
    else:
        m_temp = "%02i" % (i_temp,)

    if f1_temp < 0:
        t_temp = "1%03i" % (0 - f1_temp,)
    else:
        t_temp = "0%03i" % (f1_temp,)

    return m_temp, t_temp


def METARwind(sknt, drct, gust):
    """convert to METAR"""
    s = ""
    d5 = drct
    if str(d5)[-1] == "5":
        d5 -= 5
    s += "%03.0f%02.0f" % (d5, sknt)
    if gust is not None:
        s += "G%02.0f" % (gust,)
    s += "KT"
    return s


def gen_metars(obs, filename, convids=False):
    """Create METAR Data files

    Args:
      obs (list): list of dictionaries with obs in them
      filename (str): filename to write data to
      convids (bool): should we use special logic for ID conversion

    """
    mtime = datetime.datetime.utcnow().strftime("%d%H%M")
    thres = datetime.datetime.utcnow() - datetime.timedelta(hours=3)
    thres = thres.replace(tzinfo=pytz.UTC)
    fp = open(filename, "w")
    fp.write("\001\015\015\012001\n")
    fp.write("SAUS43 KDMX %s\015\015\012METAR\015\015\012" % (mtime,))
    for sid in obs:
        ob = obs[sid]
        if ob["valid"] < thres:
            continue
        if sid in ["RIOI4", "ROSI4", "RSMI4", "RMCI4"]:
            continue
        metarid = sid[:4]
        remoteid = NT.sts[sid]["remote_id"]
        if convids:
            metarid = RWIS2METAR.get("%02i" % (remoteid,), "XXXX")
        temptxt = ""
        t_temptxt = ""
        windtxt = ""
        if ob.get("sknt") is not None and ob.get("drct") is not None:
            windtxt = METARwind(ob["sknt"], ob["drct"], ob.get("gust"))
        if obs.get("tmpf") is not None and obs.get("dwpf") is not None:
            m_tmpc, t_tmpc = METARtemp(temperature(ob["tmpf"], "F").value("C"))
            m_dwpc, t_dwpc = METARtemp(temperature(ob["dwpf"], "F").value("C"))
            temptxt = "%s/%s" % (m_tmpc, m_dwpc)
            t_temptxt = "T%s%s " % (t_tmpc, t_dwpc)
        fp.write(
            ("%s %s %s %s RMK AO2 %s%s\015\015\012" "")
            % (
                metarid,
                ob["valid"].strftime("%d%H%MZ"),
                windtxt,
                temptxt,
                t_temptxt,
                "=",
            )
        )

    fp.write("\015\015\012\003")
    fp.close()


def update_iemaccess(obs):
    """Update the IEMAccess database"""
    icursor = IEM.cursor()
    for sid in obs:
        ob = obs[sid]
        iemob = Observation(sid, "IA_RWIS", ob["valid"])
        for varname in [
            "tmpf",
            "dwpf",
            "drct",
            "sknt",
            "gust",
            "vsby",
            "pday",
            "tsf0",
            "tsf1",
            "tsf2",
            "tsf3",
            "scond0",
            "scond1",
            "scond2",
            "scond3",
            "relh",
        ]:
            # Don't insert NaN values into iemaccess
            thisval = ob.get(varname)
            if thisval is None:
                continue
            # strings fail the isnan check
            if isinstance(thisval, str):
                iemob.data[varname] = ob.get(varname)
            elif not np.isnan(thisval):
                iemob.data[varname] = ob.get(varname)
        for varname in ["tsub0", "tsub1", "tsub2", "tsub3"]:
            if ob.get(varname) is not None:
                iemob.data["rwis_subf"] = ob.get(varname)
                break
        iemob.save(icursor)
    icursor.close()
    IEM.commit()


def fetch_files():
    """Download the files we need"""
    props = util.get_properties()
    # get atmosfn
    atmosfn = "%s/rwis.txt" % (INCOMING,)
    try:
        ftp = ftplib.FTP("165.206.203.34")
    except TimeoutError:
        print("process_rwis FTP Server Timeout")
        sys.exit()
    ftp.login("rwis", props["rwis_ftp_password"])
    ftp.retrbinary("RETR ExpApAirData.txt", open(atmosfn, "wb").write)
    # Insert into LDM
    pqstr = "plot ac %s rwis.txt raw/rwis/%sat.txt txt" % (GTS, GTS)
    subprocess.call(
        ("pqinsert -i -p '%s' %s " "") % (pqstr, atmosfn), shell=True
    )

    # get sfcfn
    sfcfn = "%s/rwis_sf.txt" % (INCOMING,)
    ftp.retrbinary("RETR ExpSfData.txt", open(sfcfn, "wb").write)
    ftp.close()
    # Insert into LDM
    pqstr = "plot ac %s rwis_sf.txt raw/rwis/%ssf.txt txt" % (GTS, GTS)
    subprocess.call(
        ("pqinsert -i -p '%s' %s " "") % (pqstr, sfcfn), shell=True
    )

    return atmosfn, sfcfn


def ldm_insert_metars(fn1, fn2):
    """ Insert into LDM please """
    for fn in [fn1, fn2]:
        proc = subprocess.Popen(
            ("pqinsert -p '%s' %s") % (fn.replace("/tmp/", ""), fn),
            shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        os.waitpid(proc.pid, 0)
        os.unlink(fn)


def main():
    """Go Main Go"""
    (atmosfn, sfcfn) = fetch_files()
    atmos = pd.read_csv(atmosfn)
    surface = pd.read_csv(sfcfn)

    obs = merge(atmos, surface)
    do_windalerts(obs)
    do_iemtracker(obs)

    ts = datetime.datetime.utcnow().strftime("%d%H%M")
    fn1 = "/tmp/IArwis%s.sao" % (ts,)
    fn2 = "/tmp/IA.rwis%s.sao" % (ts,)
    gen_metars(obs, fn1, False)
    gen_metars(obs, fn2, True)
    ldm_insert_metars(fn1, fn2)

    # Discontinued rwis.csv generation, does not appear to be used, I hope

    update_iemaccess(obs)


if __name__ == "__main__":
    main()
    IEM.commit()
    PORTFOLIO.commit()
