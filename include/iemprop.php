<?php
/* Need something to fetch IEM Properties */
require_once dirname(__FILE__) . "/database.inc.php";
require_once dirname(__FILE__) . "/memcache.php";

$cached_get_iemprop = cacheable("iemprop", 120)(function($propname)
{
    $dbconn = iemdb("mesosite");
    $stname = iem_pg_prepare(
        $dbconn,
        "SELECT propvalue from properties where propname = $1",
    );
    $rs = pg_execute($dbconn, $stname, array($propname));
    if (pg_num_rows($rs) < 1) {
        return null;
    }
    $row = pg_fetch_assoc($rs, 0);
    return $row["propvalue"];
});

// Proxy to the cached function
function get_iemprop($propname)
{
    global $cached_get_iemprop;
    return $cached_get_iemprop($propname);
}