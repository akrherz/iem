"""
    Dump RWIS surface data to an intermediate file that GEMPAK can use
"""
import pytz
import access
import iemdb
import datetime
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

def f(v):
    print v, v is None
    if v is None:
        return '-9999'
    return v

def Main():
    ian = access.get_network("IA_RWIS", IEM)

    out = open("/tmp/rwis_surface.list", "w")
    out.write(""" PARM = TCS0;TCS1;TCS2;TCS3;SUBC

    STN    YYMMDD/HHMM      TCS0     TCS1     TCS2     TCS3     SUBC
""")

    now = datetime.datetime.now()
    now = now.replace(tzinfo=pytz.timezone("America/Chicago"))
    thres = now - datetime.timedelta(hours=1)
    for sid in ian.keys():
        if ian[sid].data["valid"] < thres:
            continue
        m = ian[sid].data["valid"].minute
        if m > 45:
            ts = ian[sid].data["valid"] + datetime.timedelta(hours=+1)
            ts = ts.replace(minute=0)
        elif m > 25:
            ts = ian[sid].data["valid"].replace(minute=40)
        elif m >  5:
            ts = ian[sid].data["valid"].replace(minute=20)
        else:
            ts = ian[sid].data["valid"].replace(minute=0)
        out.write("%10s %16s %8s %8s %8s %8s %8s\n" % (
            sid, ts.astimezone(pytz.timezone("UTC")).strftime("%y%m%d/%H%M"), 
            f(ian[sid].data.get("tsf0")), 
           f(ian[sid].data.get("tsf1")), f(ian[sid].data.get("tsf2")), 
           f(ian[sid].data.get("tsf3")), 
           f(ian[sid].data.get("rwis_subf")) ) )

    out.close()
Main()
