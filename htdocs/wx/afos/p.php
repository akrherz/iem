<?php
include("../../../config/settings.inc.php");
include("../../../include/database.inc.php");
include("../../../include/myview.php");
$t = new MyView();

define("IEM_APPID", 47);
$t->thispage = "archive-afos";

$e = isset($_GET['e']) ? intval($_GET['e']) : "201112151144";
$pil = isset($_GET['pil']) ? strtoupper(substr($_GET['pil'],0,6)) : "AFDDMX";
$dir = isset($_REQUEST['dir']) ? $_REQUEST['dir'] : null;

$t->title = sprintf("%s from NWS %s", substr($pil,0,3), substr($pil,3,3));
$t->twitter_image = "http://mesonet.agron.iastate.edu/content/pil_${pil}.png";

$conn = iemdb("afos");
$ts = gmmktime( substr($e,8,2), substr($e,10,2), 0, 
      substr($e,4,2), substr($e,6,2), substr($e,0,4) );

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
				entered at time zone 'UTC' as mytime, source from products
                 WHERE pil = $1 and entered between $2 and $3
                 ORDER by entered $sortdir LIMIT 100");
$rs = pg_execute($conn, "_LSELECT", Array($pil, 
	date("Y-m-d H:i", $ts+$offset0),
	date("Y-m-d H:i", $ts+$offset1)));


$content = "<h3>National Weather Service Raw Text Product</h3>";
if (pg_numrows($rs) < 1){
	$content .= "<div class=\"alert alert-warning\">Sorry, could not find product.</div>";
}
for ($i=0; $row = @pg_fetch_assoc($rs, $i); $i++)
{
	if ($i == 0){ 
		$basets = strtotime($row["mytime"]); 
		$newe = date("YmdHi", $basets);
		$content .= "<p>Displaying AFOS PIL: <strong>$pil</strong> Received: <strong>". date("Y-m-d H:i", $basets) ." UTC</strong>";
		$content .= "<br /><a class=\"btn btn-primary\" href=\"p.php?dir=prev&pil=$pil&e=$newe\"><i class='glyphicon glyphicon-arrow-left'></i> Previous in Time</a>";
		$content .= sprintf(" <a class=\"btn btn-primary\" href=\"list.phtml?source=%s&day=%s&month=%s&year=%s\">View All %s Products for %s</a>", 
		$row["source"], date("d", $basets), date("m", $basets), 
		date("Y", $basets), $row["source"], date("d M Y", $basets) );
		$content .= " <a class=\"btn btn-primary\" href=\"p.php?dir=next&pil=$pil&e=$newe\">Next in Time <i class='glyphicon glyphicon-arrow-right'></i></a></div>";
		$content .= "<br clear=\"both\" />";
	}
	if (strtotime($row["mytime"]) != $basets){ continue; }
	$d = preg_replace("/\r\r\n/", "\n", $row["data"]);
	if (preg_match('/xml/', $row["data"]) > 0){
        $content .= "<pre>". $d ."</pre>\n";
	} else {
		$content .= "<pre>". htmlentities($d) ."</pre>\n";
	}
}

$t->content = $content;
$t->render('single.phtml');
?>