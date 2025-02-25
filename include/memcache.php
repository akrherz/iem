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