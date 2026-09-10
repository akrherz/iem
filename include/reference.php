<?php
// Proxy for pyiem reference data
require_once dirname(__FILE__) . '/../config/settings.inc.php';
require_once dirname(__FILE__) . '/memcache.php';
require_once dirname(__FILE__) . '/mlib.php';

/**
 * Get the pyiem reference dictionary, memcached for performance.
 * @return array<string, mixed>
 */
function get_reference(): array
{
    // Cache the reference data in a static variable to avoid repeated lookups
    // within the same single request.
    static $reference = null;
    if ($reference === null) {
        $cached_reference = cacheable('include_reference')(function () {
            return require_json_response("/json/reference.json", array());
        });
        $reference = $cached_reference();
    }
    return $reference;
}

