#!/bin/sh
# This script assembles all the various apache configs provided by this
# project and others for usage by an IEM webfarm node

APPS="/mesonet/www/apps"
CONFD="/etc/httpd/conf.d/"

cp -f /opt/iem/deployment/apache_configs/*.conf $CONFD

cp -f /opt/dep/config/apache-vhost.conf $CONFD/idep.conf
cp -f $APPS/weather.im/config/weather-im-vhost.conf $CONFD
cp -f /opt/iem/config/mesonet.inc $CONFD
cp -f /opt/iem/config/00iem.conf $CONFD
cp -f /opt/iem/config/00iem-ssl.conf $CONFD
cp -f $APPS/vendor/conf/vendor.conf $CONFD
cp -f $APPS/weppwebsite/etc/apache_vhost.conf $CONFD/wepp.conf
cp -f $APPS/cocorahs/config/apache-vhost.conf $CONFD/cocorahs.conf
cp -f $APPS/nwnwebsite/deployment/schoolnet8-vhost.conf $CONFD/iem-schoolnet8.conf
echo "Header set X-IEM-ServerID $(hostname)" > $CONFD/iemvs.conf

echo "=== datateam.conf, clients.conf one-offs ATTM ==="
# Finally, reload httpd
systemctl reload httpd