"""
 Generate a first guess file for Harry Hillaker to use for the monthly COOP
 QC, will hopefully save him some time...

sites = []
for line in open('/tmp/SCIA1107.txt'):
    tokens = line.split(",")
    if tokens[0] in ["", "2011", "YR"]:
        continue
    site = "IA%04i" % (int(tokens[0]),)
    if not site in sites:
        sites.append( site )
    
print `sites`
sys.exit()
"""

import sys
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import mx.DateTime
import iemdb
from xlwt import Workbook
MESOSITE = iemdb.connect('mesosite', bypass=True)
mcursor = MESOSITE.cursor()
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

DATA = """IA0112,ALBI4,A
IA0133,ALGI4,B
IA0157,ASNI4,C
IA0200,AMSI4,F
IA0203,AESI4,G
IA0214,AMOI4,H
IA0241,AKYI4,I
IA0364,ATLI4,J
IA0385,AUDI4,K
IA0536,BCNI4,L
IA0576,BEDI4,M
IA0600,BLLI4,N
IA0608,BLVI4,O
IA0745,BLKI4,P
IA0753,BLMI4,Q
IA0807,BNWI4,R
IA0910,BRII4,S
IA0923,BTTI4,T
IA0933,BRKI4,U
IA1060,BLGI4,W
IA1126,CMRI4,V
IA1233,CINI4,Y
IA1257,CASI4,Z
IA1277,CSAI4,AA
IA1319,CRPI4,AC
IA1354,CNTI4,AD
IA1394,CHRI4,AE
IA1402,CIYI4,AF
IA1442,CKPI4,AG
IA1533,CLDI4,AH
IA1541,CLII4,AI
IA1635,CLNI4,AJ
IA0149,ALRI4,AK
IA1704,CLUI4,AL
IA1705,CGGI4,AM
IA0512,BTLI4,AO
IA1833,CRNI4,AQ
IA1954,CRCI4,AR
IA1962,CRTI4,AS
IA2041,DAKI4,CE
IA2110,DCRI4,AU
IA2171,DNSI4,AV
IA2209,DMX,AX
IA2235,DWTI4,AY
IA2299,DNNI4,AZ
IA2311,DORI4,BA
IA2364,DLDI4,BB
IA2573,ELDI4,BE
IA2603,EKRI4,BF
IA2638,ELMI4,BD
IA2689,EMMI4,BG
IA2724,ESTI4,BI
IA7892,SNYI4,BJ
IA2789,FRFI4,BK
IA2864,FYTI4,BL
IA2977,FSCI4,BM
IA2999,WMTI4,BN
IA3007,FTMI4,BO
IA3120,GRWI4,BQ
IA3288,GLNI4,BS
IA3438,GRNI4,BT
IA3473,GRII4,BU
IA3487,GNDI4,BV
IA3509,GTHI4,BW
IA3517,GTTI4,BX
IA3584,HPTI4,BY
IA3632,HRLI4,CA
IA3675,HSII4,CF
IA3718,HAWI4,CB
IA3909,HSTI4,CC
IA4063,IDAI4,CH
IA4094,IONI4,BZ
IA4101,ICYI4,CI
IA4142,IWAI4,CK
IA4228,JFFI4,CL
IA4244,JWLI4,CM
IA4308,KANI4,CN
IA4381,EOKI4,CP
IA4389,KEQI4,CQ
IA4502,KNXI4,CR
IA4557,LMLI4,CS
IA4585,3OI,CU
IA4624,LSGI4,CW
IA4705,LECI4,CX
IA4735,LEMI4,CY
IA4758,LENI4,CZ
IA4874,LSXI4,CO
IA4894,LOGI4,DA
IA4926,LORI4,DB
IA4963,LWDI4,DC
IA5086,MHRI4,DD
IA5123,MPTI4,DE
IA5131,MKTI4,DF
IA5198,MSHI4,DH
IA5230,MCWI4,DJ
IA5235,MCW,DK
IA5250,MSNI4,DL
IA5493,MFRI4,DM
IA5650,MZUI4,DP
IA5769,MTAI4,DQ
IA5796,MPZI4,DR
IA5837,MCTI4,DS
IA5876,NHUI4,DN
IA5952,NHPI4,DT
IA5992,NWTI4,DU
IA6103,NWDI4,DV
IA6151,OAKI4,DW
IA6160,OKMI4,DX
IA6190,OCHI4,DY
IA6199,OLNI4,DZ
IA6243,ONAI4,EB
IA6273,ORCI4,EG
IA6305,OSAI4,EC
IA6316,OSEI4,ED
IA6327,OSKI4,EE
IA6527,PEAI4,EH
IA6566,PERI4,EI
IA6719,POCI4,EJ
IA6766,PSTI4,EL
IA6800,PGHI4,EM
IA6891,RANI4,EN
IA6910,RADI4,EO
IA6940,ROKI4,EP
IA7147,RKRI4,EQ
IA7152,RKVI4,ER
IA7161,RKWI4,ES
IA7312,SACI4,ET
IA7326,SANI4,EK
IA7386,SNBI4,EU
IA7594,SHDI4,EV
IA7613,SDHI4,EW
IA7664,SIBI4,EX
IA7669,SIDI4,EY
IA7678,SGYI4,EZ
IA7700,SIXI4,FA
IA7859,SPRI4,FC
IA7726,SXRI4,FE
IA7844,3SE,FG
IA7979,SLBI4,FI
IA8009,SPTI4,FH
IA8026,SWEI4,FJ
IA8062,SWHI4,FK
IA8296,TLDI4,FN
IA8339,TRPI4,FO
IA8568,VNTI4,FP
IA8668,WAPI4,FR
IA8688,WSHI4,FS
IA8755,WAUI4,FV
IA8806,WEBI4,FW
IA9067,WLBI4,FY
IA9132,WTRI4,FZ
IA9750,ZRGI4,GA
IA8410,UNDI4,GB
IA8693,WHTI4,GC"""

