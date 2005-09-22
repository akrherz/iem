<?php
include("../config/settings.inc.php");
include("$rootpath/include/database.inc.php");

$id = isset($_GET['id']) ? intval($_GET['id']) : die('no id');

$conn = iemdb("postgis");

pg_query($conn, "update text_products SET reads = reads + 1 WHERE id = $id");
$sql = sprintf('SELECT product from text_products WHERE id = %s', $id);

$rs = pg_query($conn, $sql);

$row = pg_fetch_array($rs, 0);

echo "<pre>". $row["product"] ."</pre>";

?>

