<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");

$e = isset($_GET['e']) ? intval($_GET['e']) : "";
$pil = isset($_GET['pil']) ? substr($_GET['pil'],0,6) : "";
if ($e == "" && $pil == "") die();

$conn = iemdb("afos");
$ts = mktime( substr($e,8,2), substr($e,10,2), 0, 
      substr($e,4,2), substr($e,6,2), substr($e,0,4) );

$table = sprintf("products_%s_0106",   date("Y", $ts) );
if (intval(date("m",$ts)) > 6){
  $table = sprintf("products_%s_0712", date("Y", $ts) );
}


$rs = pg_prepare($conn, "SELECT", "SELECT data from $table
                 WHERE pil = $1 and entered between $2 and $3");
$rs = pg_execute($conn, "SELECT", Array($pil, date("Y-m-d H:i", $ts)."+00",
      date("Y-m-d H:i", $ts+60)."+00"));

include("$rootpath/include/header.php");

for ($i=0; $row = @pg_fetch_array($rs, $i); $i++)
{
  echo "<pre>". $row["data"] ."</pre>\n";
}

include("$rootpath/include/footer.php");
?>