METADATA = {}
ordering = []
for line in DATA.split("\n"):
    tokens = line.split(",")
    METADATA[ tokens[2].strip() ] = {'IEMRE': tokens[0], 'NWSLI': tokens[1]}
    ordering.append( tokens[2].strip() )

def good_value(val, bad):
    if val == bad:
        return 'M'
    return val

def get_site(year, month, iemre, nwsli):
    """
    do our work for this site
    """
    # Create data dictionary to store our wares
    data = [0,]
    sts = mx.DateTime.DateTime(year, month, 1)
    ets = sts + mx.DateTime.RelativeDateTime(months=1)
    while sts < ets:
        data.append({'coop': {'high': '', 'low': '', 'atob': '', 
                              'prec': '', 'sf': '', 'sog': ''},
                     'iemre': {'high': '', 'low': '', 'atob': '', 
                              'prec': '', 'sf': '', 'sog': ''}})
        sts += mx.DateTime.RelativeDateTime(days=1)

    # Go fetch COOP obs
    icursor.execute("""
    select extract(day from day), s.max_tmpf, s.min_tmpf, s.snow, s.snowd, 
    s.coop_tmpf, s.pday from summary_%s s JOIN stations t on (t.iemid = s.iemid) 
    WHERE t.id = '%s' and extract(month from day) = %s and t.network = 'IA_COOP'
    """ % (year, nwsli, month))
    for row in icursor:
        idx = int(row[0])
        data[idx]['coop']['high'] = good_value(row[1], -99)
        data[idx]['coop']['low'] = good_value(row[2], 99)
        data[idx]['coop']['atob'] = row[5]
        data[idx]['coop']['sf'] = good_value(row[3], -99)
        data[idx]['coop']['sog'] = good_value(row[4], -99)
        data[idx]['coop']['prec'] = good_value(row[6], -99)

    # Go Fetch IEMRE
    ccursor.execute("""
    select extract(day from day), high, low, snow, snowd, precip from 
    alldata_ia where station = %s and year = %s and month = %s
    """, (iemre, year, month))
    for row in ccursor:
        idx = int(row[0])
        data[idx]['iemre']['high'] = row[1]
        data[idx]['iemre']['low'] = row[2]
        data[idx]['iemre']['sf'] = row[3]
        data[idx]['iemre']['sog'] = row[4]
        data[idx]['iemre']['prec'] = row[5]

    return data

