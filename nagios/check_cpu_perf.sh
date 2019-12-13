#!/bin/bash
#
# Check CPU Performance plugin for Nagios 
#
# Licence : GPL - http://www.fsf.org/licenses/gpl.txt
#
# Author        : Luke Harris
# version       : 2011090802
# Creation date : 1 October 2010
# Revision date : 8 September 2011
# Description   : Nagios plugin to check CPU performance statistics.
#               This script has been tested on the following Linux and Unix platforms:
#		RHEL 4, RHEL 5, RHEL 6, CentOS 4, CentOS 5, CentOS 6, SUSE, Ubuntu, Debian, FreeBSD 7, AIX 5, AIX 6, and Solaris 8 (Solaris 9 & 10 *should* work too)
#               The script is used to obtain key CPU performance statistics by executing the sar command, eg. user, system, iowait, steal, nice, idle
#		The Nagios Threshold test is based on CPU idle percentage only, this is NOT CPU used.
#		Support has been added for Nagios Plugin Performance Data for integration with Splunk, NagiosGrapher, PNP4Nagios, 
#		opcp, NagioStat, PerfParse, fifo-rrd, rrd-graph, etc
#
# USAGE         : ./check_cpu_perf.sh {warning} {critical}
#
# Example: ./check_cpu_perf.sh 20 10
# OK: CPU Idle = 84.10% | CpuUser=12.99; CpuNice=0.00; CpuSystem=2.90; CpuIowait=0.01; CpuSteal=0.00; CpuIdle=84.10:20:10
#
# Note: the option exists to NOT test for a threshold. Specifying 0 (zero) for both warning and critical will always return an exit code of 0.


#Ensure warning and critical limits are passed as command-line arguments
if [ -z "$1" -o -z "$2" ]
then
 echo "Please include two arguments, eg."
 echo "Usage: $0 {warning} {critical}"
 echo "Example :-"
 echo "$0 20 10"
exit 3
fi

#Disable nagios alerts if warning and critical limits are both set to 0 (zero)
if [ $1 -eq 0 ]
 then
  if [ $2 -eq 0 ]
   then
    ALERT=false
  fi
fi
        
#Ensure warning is greater than critical limit
if [ $1 -lt $2 ]
 then
  echo "Please ensure warning is greater than critical, eg."
  echo "Usage: $0 20 10"
  exit 3
fi

#Detect which OS and if it is Linux then it will detect which Linux Distribution.
OS=`uname -s`
 
GetVersionFromFile()
{
	VERSION=`cat $1 | tr "\n" ' ' | sed s/.*VERSION.*=\ // `
}
 
if [ "${OS}" = "SunOS" ] ; then
	OS=Solaris
	DIST=Solaris
	ARCH=`uname -p`	
elif [ "${OS}" = "AIX" ] ; then
	DIST=AIX
elif [ "${OS}" = "FreeBSD" ] ; then
	DIST=BSD
elif [ "${OS}" = "Linux" ] ; then
	KERNEL=`uname -r`
	if [ -f /etc/redhat-release ] ; then
		DIST='RedHat'
	elif [ -f /etc/SuSE-release ] ; then
		DIST=`cat /etc/SuSE-release | tr "\n" ' '| sed s/VERSION.*//`
	elif [ -f /etc/mandrake-release ] ; then
		DIST='Mandrake'
	elif [ -f /etc/debian_version ] ; then
		DIST="Debian `cat /etc/debian_version`"
	fi
	if [ -f /etc/UnitedLinux-release ] ; then
		DIST="${DIST}[`cat /etc/UnitedLinux-release | tr "\n" ' ' | sed s/VERSION.*//`]"
	fi
fi

#Define package format 
case "`echo ${DIST}|awk '{print $1}'`" in
'RedHat')
PACKAGE="rpm"
;;
'SUSE')
PACKAGE="rpm"
;;
'Mandrake')
PACKAGE="rpm"
;;
'Debian')
PACKAGE="dpkg"
;;
'UnitedLinux')
PACKAGE="rpm"
;;
'Solaris')
PACKAGE="pkginfo"
;;
'AIX')
PACKAGE="lslpp"
;;
'BSD')
PACKAGE="pkg_info"
;;
esac

#Define locale to ensure time is in 24 hour format
LC_MONETARY=en_AU.UTF-8
LC_NUMERIC=en_AU.UTF-8
LC_ALL=en_AU.UTF-8
LC_MESSAGES=en_AU.UTF-8
LC_COLLATE=en_AU.UTF-8
LANG=en_AU.UTF-8
LC_TIME=en_AU.UTF-8

