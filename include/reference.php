<?php
/* Proxy for pyiem reference data */
require_once dirname(__FILE__) . '/../config/settings.inc.php';
require_once dirname(__FILE__) . '/memcache.php';

$cached_reference = cacheable('include_reference')(function() {
    global $INTERNAL_BASEURL;
    $ch = curl_init("{$INTERNAL_BASEURL}/json/reference.json");
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    $data = curl_exec($ch);
    curl_close($ch);
    return json_decode($data, true);
});

$reference = $cached_reference();