def get_sitename(site):
    mcursor.execute("""SELECT name from stations where network = 'IACLIMATE'
    and id = %s """, (site,))
    if mcursor.rowcount == 0:
        return site
    return mcursor.fetchone()[0]

def print_data(year, month, iemre, nwsli, sheet, data):
    """
    Print out our data file!
    """
    row = sheet.row(0)
    row.write(8, '?')
    row.write(10, '?')
    row.write(12, "%s %s NWSLI: %s" % (get_sitename(iemre), iemre, nwsli) )
    row = sheet.row(1)
    row.write(2, 'YR')
    row.write(3, 'MO')
    row.write(4, 'DA')
    row.write(6, 'MAX')
    row.write(8, 'MIN')
    row.write(10, 'ATOB')
    row.write(12, 'PREC')
    row.write(14, 'SF')
    row.write(16, 'SOG')
    row.write(17, 'F')
    row.write(18, 'I')
    row.write(19, 'G')
    row.write(20, 'T')
    row.write(21, 'H')
    row.write(22, 'W')

    sts = mx.DateTime.DateTime(year, month, 1)
    ets = sts + mx.DateTime.RelativeDateTime(months=1)
    while sts < ets:
        idx = int(sts.day)
        row = sheet.row(idx+1)
        row.write(0, '%s' % (int(iemre[2:]),))
        row.write(2, year)
        row.write(3, month)
        row.write(4, sts.day)
        row.write(5, data[idx]['iemre']['high'])
        row.write(6, data[idx]['coop']['high'])
        row.write(7, data[idx]['iemre']['low'])
        row.write(8, data[idx]['coop']['low'])
        row.write(10, data[idx]['coop']['atob']) 
        row.write(11, data[idx]['iemre']['prec'])
        row.write(12, data[idx]['coop']['prec'])
        row.write(13, data[idx]['iemre']['sf'])
        row.write(14, data[idx]['coop']['sf'])
        row.write(15, data[idx]['iemre']['sog'])
        row.write(16, data[idx]['coop']['sog'])
        sts += mx.DateTime.RelativeDateTime(days=1)

def runner(year, month):
    """
    Actually generate a text file for the given month
    @return the filename generated
    """
    book = Workbook()
    for label in ordering:
        data = get_site(year, month, METADATA[label]['IEMRE'],
                        METADATA[label]['NWSLI'])
        sheet = book.add_sheet(label)
        sheet.col(0).width = 256*5
        sheet.col(1).width = 256*2
        sheet.col(2).width = 256*5
        sheet.col(3).width = 256*4
        sheet.col(4).width = 256*4
        for col in range(5,17):
            sheet.col(col).width = 256*5
        print_data( year, month, METADATA[label]['IEMRE'],
                        METADATA[label]['NWSLI'], sheet, data)
    fn = "IEM%s%02i.xls" % (year, month)
    book.save(fn)
    return fn

if __name__ == '__main__':
    if len(sys.argv) == 1:
        lastmonth = mx.DateTime.now() - mx.DateTime.RelativeDateTime(months=1)
        fn = runner( lastmonth.year, lastmonth.month)
        # Email this out!
        msg = MIMEMultipart()
        msg['Subject'] = 'IEM COOP Report for %s' % (lastmonth.strftime("%b %Y"),)
        msg['From'] = 'akrherz@iastate.edu'
        msg['To'] = 'Harry.Hillaker@iowaagriculture.gov'
        msg.preamble = 'COOP Report'

        fp = open(fn, 'rb')
        b = MIMEBase('Application', 'VND.MS-EXCEL')
        b.set_payload(fp.read())
        encoders.encode_base64(b)
        fp.close()
        b.add_header('Content-Disposition', 'attachment; filename="%s"' % (fn,))
        msg.attach(b)

        # Send the email via our own SMTP server.
        s = smtplib.SMTP('localhost')
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()
        os.unlink(fn)
    else:
        fn = runner(int(sys.argv[1]), int(sys.argv[2]))
