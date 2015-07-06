""" Parse the files generated from LDM rtstats


        unotice("%s %s %s %12.0lf %12.0lf %10.2f %4.0f@%s %s",
                s_time(buf, sizeof(buf), sb->recent.tv_sec),
                s_feedtypet(sb->feedtype),
                sb->origin,
                sb->nprods,
                sb->nbytes,
                sb->latency_sum/(sb->nprods == 0 ? 1 : sb->nprods),
                sb->max_latency,
                s_time_abrv(sb->slowest_at),
                s_time(buf_a, sizeof(buf_a), sb->recent_a.tv_sec)
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
import sys
import os
import glob


def runner(hostname):
    """ Do something! """
    max_latencies = {}
    mydir = "/home/ldm/rtstats/%s" % (hostname,)
    os.chdir(mydir)
    for subdir in glob.glob("[A-Z]*"):
        os.chdir(subdir)
        for fn in glob.glob("*_v_*"):
            line = open(fn).read()
            tokens = line.split()
            if len(tokens) != 11:
                continue
            feedtype = tokens[3]
            latency = float(tokens[7])
            if feedtype not in max_latencies:
                max_latencies[feedtype] = []
            max_latencies[feedtype].append(latency)
        os.chdir("..")

    exitcode = 0
    stats = ""
    msg = "LDM OK"
    idsmsg = "IDS Latency Unknown"
    for feedtype in max_latencies:
        if feedtype == 'IDS|DDPLUS':
            idsmsg = "IDS Latency %.0fs" % (max(max_latencies[feedtype]), )
            if max(max_latencies[feedtype]) > 600:
                exitcode = 1
                msg = 'ERROR'
        stats += " %s_age=%s;600;1200;0 " % (feedtype.replace("|", "_"),
                                             max(max_latencies[feedtype]))
    print "%s - %s |%s" % (msg, idsmsg, stats)
    sys.exit(exitcode)

if __name__ == '__main__':
    runner(sys.argv[1])
