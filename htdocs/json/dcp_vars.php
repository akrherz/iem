<?php
/* We need a JSON listing of variables this site reports with! */
require_once 'Zend/Json.php';
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$hads = iemdb('hads');
$table = sprintf("raw%s_%s", date("Y"), date("m"));
$rs = pg_prepare($hads, "SELECT", "SELECT distinct key from $table " .
		"WHERE station = $1");

$station = isset($_REQUEST["station"]) ? $_REQUEST["station"] : die('No Station'); 

$rs = pg_execute($hads, "SELECT", Array($station));

$ar = Array("vars"=> Array());

for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $z = Array("id"=>$row["key"]);
  $ar["vars"][] = $z;
}

echo Zend_Json::encode($ar);
?>