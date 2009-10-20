<?php
/* Giveme JSON data listing products */
require_once 'Zend/Json.php';
require_once '../../config/settings.inc.php';
require_once "$rootpath/include/database.inc.php";

$connect = iemdb("mesosite");

$result = pg_exec($connect, sprintf("SELECT * from archive_products"));

$ar = Array("products" => Array() );
for( $i=0; $row = @pg_fetch_array($result,$i); $i++)
{
  $z = Array("id" => $row["id"],
        "template" => $row["template"], 
        "name" => $row["name"], 
        "interval" => $row["interval"],
        "sts" => $row["sts"]);
  $ar["products"][] = $z;
}

echo Zend_Json::encode($ar);

?>
