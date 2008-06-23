<?php
include("../config/settings.inc.php");
include("$rootpath/include/database.inc.php");

$id = isset($_GET['id']) ? intval($_GET['id']) : "";
$pid = isset($_GET['pid']) ? substr($_GET['pid'],0,32) : "";
if ($id == "" && $pid == "") die();

$conn = iemdb("postgis");

if ($id != "") {
 pg_query($conn, "update text_products SET reads = reads + 1 WHERE id = $id");
 $sql = sprintf('SELECT product,geom from text_products WHERE id = %s', $id);
} else {
 pg_query($conn, "update text_products SET reads = reads + 1 WHERE product_id = '$pid'");
 $sql = sprintf("SELECT product,geom from text_products WHERE product_id = '%s'", $pid);
}

$rs = pg_query($conn, $sql);
//header("Content-type: text/plain");
for ($i=0; $row = @pg_fetch_array($rs, $i); $i++)
{
  echo "<pre>". $row["product"] ."</pre>\n";
  if ($row["geom"] != ""){  echo "<p><img src=\"GIS/radmap.php?pid=$pid\">"; }
}

?>

