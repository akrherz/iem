<?php
/*
 * Database connection function that most every script uses :)
 */

function database_failure($DBKEY)
{
    echo sprintf("<div class='warning'>Unable to contact database: %s</div>", $DBKEY);
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
function iemdb($dbname, $flags = 0, $rw = FALSE)
{
    $connstr = get_dbconn_str($dbname);
    $db = pg_connect($connstr, $flags);
    if (!$db) {
        // Try once more
        $db = pg_connect($connstr, $flags);
    }
    if (!$db) {
        database_failure($dbname);
    }
    return $db;
}
