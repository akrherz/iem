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
    dir = "/home/ldm/rtstats/%s" % (hostname,)
    os.chdir( dir )
    for subdir in glob.glob("[A-Z]*"):
        os.chdir(subdir)
        for file in glob.glob("*_v_*"):
            line = open(file).read()
            tokens = line.split()
            if len(tokens) != 11:
                continue
            feedtype = tokens[3]
            latency = float(tokens[7])
            if not max_latencies.has_key(feedtype):
                max_latencies[feedtype] = []
            max_latencies[feedtype].append( latency )
        os.chdir("..")
    
    exitcode = 0
    stats = ""
    msg = "OK"
    for feedtype in max_latencies:
        if  max(max_latencies[feedtype]) > 600 and feedtype == 'IDS|DDSPLUS':
            exitcode = 1
        stats += " %s_age=%s;600;1200;0 " % (feedtype.replace("|", "_"), 
                                                 max(max_latencies[feedtype]))
    print "%s - OK |%s" % (msg, stats)
    sys.exit(exitcode)
    
if __name__ == '__main__':
    runner( sys.argv[1] )