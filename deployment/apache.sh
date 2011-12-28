#!/bin/sh
# Deployment script for apache!
SVNROOT="/mesonet/www/apps/iemwebsite"

cp -r $SVNROOT/config/apache-vhost.conf /etc/httpd/conf.d/mesonet.inc
service httpd reload