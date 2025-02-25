<?php

class MemcacheSingleton
{
    private static $instance = null;
    private $memcache;

    private function __construct()
    {
        $this->memcache = new Memcached();
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