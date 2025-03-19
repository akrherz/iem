<?php
// Avoid circular includes here!

/**
 * Prepare a query, die if it fails
 * @param PgSql\Connection $dbconn database connection
 * @param string $sql SQL query
 * @return string the statement name
 */
function iem_pg_prepare($dbconn, $sql)
{
    $stname = uniqid();
    $res = pg_prepare($dbconn, $stname, $sql);
    if ($res === FALSE) {
        // Thought here is that erroring here is likely a code bug that 
        // should be fixed, so we die here.
        http_response_code(500);
        error_log(pg_last_error($dbconn));
        die("Aborting, failed to prepare database query.");
    }
    return $stname;
}

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
