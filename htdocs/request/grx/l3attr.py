"""Placefile for NEXRAD l3 storm attributes

TODO suggestions:
> On another note, it might be nice to set thresholds for visibility when
> things get cluttered, such as ~420 for overall visibility so you can
> zoom out to max to drop the icons, and maybe a lower value (like 200)
> for storms that don't have either MDA, Hail, or TVS on them. This
> shouldn't take more than changing a few constants and maybe an
> if/assignment statement or two.

TODO:
Add storm tracks.
"""
# pylint: disable=unpacking-non-sequence
import math

import numpy as np
import pyproj
from pyiem.util import convert_value, get_dbconnc
from pyiem.webutil import iemapp
from pymemcache.client import Client

# Do geo math in US National Atlas Equal Area
P3857 = pyproj.Proj("EPSG:3857")

ICONFILE = "https://mesonet.agron.iastate.edu/request/grx/storm_attribute.png"
SECONDS = np.array([15 * 60, 30 * 60, 45 * 60, 60 * 60])
RADARS = """pabc,-161.876
pacg,-135.528
pahg,-151.351
pakc,-156.627
paih,-146.301
paec,-165.293
papd,-147.501
kbmx,-86.770
keox,-85.459
khtx,-86.084
kmxx,-85.790
kmob,-88.240
ksrx,-94.362
klzk,-92.262
kfsx,-111.198
kiwa,-111.670
tphx,-112.163
kemx,-110.630
kyux,-114.656
kbbx,-121.632
keyx,-117.561
kbhx,-124.292
kvtx,-119.179
kdax,-121.678
knkx,-117.041
kmux,-121.898
khnx,-119.632
ksox,-117.636
kvbx,-120.398
kftg,-104.546
kgjx,-108.214
kpux,-104.181
tden,-104.526
kdox,-75.440
kevx,-85.922
kjax,-81.702
kbyx,-81.703
kmlb,-80.654
kamx,-80.413
tfll,-80.344
tmia,-80.491
tmco,-81.326
ttpa,-82.518
tpbi,-80.273
ktlh,-84.329
ktbw,-82.402
kffc,-84.566
kvax,-83.002
kjgx,-83.351
tatl,-84.262
pgua,144.811
phki,-159.552
phkm,-155.778
phmo,-157.180
phwa,-155.569
kdmx,-93.723
kdvn,-90.581
kcbx,-116.236
ksfx,-112.686
klot,-88.085
kilx,-89.337
tmdw,-87.730
tord,-87.858
kvwx,-87.724
kiwx,-85.700
kind,-86.280
tids,-86.436
kddc,-99.969
kgld,-101.700
tich,-97.437
ktwx,-96.232
kict,-97.443
khpx,-87.285
kjkl,-83.313
klvx,-85.944
kpah,-88.772
tsdf,-85.610
kpoe,-92.976
klch,-93.216
klix,-89.825
kshv,-93.841
tmsy,-90.403
kbox,-71.137
tbos,-70.933
tadw,-76.845
tbwi,-76.630
tdca,-76.962
kcbw,-67.806
kgyx,-70.256
kdtx,-83.472
kapx,-84.720
kgrr,-85.545
kmqt,-87.548
tdtw,-83.515
kdlh,-92.210
kmpx,-93.565
tmsp,-92.933
keax,-94.264
ksgf,-93.400
klsx,-90.683
tmci,-94.742
tstl,-90.489
kgwx,-88.329
kdgx,-89.984
kblx,-108.607
kggw,-106.625
ktfx,-111.385
kmsx,-113.986
kmhx,-76.876
krax,-78.490
tclt,-80.885
trdu,-78.697
kltx,-78.429
kbis,-100.760
kmvx,-97.325
kmbx,-100.864
kuex,-98.442
klnx,-100.576
koax,-96.367
tewr,-74.270
kabx,-106.824
kfdx,-103.619
khdx,-106.120
klrx,-116.803
kesx,-114.891
krgx,-119.462
tlas,-115.007
kenx,-74.064
kbgm,-75.985
kbuf,-78.737
ktyx,-75.680
tjfk,-73.881
kokx,-72.864
kcle,-81.860
tcvg,-84.580
tlve,-82.008
tcmh,-82.715
tday,-84.123
kiln,-83.822
kfdr,-98.977
ktlx,-97.278
tokc,-97.510
ttul,-95.827
kinx,-95.564
kvnx,-98.128
kmax,-122.717
kpdt,-118.853
krtx,-122.965
kdix,-74.411
kpbz,-80.218
kccx,-78.004
tphl,-75.069
tpit,-80.486
tjua,-66.078
tsju,-66.179
kclx,-81.042
kcae,-81.119
kgsp,-82.220
kabr,-98.413
kudx,-102.830
kfsd,-96.729
kmrx,-83.402
knqa,-89.873
kohx,-86.563
tmem,-89.993
tbna,-86.662
kama,-101.709
kbro,-97.419
kgrk,-97.383
kcrp,-97.511
kfws,-97.303
kdyx,-99.254
kepz,-106.698
khgx,-95.079
kdfx,-100.280
klbb,-101.814
kmaf,-102.189
ksjt,-100.492
kewx,-98.029
tdal,-96.968
tdfw,-96.918
thou,-95.242
tiah,-95.567
kicx,-112.862
kmtx,-112.448
tslc,-111.930
kfcx,-80.274
klwx,-77.487
tiad,-77.529
kakq,-77.008
kcxx,-73.166
klgx,-124.107
katx,-122.496
kotx,-117.626
kgrb,-88.111
karx,-91.191
kmkx,-88.551
tmke,-88.046
krlx,-81.723
kcys,-104.806
kriw,-108.477"""


