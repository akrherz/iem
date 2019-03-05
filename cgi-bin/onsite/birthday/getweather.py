#!/usr/bin/env python
"""Legacy."""

import cgi
import datetime
import sys

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn
nt = NetworkTable("IACLIMATE")

COOP = get_dbconn("coop")
ccursor = COOP.cursor()


def mk_header():
    print('Content-type: text/html \n\n')
    print("""
    <HTML>
    <HEAD>  
        <TITLE>IEM| Weather On Your Birthday</TITLE>
        <META name="author" content="Daryl Herzmann akrherz@iastate.edu">
        <link rel=stylesheet type=text/css href=/onsite/birthday/pals.css>
    </HEAD>

    <body BGCOLOR="#ffffff" MARGINWIDTH="20" MARGINHEIGHT="20" vlink="blue" alink="blue" link="blue">

    <TABLE WIDTH="100%" BORDER="0" CELLSPACING="0" CELLPADDING="0"  BORDER="0" BGCOLOR="#99ccff">
    <TR>
        <TD WIDTH="100%" ALIGN="left" NOWRAP>
        <font color="blue" size="3">Iowa Environmental Mesonet</font>
        </TD>
    </TR>

    <TR>
        <TD bgcolor="black"><img src="/icons/blank.gif" height="1" width="3"></TD>
    </TR>
    </TABLE>
    
    <H3>The Weather on Your Birthday!!</H3>
    
    <a href="/onsite/birthday/">Try another date or city</a><BR>
    """)


def weather_logic(month, high, low, rain, snow):
    deltaT = high - low
    
    if month > 4 and month < 11:		# It is summer
        if deltaT >= 30:
            if rain == 0.00:
                return "Sunny!!"
            else:
                return "Mostly sunny w/ Rain!!"
        elif deltaT >= 15 and deltaT < 30:
            if rain == 0.00:
                return "Mostly Sunny!!"
            else:
                return "Partly Sunny w/ Rain!!"
        else:
            if rain == 0.00:
                return "Cloudy!!"
            else:
                return "Cloudy and rainy!!"
        
    else:					# It is winter
        if deltaT >= 20:
            if rain == 0.00:
                return "Sunny!!"
            elif rain > 0 and snow > 0:
                return "Snowy!!"
            else:
                return "Mostly sunny w/ Rain!!"
                
        elif deltaT >= 10 and deltaT < 20:
            if rain == 0.00:
                return "Mostly Sunny!!"
            elif rain > 0 and snow > 0:
                return "Snowy!!"
            else:
                return "Partly Sunny w/ Rain!!"
        else:
            if rain == 0.00:
                return "Cloudy!!"
            elif rain > 0 and snow > 0:
                return "Snowy!!"
            else:
                return "Cloudy and rainy!!"

def get_values(city, dateStr):
    query_str = """SELECT high, low, precip, snow from alldata_ia
    WHERE station = %s and day = %s """
    args = (city, dateStr)
    ccursor.execute(query_str, args)
    row = ccursor.fetchone()
    rain = round(float(row[2]), 2)
    try:
        snow = round(float(row[3]), 2)
    except:
        snow = 0	

    if rain < 0:
        rain = 0
    if snow < 0:
        snow = 0
        
    return row[0], row[1], str(rain), str(snow)



def get_day(city, ts):
    str_month = ts.strftime("%B")
    year = str(ts.year)
    month = str(ts.month)
    day = str(ts.day)
    dateStr = year+"-"+month+"-"+day
    high, low, rain, snow =  get_values(city, dateStr)
    
    cloud_type = weather_logic(int(month), int(high), int(low), round(float(rain), 2), round(float(snow), 2) )

    print('<TD WIDTH="120" VALIGN="TOP" BORDER="1" align="CENTER">')
    print('<img src="/content/date.php?year='+year+'&month='+str_month+'&day='+day+'"><BR>')
    print('<TABLE>')
    print("<TR><TH>HIGH </TH><TD> "+str(high)+"</TD></TR>")
    print("<TR><TH>LOW  </TH><TD> "+str(low)+"</TD></TR>")
    print("<TR><TH>RAIN </TH><TD> "+str(rain)+"</TD></TR>")
    print("<TR><TH>SNOW </TH><TD> "+str(snow)+"</TD></TR>")
    print("<TR><TH colspan='2' NOWRAP><font color='blue'>"+cloud_type+"</font></TH></TR>")
    print('</TABLE>')
    print('</TD>')
    
