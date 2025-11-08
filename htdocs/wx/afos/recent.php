<?php
/* Print last two days worth of some PIL */
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/forms.php";

$pil = strtoupper(substr(get_str404('pil', "AFD"), 0, 3));

$conn = iemdb("afos");
$stname = iem_pg_prepare($conn, "SELECT data from products " .
    "WHERE substr(pil,1,3) = $1 " .
    "and entered between now() - '48 hours'::interval and now() " .
    "ORDER by entered DESC");
$rs = pg_execute($conn, $stname, array($pil));

$content = "";
if (pg_num_rows($rs) < 1) {
    $content .= "ERROR: No products found in past 48 hours.";
}
while ($row = pg_fetch_assoc($rs)) {
    $d = preg_replace("/\r\r\n/", "\n", $row["data"]);
    $d = preg_replace("/\001/", "", $d);
    $d = preg_replace("/\x1e/", "", $d);
    $content .= $d;
}

header("Content-type: text/plain");
echo $content;