#Collect sar output
case "$PACKAGE" in
'rpm')
SARCPU=`/usr/bin/sar -P ALL|grep all|grep -v Average|tail -1`
SYSSTATRPM=`rpm -q sysstat|awk -F\- '{print $2}'|awk -F\. '{print $1}'`
if [ $SYSSTATRPM -gt 5 ]
 then
  SARCPUIDLE=`echo ${SARCPU}|awk '{print $8}'|awk -F. '{print $1}'`
  CPU=`echo ${SARCPU}|awk '{print "CPU Idle = " $8 "% | " "CpuUser=" $3 "; CpuNice=" $4 "; CpuSystem=" $5 "; CpuIowait=" $6 "; CpuSteal=" $7 "; CpuIdle=" $8":20:10"}'`
 else
  SARCPUIDLE=`echo ${SARCPU}|awk '{print $7}'|awk -F. '{print $1}'`
  CPU=`echo ${SARCPU}|awk '{print "CPU Idle = " $7 "% | " "CpuUser=" $3 "; CpuNice=" $4 "; CpuSystem=" $5 "; CpuIowait=" $6 "; CpuIdle=" $7":20:10"}'`
fi
;;
'dpkg')
SARCPU=`/usr/bin/sar -P ALL|grep all|grep -v Average|tail -1`
SYSSTATDPKG=`dpkg -l sysstat|grep sysstat|awk '{print $3}'|awk -F\. '{print $1}'`
if [ $SYSSTATDPKG -gt 5 ]
 then
  SARCPUIDLE=`echo ${SARCPU}|awk '{print $8}'|awk -F. '{print $1}'`
  CPU=`echo ${SARCPU}|awk '{print "CPU Idle = " $8 "% | " "CpuUser=" $3 "; CpuNice=" $4 "; CpuSystem=" $5 "; CpuIowait=" $6 "; CpuSteal=" $7 "; CpuIdle=" $8":20:10"}'`
 else
  SARCPUIDLE=`echo ${SARCPU}|awk '{print $7}'|awk -F. '{print $1}'`
  CPU=`echo ${SARCPU}|awk '{print "CPU Idle = " $7 "% | " "CpuUser=" $3 "; CpuNice=" $4 "; CpuSystem=" $5 "; CpuIowait=" $6 "; CpuIdle=" $7":20:10"}'`
fi
;;
'lslpp')
SARCPU=`/usr/sbin/sar -P ALL|grep "\-"|grep -v U|tail -2|head -1`
SYSSTATLSLPP=`lslpp -l bos.acct|tail -1|awk '{print $2}'|awk -F\. '{print $1}'`
if [ $SYSSTATLSLPP -gt 4 ]
 then
  CpuPhysc=`echo ${SARCPU}|awk '{print $6}'`
  LPARCPU=`/usr/bin/lparstat -i | grep "Maximum Capacity" | awk '{print $4}' |head -1`
  SARCPUIDLE=`echo "scale=2;100-(${CpuPhysc}/${LPARCPU}*100)" | bc | awk -F. '{print $1}'`
  PERFDATA=`echo ${SARCPU}|awk '{print "CpuUser=" $2 "; CpuSystem=" $3 "; CpuIowait=" $4 "; CpuPhysc=" $6 "; CpuEntc=" $7 "; CpuIdle=" $5":20:10"}'`
  CPU=`echo "CPU Idle = "${SARCPUIDLE}"% |" ${PERFDATA}"; LparCpuIdle="${SARCPUIDLE}"; LparCpuTotal="$LPARCPU`
 else
  echo "AIX $SYSSTATLSLPP Not Supported"
  exit 3
fi
;;
'pkginfo')
SARCPU=`/usr/bin/sar -u|grep -v Average|tail -2|head -1`
SYSSTATPKGINFO=`pkginfo -l SUNWaccu|grep VERSION|awk '{print $2}'|awk -F\. '{print $1}'`
if [ $SYSSTATPKGINFO -ge 11 ]
 then
  SARCPUIDLE=`echo ${SARCPU}|awk '{print $5}'`
  CPU=`echo ${SARCPU}|awk '{print "CPU Idle = " $5 "% | " "CpuUser=" $2 "; CpuSystem=" $3 "; CpuIowait=" $4 "; CpuIdle=" $5":20:10"}'`
 else
  echo "Solaris $SYSSTATPKGINFO Not Supported"
  exit 3
fi
;;
'pkg_info')
SARCPU=`/usr/local/bin/bsdsar -u|tail -1`
SYSSTATPKGINFO=`pkg_info | grep ^bsdsar | awk -F\- '{print $2}' | awk -F\. '{print $1}'`
if [ $SYSSTATPKGINFO -ge 1 ]
 then
  SARCPUIDLE=`echo ${SARCPU}|awk '{print $6}'`
  CPU=`echo ${SARCPU}|awk '{print "CPU Idle = " $6 "% | " "CpuUser=" $2 "; CpuSystem=" $3 "; CpuNice=" $4 "; CpuIntrpt=" $5 "; CpuIdle=" $6":20:10"}'`
 else
  echo "BSD $SYSSTATPKGINFO Not Supported"
  exit 3
fi
;;
esac

#Display CPU Performance without alert
if [ "$ALERT" == "false" ]
 then
		echo "$CPU"
		exit 0
 else
        ALERT=true
fi

#Display CPU Performance with alert
if [ ${SARCPUIDLE} -lt $2 ]
 then
		echo "CRITICAL: $CPU"
		exit 2
 elif [ $SARCPUIDLE -lt $1 ]
		 then
		  echo "WARNING: $CPU"
		  exit 1
         else
		  echo "OK: $CPU"
		  exit 0
fi

