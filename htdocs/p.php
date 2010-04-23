<?php
/* Simple program to simply print out a product, if the product has a 
 * geometry, present it in a map as well.  iembot generates links to this
 * app
 */
include("../config/settings.inc.php");
include("$rootpath/include/database.inc.php");

$id = isset($_GET['id']) ? intval($_GET['id']) : "";
$pid = isset($_GET['pid']) ? substr($_GET['pid'],0,32) : "";
if ($id == "" && $pid == "") die();

$conn = iemdb("postgis");

if ($id != "") {
 $rs = pg_prepare($conn, "IDUPDATE", "update text_products 
                 SET reads = reads + 1 WHERE id = $1");
 $rs = pg_prepare($conn, "IDSELECT", "SELECT product,geom from text_products 
                 WHERE id = $1");
 pg_execute($conn, "IDUPDATE", Array($id));
 $rs = pg_execute($conn, "IDSELECT", Array($id));
} else {
 $rs = pg_prepare($conn, "PIDUPDATE", "update text_products 
                 SET reads = reads + 1 WHERE product_id = $1");
 $rs = pg_prepare($conn, "PIDSELECT", "SELECT product,geom from text_products 
                 WHERE product_id = $1");
 pg_execute($conn, "PIDUPDATE", Array($pid));
 $rs = pg_execute($conn, "PIDSELECT", Array($pid));
}

include("$rootpath/include/header.php");

for ($i=0; $row = @pg_fetch_array($rs, $i); $i++)
{
  echo "<pre>". $row["product"] ."</pre>\n";
  if ($row["geom"] != ""){  echo "<p><img src=\"GIS/radmap.php?pid=$pid\">"; }
}

include("$rootpath/include/footer.php");
?>
