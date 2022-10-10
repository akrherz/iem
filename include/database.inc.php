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
function iemdb($dbname, $force_new = 0, $rw = FALSE)
{
    $connstr = get_dbconn_str($dbname);
    $db = pg_connect($connstr, $force_new);
    if (!$db) {
        // Try once more
        $db = pg_connect($connstr, $force_new);
    }
    if (!$db) {
        database_failure($dbname);
    }
    return $db;
} // End of iemdb()
