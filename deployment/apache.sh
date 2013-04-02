#!/bin/sh
# Deployment script for apache!
SVNROOT="/mesonet/www/apps/iemwebsite"

cp -r $SVNROOT/config/apache-vhost.conf /etc/httpd/conf.d/mesonet.inc
cp -r $SVNROOT/config/00iem.conf /etc/httpd/conf.d/
# TODO fix bind port!
#cp -r $SVNROOT/config/00iem-ssl.conf /etc/httpd/conf.d/
service httpd reload