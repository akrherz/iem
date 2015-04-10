"""
 Attempt to process the 1 minute archives available from NCDC

 NCDC provides monthly tar files for nearly up to the current day here:

 http://www1.ncdc.noaa.gov/pub/download/hidden/onemin/
"""
import re
import os
import subprocess
import sys
import datetime
import pytz
import urllib2

BASEDIR = "/mesonet/ARCHIVE/raw/asos/"

P1_RE = re.compile(r"""
(?P<wban>[0-9]{5})
(?P<faaid>[0-9A-Z]{4})\s
(?P<id3>[0-9A-Z]{3})
(?P<tstamp>[0-9]{16})\s+
((?P<vis1_coef>\-?\d+\.\d*)|(?P<vis1_coef_miss>M))\s*\s*
(?P<vis1_nd>[0-9A-Za-z\?\$/ ])\s+
((?P<vis2_coef>\d+\.\d*)|(?P<vis2_coef_miss>[M ]))\s+(?P<vis2_nd>[A-Za-z\?\$ ])\s+
...............\s+
((?P<drct>\d+)|(?P<drct_miss>M))\s+
((?P<sknt>\d+)|(?P<sknt_miss>M))\s+
((?P<gust_drct>\d+)\+?|(?P<gust_drct_miss>M))\s+
((?P<gust_sknt>\d+)R?L?F*\d*\+?|(?P<gust_sknt_miss>M))\s+
(....)\s
(...)
""", re.VERBOSE)

p1_examples = [
"14923KMLI MLI2010010206581258   0.109 b                              M     M     M     0    09 60+              ",
"14923KMLI MLI2010010309121512  -0.126 D                              M     M    276    6    09 60+              ",
"14923KMLI MLI2010011107091309 [ 0.219 N]                          [ 296     6   294    9 ] [09 60+]             ",
"14931KBRL BRL2010012100100610   1.774 B                              M     M     85   10                        ",
"14942KOMA OMA2010011316472247   0.143 D                             183    13   179   16   [14R60+]             ",
"14942KOMA OMA2010011521400340   0.989 N                             168    12   164   14    14R60+              ",
"14942KOMA OMA2010011708051405   5.278 D                             245     3   257    4    14R24               ",
"14931KBRL BRL2010012103370937   3.657 V                              M     M     92   13                        ",
"14931KBRL BRL2010012023010501   2.819 S                              M     M     89   11                        ",
"14943KSUX SUX2010010100000600   0.104 N                             318     2   318    3      M                 ",
"14943KSUX SUX2010013123590559   0.115 N                              96     8   102   10      M                 ",
"94989KAMW AMW2010010106261226   0.087 N                             318     9   321   11                        ",
"14933KDSM DSM2010010101380738   0.098 N                             306     9   312    9    31 60+              ",
"94989KAMW AMW2010012112281828    M    M                              80     6    72    9                        ",
"94989KAMW AMW2010012112271827  70000.00                                80     6    82    8                      ",
"14942KOMA OMA2012111704141014   0.191 N                             149    10   151   12    14RFFF              ",
"14933KDSM DSM2013030312191819    0.167 [N]                             120   11  121   12   31 60+              ",
"03928KICT ICT2013060105471147   0.050 D                             325    14   329   19    01L60+              ",
"14942KOMA OMA2013120308291429  [   M  ][D]                            [ M    M    M    M ] []                   ",
"14942KOMA OMA2013120309421542  [ 0.265][D]                            [ M    M    M    M ] [14R60+]             ",
"14942KOMA OMA2013121611251725  [15.300] D                              161    2  189    3   14R60+              ",
]

