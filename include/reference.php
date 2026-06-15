<?php
/* Proxy for pyiem reference data */
require_once dirname(__FILE__) . '/../config/settings.inc.php';
require_once dirname(__FILE__) . '/memcache.php';
require_once dirname(__FILE__) . '/mlib.php';

$cached_reference = cacheable('include_reference')(function() {
    return require_json_response("/json/reference.json", array());
});

$reference = $cached_reference();
