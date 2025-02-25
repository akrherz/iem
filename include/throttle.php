<?php
// Throttle the script kiddies.
require_once __DIR__ . '/mlib.php';

$client_ip = getClientIp();
$key = "throttle_{$client_ip}";

// Need to do a custom memcache with BinaryProtocol
$lmemcache = new Memcached();
$lmemcache->setOption(Memcached::OPT_BINARY_PROTOCOL, true);
$lmemcache->addServer('iem-memcached', 11211);
register_shutdown_function(function () use ($lmemcache, $key) {
    $lmemcache->decrement($key);
});
if ($lmemcache->increment($key, 1, 0, 300) > 5) {
    http_response_code(429);
    die('429: Too Many Requests');
}
