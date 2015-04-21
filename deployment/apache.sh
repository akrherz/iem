#!/bin/sh
# Deployment script for apache!
SVNROOT="/mesonet/www/apps/iemwebsite"

SSLIP=$(ifconfig eth0:0 | awk -F':' '/inet addr/&&!/127.0.0.1/{split($2,_," ");print _[1]}')
if [ -z "$SSLIP"  ] 
then
	SSLIP="*"
fi

sed -e s/MYSSLIP/$SSLIP/g $SVNROOT/config/00iem-ssl.conf > /tmp/00iem-ssl.conf

cp -f $SVNROOT/config/geoserver.conf /etc/httpd/conf.d/
cp -f $SVNROOT/config/apache-vhost.conf /etc/httpd/conf.d/mesonet.inc
cp -f $SVNROOT/config/00iem.conf /etc/httpd/conf.d/
cp -f /mesonet/www/apps/weppwebsite/etc/apache_vhost.conf /etc/httpd/conf.d/wepp.conf
cp -f /mesonet/www/apps/transformingdrainage/config/apache_vhost.conf /etc/httpd/conf.d/transdrain.conf
cp -r /tmp/00iem-ssl.conf /etc/httpd/conf.d/
service httpd reload