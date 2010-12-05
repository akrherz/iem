<?php
include("../../config/settings.inc.php");
/* I produce maps for a given ID
 * 
 */
include("$rootpath/include/database.inc.php");
$mesosite = iemdb('mesosite');
$rs = pg_prepare($mesosite, "SELECT", "SELECT * from iemmaps" .
		" WHERE id = $1");

$id = isset($_GET['id']) ? intval($_GET['id']) : die();

$rs = pg_execute($mesosite, "SELECT", Array($id));
$row = pg_fetch_array($rs, 0);

include("$rootpath/include/header.php");

echo sprintf("<h3>%s</h3>", $row["title"]);

include("$rootpath/include/footer.php");
?>