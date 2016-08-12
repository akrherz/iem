#!/bin/sh
# Deployment script for apache!
SVNROOT="/mesonet/www/apps/iemwebsite"

cp -f $SVNROOT/config/geoserver.conf /etc/httpd/conf.d/
cp -f $SVNROOT/config/backend-vhost.conf /etc/httpd/conf.d/backend.conf
cp -f $SVNROOT/config/mesonet.inc /etc/httpd/conf.d/mesonet.inc
cp -f $SVNROOT/config/00iem.conf /etc/httpd/conf.d/
cp -f /mesonet/www/apps/weppwebsite/etc/apache_vhost.conf /etc/httpd/conf.d/wepp.conf
cp -r $SVNROOT/config/00iem-ssl.conf /etc/httpd/conf.d/
service httpd reload