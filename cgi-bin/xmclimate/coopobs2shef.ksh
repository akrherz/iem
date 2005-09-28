#!/bin/ksh

filepath="$1"

correct=`awk '/Correction:/ {print $2}' $filepath`
loc=`awk '/SiteID:/ {print $2}' $filepath`
obdate=`awk '/Date:/ {print $2}' $filepath`
DH=`awk '/Time:/ {print $3}' $filepath`
TX=`awk '/Max:/ {print $2}' $filepath`
TN=`awk '/Min:/ {print $2}' $filepath`
TA=`awk '/Current:/ {print $2}' $filepath`
PPD=`awk '/Precip:/ {print $2}' $filepath`
SF=`awk '/Snowfall:/ {print $2}' $filepath`
SD=`awk '/Snowdepth:/ {print $2}' $filepath`
XC=`awk '/SkyCover:/ {print $2, $3}' $filepath`
XV=`awk '/Visibility:/ {print $2}' $filepath`
XW=`awk '/Weather:/ {print $2, $3, $4, $5, $6, $7, $8}' $filepath`
US=`awk '/WindSpeed:/ {print $2}' $filepath`
UD=`awk '/WindDir:/ {print $2}' $filepath`
UG=`awk '/WindGust:/ {print $2}' $filepath`
UP=`awk '/PeakWind:/ {print $2}' $filepath`
UR=`awk '/PeakDir:/ {print $2}' $filepath`
PW1=`awk '/Rain:/ {print $2}' $filepath`
PW2=`awk '/Snow:/ {print $2}' $filepath`
PW3=`awk '/Drizzle:/ {print $2}' $filepath`
PW4=`awk '/Fog:/ {print $2}' $filepath`
PW5=`awk '/Hail:/ {print $2}' $filepath`
PW6=`awk '/Thunder:/ {print $2}' $filepath`
PW7=`awk '/Smoke or Haze:/ {print $4}' $filepath`
PW8=`awk '/Freezing Precip:/ {print $3}' $filepath`
PW9=`awk '/Ice Pellets:/ {print $3}' $filepath`
PW10=`awk '/Damaging Winds:/ {print $3}' $filepath`
PW11=`awk '/Blowing Snow:/ {print $3}' $filepath`
AD="/AD 01"

if [ "$TX" ]
then
if [ $TX = "m" ]
then
TX="M"
fi
fi


if [ "$TN" ]
then
if [ $TN = "m" ]
then
TN="M"
fi
fi


if [ "$TA" ]
then
if [ $TA = "m" ]
then
TA="M"
fi
fi


if [ "$PPD" ]
then
if [ $PPD = "m" ]
then
PPD="M"
fi
fi


if [ "$PPD" ]
then
if [ $PPD = "t" ]
then
PPD="T"
fi
fi


if [ "$SF" ]
then
if [ $SF = "m" ]
then
SF="M"
fi
fi


if [ "$SF" ]
then
if [ $SF = "t" ]
then
SF="T"
fi
fi

if [ "$SD" ]
then
if [ $SD = "m" ]
then
SD="M"
fi
fi 

if [ "$SD" ]
then
if [ $SD = "t" ]
then
SD="T"
fi                                                          
fi 

if [ "$correct" ] 
then
 correct=".AR"
 else
 correct=".A"
 fi

if [ "$XC" ]
then
  if [ "$XC" = "Clear " ]
  then
  XC="0"
  fi
  if [ "$XC" = "Scattered " ]
  then
  XC="3"
  fi
  if [ "$XC" = "Mostly Cloudy" ]
  then
  XC="6"
  fi
  if [ "$XC" = "Cloudy " ]
  then
  XC="8"
  fi
fi

