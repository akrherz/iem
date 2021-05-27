<?php
// Throttle the script kiddies.

$key = "throttle_". $_SERVER['REMOTE_ADDR'];

$memcache = new Memcached();
$memcache->setOption(Memcached::OPT_BINARY_PROTOCOL, true);
$memcache->addServer('iem-memcached', 11211);
register_shutdown_function(function() use ($memcache,$key){
    $memcache->decrement($key);
});
if ($memcache->increment($key, 1, 0, 300) > 5) {
    http_response_code(429);
    die('429: Too Many Requests');
}

?>