P2_RE = re.compile(r"""
(?P<wban>[0-9]{5})
(?P<faaid>[0-9A-Z]{4})\s
(?P<id3>[0-9A-Z]{3})
(?P<tstamp>[0-9]{16})\s+
\s?(?P<ptype>[a-zA-Z0-9\?\-\+\.]{1,2})\s?\s?\s?
((?P<unk>\d+)V?|\s+(?P<unk_miss>[M ]))\s+\s?
\s*((?P<precip>\d+\.\d*)|(?P<precip_miss>[M ]))\s*
............\s+
((?P<unk2>\d*)|(?P<unk2_miss>M))\s+
((?P<pres1>\d+\.\d*)|(?P<pres1_miss>[M ]))\s*
((?P<pres2>\d+\.\d*)|(?P<pres2_miss>[M ]))\s*
((?P<pres3>\d+\.\d*)|(?P<pres3_miss>[M ]))\s*
\s*((?P<tmpf>\-?\d+)|(?P<tmpf_miss>[M ]))\s*
\s*((?P<dwpf>\-?\d+)|(?P<dwpf_miss>[M ]))\s+
""", re.VERBOSE)


p2_examples = [
"94908KDBQ DBQ2012020713191919  NP [0000  ][ 0.00]            39971   29.196  29.197  29.204    29   23          ",
"14972KSPW SPW2009110517122312  NP  0000   [ 0.00]            39992   28.661  28.673            50   34         ",
"94991KLWD LWD2009122215352135  NP  0000     0.00             39992   28.738  28.736          [ 32]  30         ",
"14944KFSD FSD2010013123590559  NP           0.00             39985   28.686  28.681  28.684     7    2         ",
"14937KIOW IOW2010010212131813  M   0000      M                 M    [29.841][29.840]           M    M          ",
"14990KCID CID2010012705561156  NP [0000  ]  0.00            [39967]  29.193  29.188  29.195    11    5         ",
"14990KCID CID2010012708381438 [S-][0000  ]  0.00             39967   29.205  29.199  29.207    15    9         ",
"14972KSPW SPW2010012507461346 [M ] 0000     0.00             39994   28.021  28.035            20   17         ",
"14931KBRL BRL2010012016222222  Yb  0000     0.00             39840   28.974  28.974  28.980    33   31         ",
"14931KBRL BRL2010012012041804  P   0001V    0.00             39547   29.014  29.013  29.019    32   30         ",
"14931KBRL BRL2010012016332233  0.    M      0.00             39831     M       M       M       33   31         ",
"94988KMIW MIW2010012110331633  M     M       M                 M     28.736  28.733            M    M           ",
"14931KBRL BRL2010012105471147  NP    M       M               40000   28.945  28.944  28.950    34   33          ",
"14940KMCW MCW2010010916182218  NP  0000     0.00               M     29.192  29.196  29.197    M    M           ",
"14943KSUX SUX2010010100000600  NP  0000     0.00             39981   29.200  29.200  29.205    -2   -7          ",
"14933KDSM DSM2010010101380738  NP [0000  ]  0.00             39991   29.336  29.331  29.330     3   -5          ",
"94982KDVN DVN2010010101350735  NP  0000     0.00             39942   29.508  29.500            -1   -6          ",
"14943KSUX SUX2010013123050505  NP    M      0.00             39988   29.013  29.012  29.018    13    6          ",
"14943KSUX SUX2010013109471547  ?0 [  M   ]  0.00             39988   29.087  29.086  29.092    16   10          ",
"94989KAMW AMW2010010613201920  S   0000     0.01             40002   29.197  29.191             9    5          ",
"14944KFSD FSD2012111613061906  NP [0000  ]  0.00             39992   28.806  28.797  28.801    45 [ 25]         ",
"14937KIOW IOW2013042921140314  NP  0000                      39975   28.966  28.962            70   59          ",
"14933KDSM DSM2013101412201820 [ S-] 0000    0.00              40003   29.096  29.088  29.089   65   37          ",
"14944KFSD FSD2013121800080608   NP  0000    0.00              39998   28.456  28.449  28.451 [ 38][ 14]         ",
"14933KDSM DSM2013121710211621   NP [0000  ] 0.00              40009   29.131  29.125  29.124 [ M ]  25          ",
"14943KSUX SUX2013122716022202 [ M ] 0000                     [  M  ]  28.854  28.852  28.859 [ M ][ M ]         ",
"14942KOMA OMA2013120308361436 [ M ][  M   ]                  [  M  ] [  M   ][  M   ][  M   ][ M ][ M ]         ",
]


