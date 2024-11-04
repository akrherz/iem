<?php
/* Need something to fetch IEM Properties */
require_once dirname(__FILE__) . "/database.inc.php";

function get_iemprop($propname)
{
    $dbconn = iemdb("mesosite", true);
    $rs = pg_prepare(
        $dbconn,
        "SELECT",
        "SELECT propvalue from properties where propname = $1",
    );
    $rs = pg_execute($dbconn, "SELECT", array($propname));
    if (pg_num_rows($rs) < 1) {
        return null;
    }
    $row = pg_fetch_array($rs, 0);
    return $row["propvalue"];
}