if [ "$XW" ]
then
  if [ "$XW" = "Smoke      " ]
  then
  XW="04"
  fi
  if [ "$XW" = "Haze      " ]
  then
  XW="05"
  fi
  if [ "$XW" = "Light Fog (vis > 1/2 mi.) " ]
  then
  XW="10"
  fi
  if [ "$XW" = "Fog (sky visible)    " ]
  then
  XW="44"
  fi
  if [ "$XW" = "Fog (sky not visible)   " ]
  then
  XW="45"
  fi
  if [ "$XW" = "Light Drizzle     " ]
  then
  XW="51"
  fi
  if [ "$XW" = "Moderate Drizzle     " ]
  then
  XW="53"
  fi
  if [ "$XW" = "Heavy Drizzle     " ]
  then
  XW="55"
  fi
  if [ "$XW" = "Light Freezing Drizzle    " ]
  then
  XW="56"
  fi
  if [ "$XW" = "Moderate or Heavy Freezing Drizzle  " ]
  then
  XW="57"
  fi
  if [ "$XW" = "Light Rain     " ]
  then
  XW="61"
  fi
  if [ "$XW" = "Moderate Rain     " ]
  then
  XW="63"
  fi
  if [ "$XW" = "Heavy Rain     " ]
  then
  XW="65"
  fi
  if [ "$XW" = "Light Freezing Rain    " ]
  then
  XW="66"
  fi
  if [ "$XW" = "Moderate or Heavy Freezing Rain  " ]
  then
  XW="67"
  fi
  if [ "$XW" = "Light Mixed Rain and Snow  " ]
  then
  XW="68"
  fi
  if [ "$XW" = "Moderate or Heavy Mixed Rain and Snow" ]
  then
  XW="69"
  fi
  if [ "$XW" = "Light Snow     " ]
  then
  XW="71"
  fi
  if [ "$XW" = "Moderate Snow     " ]
  then
  XW="73"
  fi
  if [ "$XW" = "Heavy snow     " ]
  then
  XW="75"
  fi
  if [ "$XW" = "Sleet      " ]
  then
  XW="79"
  fi
  if [ "$XW" = "Light Rain Showers    " ]
  then
  XW="80"
  fi
  if [ "$XW" = "Moderate or Heavy Rain Showers  " ]
  then
  XW="81"
  fi
  if [ "$XW" = "Light Snow Showers    " ]
  then
  XW="85"
  fi
  if [ "$XW" = "Moderate or Heavy Snow Showers  " ]
  then
  XW="86"
  fi
  if [ "$XW" = "Thunderstorm with Rain or Snow  " ]
  then
  XW="95"
  fi
  if [ "$XW" = "Thunderstorm with Hail    " ]
  then
  XW="96"
  fi
fi

obdate=$obdate" "

DH="L DH"$DH


if [ "$TX" ]
then
TX="/TX "$TX
else
TX=""
fi

if [ "$TN" ]
then
TN="/TN "$TN
else
TN=""
fi

if [ "$TA" ]
then
TA="/TA "$TA
else
TA=""
fi

if [ "$PPD" ]
then
PPD="/PPD "$PPD
else
PPD="/PPD 0.00"
fi

if [ "$SF" ]
then
SF="/SF "$SF
else
SF=""
fi

if [ "$SD" ]                                               
then                                                        
SD="/SD "$SD
else                                                        
SD=""
fi

if [ "$XC" ]                                               
then                                                        
XC="/XC "$XC
else                                                        
XC=""
fi

if [ "$XV" ]                                               
then                                                        
XV="/XV "$XV
else                                                        
XV=""
fi

if [ "$XW" ]                                               
then                                                        
XW="/XW "$XW
else                                                        
XW=""
fi

if [ "$US" ]                                               
then                                                        
US="/US "$US
else                                                        
US=""
fi

if [ "$UD" ]
then
UD=`echo "$UD"| cut -c1-2`
fi

if [ "$UD" ]                                               
then                                                        
UD="/UD "$UD
else                                                        
UD=""
fi

if [ "$UG" ]                                               
then                                                        
UG="/UG "$UG
else                                                        
UG=""
fi

if [ "$UP" ]                                               
then                                                        
UP="/UP "$UP
else                                                        
UP=""
fi

if [ "$UR" ]
then 
UR=`echo "$UR"| cut -c1-2`
fi

if [ "$UR" ]
then
UR="/UR "$UR
else
UR=""
fi

if [ "$PW1" ]
then
PW1="/XWD 61"
fi

if [ "$PW2" ]
then
PW2="/XWD 71"
fi

if [ "$PW3" ]
then
PW3="/XWD 51"
fi

if [ "$PW4" ]
then
PW4="/XWD 10"
fi

if [ "$PW5" ]
then
PW5="/XWD 89"
fi

if [ "$PW6" ]
then
PW6="/XWD 95"
fi

if [ "$PW7" ]
then
PW7="/XWD 05"
fi

if [ "$PW8" ]
then
PW8="/XWD 66"
fi

if [ "$PW9" ]
then
PW9="/XWD 79"
fi


if [ "$PW11" ]
then
PW11="/XWD 38"
fi


dir=`echo /data/rosa/`
tim=`date -u +"%j%H%M%S"`
pathname=$dir$loc.$tim



words=`echo $correct $loc $obdate$DH$TX$TN$TA$PPD$SF$SD$XC$XV$XW$PW1$PW2$PW3$PW4$PW5$PW6$PW7$PW8$PW9$PW11$US$UD$UG$UP$UR$AD|wc -c`
if [ $words -gt 74 ]
then
echo $correct $loc $obdate$DH$TX$TN$TA$PPD$SF$SD$XC$XV$XW>$pathname
echo $correct'1' $PW1$PW2$PW3$PW4$PW5$PW6$PW7$PW8$PW9$PW11$US$UD$UG$UP$UR$AD>>$pathname
else
echo $correct $loc $obdate$DH$TX$TN$TA$PPD$SF$SD$XC$XV$XW$PW1$PW2$PW3$PW4$PW5$PW6$PW7$PW8$PW9$PW11$US$UD$UG$UP$UR$AD>$pathname
fi

echo $pathname

exit


