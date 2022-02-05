<?php 
/* 
 * Giveme JSON data listing products  
 */

header('Content-type: application/json; charset=utf-8');
require_once '../../config/settings.inc.php';
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";

$connect = iemdb("mesosite");

/* Standard Issue Products :) */
$result = pg_exec(
    $connect,
    "SELECT * from archive_products ORDER by groupname, name",
);

$ar = Array("products" => Array() );
for( $i=0; $row = pg_fetch_assoc($result); $i++)
{
  $z = Array("id" => $row["id"],
        "template" => $row["template"], 
        "name" => $row["name"], 
        "groupname" => $row["groupname"], 
        "interval" => $row["interval"],
        "time_offset" => $row["time_offset"],
  		"avail_lag"	=> $row["avail_lag"],
        "sts" => substr($row["sts"],0,10));
  $ar["products"][] = $z;
}

/* Now, lets get webcam stuff */
$result = pg_exec($connect, "SELECT * from webcams WHERE 
          network != 'IDOT' ORDER by network, name");

for( $i=0; $row = pg_fetch_assoc($result); $i++)
{
  $tpl = sprintf("https://mesonet.agron.iastate.edu/archive/data/%%Y/%%m/%%d/".
  		"camera/%s/%s_%%Y%%m%%d%%H%%i.jpg", $row["id"],
         $row["id"]);
  $z = Array("id" => $row["id"],
        "template" => $tpl,
        "groupname" => $row["network"] ." Webcams",
        "name" => $row["name"], 
        "interval" => 5,
        "time_offset" => 0,
  		"avail_lag"	=> 0,
        "sts" => substr($row["sts"],0,10));
  $ar["products"][] = $z;
}

$json = json_encode($ar);

// JSON if no callback
if( ! isset($_REQUEST['callback']))
	exit( $json );

$cb = xssafe($_REQUEST['callback']);
echo "{$cb}($json)";
