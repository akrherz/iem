""" Parse the files generated from LDM rtstats


snprintf(stats_data, sizeof(stats_data),
        "%14.14s %14.14s %32.*s %7.10s %32.*s %12.0lf %12.0lf %.8g
        %10.2f %4.0f@%4.4s %20.20s\n",
        s_time(buf, sizeof(buf), sb->recent.tv_sec),
        s_time(buf_a, sizeof(buf_a), sb->recent_a.tv_sec),
        (int)_POSIX_HOST_NAME_MAX,
        myname,
        s_feedtypet(sb->feedtype),
        (int)HOSTNAMESIZE,
        sb->origin,
        sb->nprods,
        sb->nbytes,
        d_diff_timestamp(&sb->recent_a, &sb->recent),
        sb->latency_sum/(sb->nprods == 0 ? 1: sb->nprods),
        sb->max_latency,
        s_time_abrv(sb->slowest_at),
        PACKAGE_VERSION
);


20121029204759 20121029204759
laptop.local IDS|DDPLUS
chico.unidata.ucar.edu_v_metfs1.agron.iastate.edu
8949
20333883
0.01361
982.48
2207@0001
6.10.1
"""
from __future__ import print_function
import sys
import os
import glob
import stat
import datetime


def get_fileage(fn):
    """Return the age of the file in seconds"""
    now = datetime.datetime.now()
    mtime = os.stat(fn)[stat.ST_MTIME]
    ts = datetime.datetime.fromtimestamp(mtime)
    return (now - ts).total_seconds()


def runner(hostname):
    """ Do something! """
    max_latencies = {}
    host_latencies = {}
    mydir = "/home/ldm/rtstats/%s" % (hostname,)
    os.chdir(mydir)
    for subdir in glob.glob("[A-Z]*"):
        os.chdir(subdir)
        for fn in glob.glob("*_v_*"):
            age = get_fileage(fn)
            # Don't consider any files older than 15 minutes
            if age > 15*60:
                # print('Skipping %s due to age of %s' % (fn, age))
                continue
            line = open(fn).read()
            tokens = line.split()
            if len(tokens) != 11:
                continue
            feedtype = tokens[3]
            latency = float(tokens[7])
            if feedtype not in max_latencies:
                max_latencies[feedtype] = []
                host_latencies[feedtype] = []
            max_latencies[feedtype].append(latency)
            host_latencies[feedtype].append(fn)
        os.chdir("..")

    exitcode = 2
    stats = ""
    msg = "LDM Unknown"
    idsmsg = "IDS Latency Unknown"
    for feedtype in max_latencies:
        if feedtype == 'IDS|DDPLUS':
            idx = max_latencies[feedtype].index(min(max_latencies[feedtype]))
            idsmsg = ("IDS Latency %.0fs %s"
                      ) % (min(max_latencies[feedtype]),
                           host_latencies[feedtype][idx])
            if min(max_latencies[feedtype]) > 600:
                exitcode = 1
                msg = 'ERROR'
            else:
                exitcode = 0
                msg = 'OK'
        stats += " %s_age=%s;600;1200;0 " % (feedtype.replace("|", "_"),
                                             max(max_latencies[feedtype]))
    print("%s - %s |%s" % (msg, idsmsg, stats))
    return exitcode


if __name__ == '__main__':
    sys.exit(runner(sys.argv[1]))
