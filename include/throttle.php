<?php
// Throttle the script kiddies.
require_once __DIR__ . '/mlib.php';
require_once __DIR__ . '/memcache.php';

// check if THROTTLE_APP is defined and use it as the key, if so
if (defined("THROTTLE_APP")) {
    $key = sprintf("throttle/%s", THROTTLE_APP);
} else {
    $key = getClientIp();
}

// Need to do a custom memcache with BinaryProtocol
$memcache = MemcacheSingleton::getInstance();
register_shutdown_function(function () use ($memcache, $key) {
    $memcache->decrement($key);
});
if ($memcache->increment($key, 1, 0, 300) > 5) {
    http_response_code(429);
    die('429: Too Many Requests');
}
