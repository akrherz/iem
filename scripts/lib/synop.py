# Helper function to convert observation to something NCL understands

from pyIEM import mesonet

def lookup_skyc( val1, val2, val3 ):
    """
    Convert the textual sky coverage into a value
    """
#0 -- 0 eighths (clear)
#1 -- 1/8th
#2 -- 2/8ths
#3 -- 3/8ths
#4 -- 4/8ths
#5 -- 5/8ths
#6 -- 6/8ths
#7 -- 7/8ths
#8 -- 8/8ths (overcast)
#9 -- sky obscured
#/ -- no observation 
    if val1 == "OVC" or val2 == "OVC" or val3 == "OVC":
        return "8"
    if val1 == "BKN" or val2 == "BKN" or val3 == "BKN":
        return "6"
    if val1 == "SCT" or val2 == "SCT" or val3 == "SCT":
        return "4"
    if val1 == "FEW" or val2 == "FEW" or val3 == "FEW":
        return "2"
    if val1 == "CLR" or val2 == "CLR" or val3 == "CLR":
        return "0"
    return "/"

def lookup_vis( val ):
    """
    Convert the val in km to its lookup value
    """
#90 -- less than 0.05 km
#91 -- 0.05 km
#92 -- 0.2 km
#93 -- 0.5 km
#94 -- 1 km
#95 -- 2 km
#96 -- 4 km
#97 -- 10 km
#98 -- 20 km
#99 -- greater than 50 km
    bins = [0.05, 0.2, 0.5, 1, 2, 4, 10, 20, 50, 100000]
    cnt = 90
    for bin in bins: 
        if val < bin:
            return str(cnt)
        cnt += 1
    return "/"

def lookup_skyl( val ):
    """
    Convert the val in meters to its lookup value
    """
#0 -- 0 to 50 m
#1 -- 50 to 100 m
#2 -- 100 to 200 m
#3 -- 200 to 300 m
#4 -- 300 to 600 m
#5 -- 600 to 1000 m
#6 -- 1000 to 1500 m
#7 -- 1500 to 2000 m
#8 -- 2000 to 2500 m
#9 -- above 2500 m
#/ -- unknown
    bins = [50,100,200,300,600,1000,1500,2000,2500,1000000]
    cnt = 0
    for bin in bins: 
        if val < bin:
            return str(cnt)
        cnt += 1
    return "/"

def ob2synop(ob):
    """
    Take a given observation {dictionary} and return a sao coded text
    http://weather.unisys.com/wxp/Appendices/Formats/SYNOP.html
    """
    ar = ["0"] * 50
# character 0  	=  	iR  	-  	the precipitation data indicator
#0 -- Precipitation in groups 1 and 3
#1 -- Precipitation reported in group 1 only
#2 -- Precipitation reported in group 3 only
#3 -- Precipitation omitted, no precipitation
#4 -- Precipitation omitted, no observation 
    if ob.has_key("phour") and ob["phour"] is not None:
        ar[0] = "1"
    else:
        ar[0] = "4"
    
#character 1 	=	iX 	- 	weather data and station type indicator
#1 -- manned station -- weather group included
#2 -- manned station -- omitted, no significant weather
#3 -- manned station -- omitted, no weather observation
#4 -- automated station -- weather group included (see automated weather codes 4677 and 4561)
#5 -- automated station -- omitted, no significant weather
#6 -- automated station -- omitted, no weather observation
#7 -- automated station -- weather group included (see automated weather codes 4680 and 4531) 
    ar[1] = "4"

    #character 2 	=	h 	- 	height above ground of base of lowest cloud
    ar[2] = "/"
    if ob.has_key("skyl1") and ob["skyl1"] is not None and ob["skyl1"] > 0:
        ar[2] = lookup_skyl( ob["skyl1"] * 0.3048 )

    #characters 3-4 	=	VV 	- 	visibility in miles and fractions
    ar[3:5] = "//"
    if ob.has_key("vsby") and ob["vsby"] is not None and ob["vsby"] >= 0:
        ar[3:5] = lookup_vis( ob["vsby"] * 1.609344 )

    #character 5 	=	N 	- 	total amount of cloud cover
    ar[5] = "/"
    if ob.has_key("skyc1") and ob.has_key("skyc2") and ob.has_key("skyc3"):
        ar[5] = lookup_skyc( ob['skyc1'], ob['skyc2'], ob['skyc3'] )
 

    #characters 6-7 	= 	dd 	- 	direction from which wind is blowing
    if ob.has_key("drct") and ob['drct'] is not None:
        ar[6:8] = "%02i" % (ob['drct'] / 10.0,)

    #characters 8-9 	= 	ff 	- 	wind speed in knots
    if ob.has_key("sknt") and ob['sknt'] is not None:
        ar[8:10] = "%02i" % (ob['sknt'],)

    #If character 10 = "1", then
    #    character 11 	=	sn 	- sign of temperature
    #   characters 12-14 	= 	TTT 	- current air temperature
    if ob.has_key("tmpf") and ob['tmpf'] is not None:
        ar[10] = "1"
        tmpc = mesonet.f2c( ob["tmpf"] )
        if tmpc < 0:
            ar[11] = "1"
            tmpc = -1. * tmpc
        ar[12:15] = "%03i" % (tmpc * 10.0,)

    #If character 15 = "2", then
    #
    # character 16 	= 	sn 	- sign of temperature
    # characters 17-19 	= 	Td 	- dew point
    if ob.has_key("dwpf") and ob['dwpf'] is not None:
        ar[15] = "2"
        dwpc = mesonet.f2c( ob["dwpf"] )
        if dwpc < 0:
            ar[16] = "1"
            dwpc = -1. * dwpc
        ar[17:20] = "%03i" % (dwpc * 10.0,)

    #If character 20 = "3", then
    #
    #      characters 21-24 	= 	PO 	- station pressure (not plotted)
    if ob.has_key("alti") and ob["alti"] is not None:
        ar[20] = "3"
        ar[21:25] = str( "%4i" % (ob["alti"] * 33.8638866667 * 10.0,))

    #If character 25 = "4", then
    #
    #      characters 26-29 	= 	PPPP 	- pressure reduced to sea level
    if ob.has_key("pmsl") and ob["pmsl"] is not None:
        ar[25] = "4"
        ar[26:30] = str( "%4i" % (ob["pmsl"] * 10.0,))

#If character 30 = "5", then
#
#      character 31 	= 	a 	- characteristic of barograph
#      characters 32-34 	= 	ppp 	- pressure change, last 3 hrs.

#If character 35 = "6", then
#
#      characters 36-38 	= 	RRR 	- precipitation
#      character 39 	= 	tR 	- time duration of precipitation
    if ob.has_key("phour") and ob["phour"] is not None and ob["phour"] >= 0:
        ar[35] = "6"
        ar[36:39] = str( "%3i" % ( ob["phour"] * 25.4, ))
        ar[39] = "5" # 1 hour total

#If character 40 = "7", then
#
#     characters 41-42 	= 	ww 	- present weather
#      character 43 	= 	W1 	- most significant past weather
#      character 44 	= 	W2 	- 2nd most sig. past weather
    #ar[40:45] = "7////"
#
#If character 45 = "8", then
#
#      character 46 	= 	Nh 	- Fraction of sky cover
#      character 47 	= 	CL 	- cloud type, low clouds
#      character 48 	= 	CM 	- cloud type, medium clouds
#      character 49 	= 	CH 	- cloud type, high clouds
    #ar[45:50] = "8////"

    return "".join( ar )