def rotate(x, y, rad):
    """rotate"""
    return [
        (x * math.cos(-rad) - y * math.sin(-rad)),
        (x * math.sin(-rad) + y * math.cos(-rad)),
    ]


def dir2ccwrot(mydir):
    """Convert to CCW"""
    if 270 <= mydir <= 360:
        return 0 - (mydir - 270)
    if 180 <= mydir < 270:
        return 270 - mydir
    if 90 <= mydir < 180:
        return 180 - (mydir - 90)
    return 180 + (90 - mydir)


def rabbit_tracks(row):
    """Generate a rabbit track for this attr"""
    res = ""
    if row["sknt"] is None or row["sknt"] <= 5 or row["drct"] is None:
        return res
    # 5 carrots at six minutes to get 30 minutes?
    lat0 = row["lat"]
    lon0 = row["lon"]
    drct = row["drct"]
    sknt = row["sknt"]
    x0, y0 = P3857(lon0, lat0)
    smps = convert_value(sknt, "knot", "meter / second")
    angle = dir2ccwrot(drct)
    rotation = (drct + 180) % 360
    rad = math.radians(angle)
    x = x0 + math.cos(rad) * smps * SECONDS
    y = y0 + math.sin(rad) * smps * SECONDS
    # Draw white line out 30 minutes
    lons, lats = P3857(x, y, inverse=True)
    res += (
        f"Line: 1, 0, \"Cell [{row['storm_id']}]\"\n"
        f"{lat0:.4f}, {lon0:.4f}\n"
        f"{lats[-1]:.4f}, {lons[-1]:.4f}\n"
        "END:\n"
    )
    for i in range(3):
        res += (
            f"Icon: {lats[i]:.4f},{lons[i]:.4f},{rotation:.0f},"
            f'1,10,"+{((i + 1) * 15):.0f} min"\n'
        )
    return res


def produce_content(nexrad, poh, meso, tvs, max_size):
    """Do Stuff"""
    pgconn, cursor = get_dbconnc("radar")
    limiter = ""
    threshold = 999
    title = "IEM NEXRAD L3 Attributes"
    if nexrad != "":
        limiter = f" and nexrad = '{nexrad}' "
        title = f"IEM {nexrad} NEXRAD L3 Attributes"
        threshold = 45
    meso_limiter = ""
    titleadd = ""
    if meso >= 0:
        titleadd = ", all MESO"
        meso_limiter = " and meso != 'NONE' "
        if meso > 1:
            titleadd = f", MESO >= {meso}"
            meso_limiter += f" and meso::float >= {meso} "
    if poh > 0:
        titleadd += f", POH >= {poh}"
    tvs_limiter = ""
    if tvs:
        titleadd += ", all TVS"
        tvs_limiter = " and tvs = 'TVS' "
    if max_size > 0:
        titleadd += f", Max Size >= {max_size}"
    cursor.execute(
        f"""
        SELECT *, ST_x(geom) as lon, ST_y(geom) as lat,
        valid at time zone 'UTC' as utc_valid
        from nexrad_attributes WHERE valid > now() - '15 minutes'::interval
        {limiter} and poh >= %s {meso_limiter} {tvs_limiter} and
        max_size >= %s
        """,
        (poh, max_size),
    )
    res = (
        "Refresh: 3\n"
        f"Threshold: {threshold}\n"
        f"Title: {title}{titleadd}\n"
        f'IconFile: 1, 32, 32, 16, 16, "{ICONFILE}"\n'
        'Font: 1, 11, 1, "Courier New"\n'
    )
    for row in cursor:
        text = (
            f"K{row['nexrad']} [{row['storm_id']}] {row['utc_valid']:%H:%M} "
            f"Z\\n\" \"Drct: {row['drct']} Speed: {row['sknt']} kts\\n"
        )
        icon = 9
        if row["tvs"] != "NONE" or row["meso"] != "NONE":
            text += f"TVS: {row['tvs']} MESO: {row['meso']}\\n"
        if row["poh"] > 0 or row["posh"] > 0:
            text += (
                f"POH: {row['poh']} POSH: {row['posh']} "
                f"MaxSize: {row['max_size']}\\n"
            )
            icon = 2
        if row["meso"] != "NONE":
            meso = int(row["meso"])
            if meso < 4:
                icon = 8
            elif meso < 7:
                icon = 7
            else:
                icon = 6
        if row["tvs"] != "NONE":
            icon = 5
        res += (
            f"Object: {row['lat']:.4f},{row['lon']:.4f}\n"
            "Threshold: 999\n"
            f'Icon: 0,0,0,1,{icon},"{text}"\n'
            "END:\n"
        )
        res += rabbit_tracks(row)
    pgconn.close()
    return res


@iemapp()
def application(environ, start_response):
    """Go Main Go"""
    nexrad = environ.get("nexrad", "").upper()[:3]
    if nexrad == "":
        lon = environ.get("lon")
        if lon is not None:
            for line in RADARS.split("\n"):
                if line.find(lon) > 0:
                    nexrad = line[1:4].upper()

    poh = int(environ.get("poh", 0))
    meso = float(environ.get("meso", -1))
    tvs = "tvs" in environ
    max_size = float(environ.get("max_size", 0))
    mckey = f"/request/grx/i3attr|{nexrad}|{poh}|{meso}|{tvs}|{max_size}"
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        res = produce_content(nexrad, poh, meso, tvs, max_size)
        mc.set(mckey, res, 60)
    else:
        res = res.decode("utf-8")
    mc.close()
    start_response("200 OK", [("Content-type", "text/plain")])
    return [res.encode("ascii")]