def now_get_day(city, ts):
    str_month = ts.strftime("%B")
    year = str(ts.year)
    month = str(ts.month)
    day = str(ts.day)
    dateStr = year+"-"+month+"-"+day
    high, low, rain, snow =  get_values(city, dateStr)
    cloud_type = weather_logic(int(month), int(high), int(low), round(float(rain), 2), round(float(snow), 2) )

    print('<TD VALIGN="TOP" BORDER="1" bgcolor="#EEEEEE" rowspan="2" NOWRAP align="center">')
    print('<font color="BLUE">HAPPY BIRTHDAY!!</font><BR><BR>')
    print('<img src="/content/date.php?year='+year+'&month='+str_month+'&day='+day+'"><BR>')
    print('<TABLE>')
    print("<TR><TH>HIGH </TH><TD> "+str(high)+"</TD></TR>")
    print("<TR><TH>LOW  </TH><TD> "+str(low)+"</TD></TR>")
    print("<TR><TH>RAIN </TH><TD> "+str(rain)+"</TD></TR>")
    print("<TR><TH>SNOW </TH><TD> "+str(snow)+"</TD></TR>")
    print("<TR><TH colspan='2' NOWRAP><font color='blue'>"+cloud_type+"</font></TH></TR>")
    print('</TABLE>')
    print('</TD>')


def main():
    """Go Main Go."""
    mk_header()

    form = cgi.FieldStorage()
    try:
        year = form.getfirst("year")
        month = form.getfirst("month")
        day = form.getfirst("day")
        city = form.getfirst("city").upper()
    except:
        print("<P><P><B>Invalid Post:</B><BR>")
        print("Please use this URL <a href='/onsite/birthday/'>https://mesonet.agron.iastate.edu/onsite/birthday/</a>")
        sys.exit(0)

    cityName = nt.sts[city]['name']
    now = datetime.datetime(int(year), int(month), int(day))
    nowM2 = now + datetime.timedelta(days=-2)
    nowM1 = now + datetime.timedelta(days=-1)
    nowP1 = now + datetime.timedelta(days=1)
    nowP2 = now + datetime.timedelta(days=2)
    

    print('<BR><h4>Data valid for station: '+cityName+', Iowa</h4><BR>')
    
    print('<TABLE width="600">')
    print('<TR><TD><BR><BR><BR></TD><TD></TD>')
    now_get_day(city, now)
    print('<TD></TD><TD></TD></TR><TR>')
    
    get_day(city, nowM2)
    
    get_day(city, nowM1)
    
    get_day(city, nowP1)
    
    get_day(city, nowP2)
    
    
    print('</TR></TABLE>')

    print("""
    <BR><BR><P>The weather type listed for each day above in blue is <B>not</b> official data.  A rather
    subjective logic scheme is used to guess the weather purely for entertainment purposes only. 

<TABLE WIDTH="100%" BORDER="0" CELLSPACING="0" CELLPADDING="0"  BORDER="0" BGCOLOR="#99ccff">
<TR>
        <TD bgcolor="black"><img src="/icons/blank.gif" height="1" width="3"></TD>
</TR>

<TR>
        <TD WIDTH="100%" ALIGN="right" NOWRAP>
        <font color="#003366">&copy; 2002 IEM</font><BR>
        </TD>
</TR>

</TABLE>


    """)


if __name__ == '__main__':
    main()