def tstamp2dt(s):
    """ Convert a string to a datetime """
    ts = datetime.datetime(int(s[:4]), int(s[4:6]), int(s[6:8]))
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))
    local_hr = int(s[8:10])
    utc_hr = int(s[12:14])
    if utc_hr < local_hr:  # Next day assumption valid in United States
        ts += datetime.timedelta(hours=24)
    return ts.replace(hour=utc_hr, minute=int(s[14:16]))


def p2_parser(ln):
    """
    Handle the parsing of a line found in the 6506 report, return QC dict
    """
    m = P2_RE.match(ln.replace("]", "").replace("[", ""))
    if m is None:
        print "P2_FAIL:|%s|" % (ln,)
        return None
    res = m.groupdict()
    res['ts'] = tstamp2dt(res['tstamp'])
    """
    for v in ['tmpf', 'dwpf']:
        if d['%s_miss' % (v,)]:
            ret[v] = "Null"
        else:
            ret[v] = int( d[v] )

    for v in ['pres1', 'pres2', 'pres3', 'precip']:
        if d['%s_miss' % (v,)]:
            ret[v] = "Null"
        else:
            ret[v] = float( d[v] )
    """
    return res


def p1_parser(ln):
    """
    Handle the parsing of a line found in the 6505 report, return QC dict
    """
    m = P1_RE.match(ln.replace("]", "").replace("[", ""))
    if m is None:
        print "P1_FAIL:|%s|" % (ln,)
        return None
    res = m.groupdict()
    res['ts'] = tstamp2dt(res['tstamp'])
    """
    if d['vis1_coef_miss']:
        ret['vis1_coef'] = "Null"
    else:
        ret['vis1_coef'] = float( d['vis1_coef'] )

    ret['vis1_nd'] = d['vis1_nd']

    if d['vis2_coef_miss']:
        ret['vis2_coef'] = "Null"
    else:
        ret['vis2_coef'] = float( d['vis2_coef'] )

    ret['vis2_nd'] = d['vis2_nd']

    for v in ['sknt', 'drct', 'gust_drct', 'gust_sknt']:
        if d['%s_miss' % (v,)]:
            ret[v] = "Null"
        else:
            ret[v] = int( d[v] )
    """
    return res


def test():
    for ex in p1_examples:
        p1_parser(ex)

    for ex in p2_examples:
        p2_parser(ex)


def download(station, monthts):
    """
    Download a month file from NCDC
    """
    baseuri = "ftp://ftp.ncdc.noaa.gov/pub/data/asos-onemin/"
    datadir = "%s/data/%s" % (BASEDIR, station)
    if not os.path.isdir(datadir):
        os.makedirs(datadir)
    for page in [5,6]:
        uri = baseuri + "640%s-%s/640%s0K%s%s.dat" % (page, monthts.year, page,
                                    station, monthts.strftime("%Y%m"))
        url = urllib2.Request(uri)
        fp = urllib2.urlopen(url)
        data = fp.read()
        o = open("%s/640%s0K%s%s.dat" % (datadir, page,
                                    station, monthts.strftime("%Y%m")),'w')
        o.write(data)
        o.close()


