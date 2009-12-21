<?php
/* Giveme JSON data listing products */
require_once 'Zend/Json.php';
require_once '../../config/settings.inc.php';
require_once "$rootpath/include/database.inc.php";

$connect = iemdb("mesosite");

/* Standard Issue Products :) */
$result = pg_exec($connect, sprintf("SELECT * from archive_products ORDER by groupname, name"));

$ar = Array("products" => Array() );
for( $i=0; $row = @pg_fetch_array($result,$i); $i++)
{
  $z = Array("id" => $row["id"],
        "template" => $row["template"], 
        "name" => $row["name"], 
        "groupname" => $row["groupname"], 
        "interval" => $row["interval"],
        "time_offset" => $row["time_offset"],
        "sts" => substr($row["sts"],0,10));
  $ar["products"][] = $z;
}

/* Now, lets get webcam stuff */
$result = pg_exec($connect, sprintf("SELECT * from webcams WHERE 
          network != 'IDOT' ORDER by network, name"));

for( $i=0; $row = @pg_fetch_array($result,$i); $i++)
{
  $tpl = sprintf("http://mesonet.agron.iastate.edu/archive/data/%%Y/%%m/%%d/camera/%s/%s_%%Y%%m%%d%%H%%i.jpg", $row["id"],
         $row["id"]);
  $z = Array("id" => $row["id"],
        "template" => $tpl,
        "groupname" => $row["network"] ." Webcams",
        "name" => $row["name"], 
        "interval" => 5,
        "time_offset" => 0,
        "sts" => substr($row["sts"],0,10));
  $ar["products"][] = $z;
}


echo Zend_Json::encode($ar);

?>
