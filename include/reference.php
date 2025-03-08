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
    $res = json_decode($data, true);
    if (is_null($res)) {
        http_response_code(503);
        die("FATAL: Failed to fetch reference data");
    }
    return $res;
});

$reference = $cached_reference();
