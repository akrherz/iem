<?php
/*
 * Database connection function that most every script uses :)
 */

// Helper to get a dbconn string
function get_dbconn_str($dbname)
{
    return sprintf(
        "dbname=%s host=iemdb-%s.local user=nobody gssencmode=disable connect_timeout=5",
        $dbname,
        $dbname
    );
}
/*
 * Help function that yields database connections
 */
function iemdb($dbname)
{
    $connstr = get_dbconn_str($dbname);
    $db = pg_connect($connstr);
    if (!$db) {
        // Try once more
        $db = pg_connect($connstr);
    }
    if (!$db) {
        // Send a HTTP try again later
        header("HTTP/1.1 503 Service Unavailable");
        die("Could not connect to database: $dbname");
    }
    return $db;
}
