IEM Webfarm Installation Notes
===

On 8 Nov 2019, a journey was embarked to upgrade the IEM webfarm nodes to RHEL8.1.
This document details the fun and what magic I needed to do.

Local configuration variances
-----

php-fpm needs to consider `.phtml` files for PHP consumption.  In `/etc/php-fpm.d/iem.conf`.

    [www]
    security.limit_extensions = .php .phtml

PHP should save sessions in memcached. In `/etc/php.ini`.

    ; Point php.ini at memcache for sessions
    [Session]
    session.save_handler = memcache
    session.save_path = "tcp://iem-memcached:11211"

Extra RPMs necessary
-----

    yum module enable mod_auth_openidc
    yum -y install nrpe nagios-plugins-disk php-pecl-memcached mod_fcgid \
    php-pgsql php-xml php-pecl-msgpack php-pdo php-gd php-mbstring php-json \ php-pecl-igbinary php-cli fcgi liberation-mono-fonts \
    perl-Monitoring-Plugin perl-Readonly liberation-fonts \
    liberation-sans-fonts liberation-serif-fonts mod_ssl mod_wsgi mod_auth_openidc

- edit security.limit_extensions to include .phtml in /etc/php-fpm.d/www.conf
- add /etc/httpd/conf.d/server-status.conf
- add /etc/systemd/system/httpd.service.d/override.conf￼￼￼￼
- set /etc/httpd/conf.modules.d/10-wsgi-python3.conf WSGIApplicationGroup %{GLOBAL}- use conda mod_wsgi
- update `directory /` setting in httpd.conf