def runner(station, monthts):
    """
    Parse a month's worth of data please
    """

    # Our final amount of data
    data = {}
    if os.path.isfile("64050K%s%s%02i" % (station,monthts.year, monthts.month)):
        fn5 = '64050K%s%s%02i' % (station, monthts.year, monthts.month)
        fn6 = '64060K%s%s%02i' % (station, monthts.year, monthts.month)        
    else:
        fn5 = '%sdata/%s/64050K%s%s%02i.dat' % (BASEDIR, station,
                station, monthts.year, monthts.month)
        fn6 = '%sdata/%s/64060K%s%s%02i.dat' % (BASEDIR, station,
                station, monthts.year, monthts.month)
        if not os.path.isfile( fn5 ):
            try:
                download(station, monthts)
            except Exception, exp:
                print 'download() error', exp
            if not os.path.isfile( fn5 ) or not os.path.isfile( fn6 ):
                print "NCDC did not have %s station for %s" % (station,
                                                    monthts.strftime("%b %Y"))
                return
    # We have two files to worry about
    print "Processing 64050: %s" % (fn5,)
    for ln in open(fn5):
        d = p1_parser( ln )
        if d is None:
            continue
        data[ d['ts'] ] = d

    print "Processing 64060: %s" % (fn6,)
    for ln in open(fn6):
        d = p2_parser( ln )
        if d is None:
            continue
        if not data.has_key( d['ts'] ):
            data[ d['ts'] ] = {}
        for k in d.keys():
            data[ d['ts'] ][ k ] = d[k]

    if len(data) == 0:
        print 'No data found for station: %s' % (station,)
        return

    mints = None
    maxts = None
    for ts in data.keys():
        if mints is None or maxts is None:
            mints = ts
            maxts = ts
        if mints > ts:
            mints = ts
        if maxts < ts:
            maxts = ts

    tmpfn = "/tmp/%s%s-dbinsert.sql" % (station, monthts.strftime("%Y%m"))
    out = open( tmpfn , 'w')
    out.write("""DELETE from alldata_1minute WHERE station = '%s' and 
               valid >= '%s' and valid <= '%s';\n""" % (station, mints, maxts))
    out.write("COPY t%s_1minute FROM stdin WITH NULL as 'Null';\n" % (
         monthts.year,))

    # Loop over the data we got please
    keys = data.keys()
    keys.sort()
    flipped = False
    for ts in keys:
        if ts.year != monthts.year and not flipped:
            print "  Flipped years from %s to %s" % (monthts.year, ts.year)
            out.write("\.\n")
            out.write(("COPY t%s_1minute FROM stdin WITH NULL as 'Null';\n"
                       ) % (ts.year,))
            flipped = True
        ln = ""
        data[ts]['station'] = station
        for col in ['station', 'ts', 'vis1_coeff', 'vis1_nd',
                    'vis2_coeff', 'vis2_nd', 'drct', 'sknt', 'gust_drct',
                    'gust_sknt', 'ptype', 'precip', 'pres1', 'pres2', 'pres3',
                    'tmpf', 'dwpf']:
            ln += "%s\t" % (data[ts].get(col) or 'Null',)
        out.write(ln[:-1]+"\n")
    out.write("\.\n")
    out.close()

    proc = subprocess.Popen("psql -f %s -h iemdb asos" % (tmpfn,), shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = proc.stdout.read()
    stderr = proc.stderr.read()

    print(("%s %s processed %s entries [%s to %s UTC]\n"
           "STDOUT: %s\nSTDERR: %s"
           ) % (datetime.datetime.now().strftime("%H:%M %p"),
                station, len(data.keys()), mints.strftime("%y%m%d %H:%M"),
                maxts.strftime("%y%m%d %H:%M"), stdout.replace("\n", " "),
                stderr.replace("\n", " ")))

    if stderr == '':
        os.unlink(tmpfn)


def main(argv):
    if len(argv) == 3:
        for station in ["DVN", "LWD", "FSD", "MLI", 'OMA', 'MCW', 'BRL', 'AMW',
                        'MIW', 'SPW', 'OTM', 'CID', 'EST', 'IOW', 'SUX', 'DBQ',
                        'ALO', 'DSM']:
            runner(station,
                   datetime.datetime(int(argv[1]), int(argv[2]), 1))
    elif len(argv) == 4:
            if int(argv[3]) != 0:
                months = [int(argv[3]), ]
            else:
                months = range(1, 13)
            for month in months:
                runner(sys.argv[1], datetime.datetime(int(argv[2]), month, 1))
    else:
        test()

if __name__ == '__main__':
    main(sys.argv)
