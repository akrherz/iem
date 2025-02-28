<?php

class MemcacheSingleton
{
    private static $instance = null;
    private $memcache;

    private function __construct()
    {
        $this->memcache = new Memcached();
        // Belief is that this is safe for all intended usage
        $this->memcache->setOption(Memcached::OPT_BINARY_PROTOCOL, true);
        $this->memcache->addServer('iem-memcached', 11211);
    }

    public static function getInstance()
    {
        if (self::$instance == null) {
            self::$instance = new MemcacheSingleton();
        }

        return self::$instance->memcache;
    }
}

function cacheable($cacheKeyPrefix, $cacheDuration = 3600) {
    return function ($func) use ($cacheKeyPrefix, $cacheDuration) {
        return function (...$args) use ($func, $cacheKeyPrefix, $cacheDuration) {
            try {
                $memcache = MemcacheSingleton::getInstance();
                $mckey = $cacheKeyPrefix . implode('_', $args);
                $val = $memcache->get($mckey);
            } catch (Exception $e) {
                // log error
                openlog("IEM", LOG_PID | LOG_PERROR, LOG_LOCAL0);
                syslog(LOG_ERR, "memcache error: " . $e->getMessage());
                closelog();
                $val = null;
            }
            if ($val) {
                return $val;
            }
            $result = $func(...$args);
            try{
                $memcache->set($mckey, $result, $cacheDuration);
            } catch (Exception $e) {
                // log error
                openlog("IEM", LOG_PID | LOG_PERROR, LOG_LOCAL0);
                syslog(LOG_ERR, "memcache error: " . $e->getMessage());
                closelog();
                // ignore
            }
            return $result;
        };
    };
}