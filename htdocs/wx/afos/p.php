<?php
include("../../../config/settings.inc.php");
define("IEM_APPID", 47);
include("$rootpath/include/database.inc.php");
$THISPAGE = "archive-afos";
include("$rootpath/include/header.php");

$e = isset($_GET['e']) ? intval($_GET['e']) : "201112151144";
$pil = isset($_GET['pil']) ? substr($_GET['pil'],0,6) : "AFDDMX";
$dir = isset($_REQUEST['dir']) ? $_REQUEST['dir'] : null;

$conn = iemdb("afos");
$ts = mktime( substr($e,8,2), substr($e,10,2), 0, 
      substr($e,4,2), substr($e,6,2), substr($e,0,4) );

$table = sprintf("products_%s_0106",   date("Y", $ts) );
if (intval(date("m",$ts)) > 6){
  $table = sprintf("products_%s_0712", date("Y", $ts) );
}
if ($dir == 'next'){
	$sortdir = "ASC";
	$offset0 = 60;
	$offset1 = 5*86400;
} else if ($dir == 'prev'){
	$sortdir = "DESC";
	$offset0 = -5*86400;
	$offset1 = -1;
} else {
	$sortdir = "ASC";
	$offset0 = 0;
	$offset1 = 60;
}

$rs = pg_prepare($conn, "_LSELECT", "SELECT data, 
				entered at time zone 'UTC' as mytime, source from $table
                 WHERE pil = $1 and entered between $2 and $3
                 ORDER by entered $sortdir LIMIT 10");
$rs = pg_execute($conn, "_LSELECT", Array($pil, 
	date("Y-m-d H:i", $ts+$offset0)."+00",
	date("Y-m-d H:i", $ts+$offset1)."+00"));


echo "<h3>National Weather Service Raw Text Product</h3>";
if (pg_numrows($rs) < 1){
	echo "<div class=\"warning\">Sorry, could not find product.</div>";
}
for ($i=0; $row = @pg_fetch_assoc($rs, $i); $i++)
{
	if ($i == 0){ 
		$basets = strtotime($row["mytime"]); 
		$newe = date("YmdHi", $basets);
		echo "<p>Displaying AFOS PIL: <strong>$pil</strong> Received: <strong>". date("Y-m-d H:i", $basets) ." UTC</strong>";
		echo "<div class=\"buttons\"><a class=\"button down\" href=\"p.php?dir=prev&pil=$pil&e=$newe\">Previous in Time</a>";
		echo sprintf("<a class=\"button save\" href=\"list.phtml?source=%s&day=%s&month=%s&year=%s\">View All %s Products for %s</a>", 
		$row["source"], date("d", $basets), date("m", $basets), 
		date("Y", $basets), $row["source"], date("d M Y", $basets) );
		echo "<a class=\"button up\" href=\"p.php?dir=next&pil=$pil&e=$newe\">Next in Time</a></div>";
		echo "<br clear=\"both\" />";
	}
	if (strtotime($row["mytime"]) != $basets){ continue; }
	if (preg_match('/xml/', $row["data"]) > 0){
      echo "<pre>". $row["data"] ."</pre>\n";
	} else {
		echo "<pre>". htmlentities($row["data"]) ."</pre>\n";
	}
}

include("$rootpath/include/footer.php");
?>
