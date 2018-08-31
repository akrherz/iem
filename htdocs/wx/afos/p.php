<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/myview.php";
$t = new MyView();

define("IEM_APPID", 47);
$t->thispage = "archive-afos";

$e = isset($_GET['e']) ? intval($_GET['e']) : null;
$pil = isset($_GET['pil']) ? strtoupper(substr($_GET['pil'],0,6)) : null;
$dir = isset($_REQUEST['dir']) ? $_REQUEST['dir'] : null;

if ($pil == null || trim($pil) == ""){
	die("No 'pil' provided by URL, it is required.");
}

$conn = iemdb("afos");

// Okay, lets see if we can find the product we are looking for!
if ($e == null){
	$rs = pg_prepare($conn, "_LSELECT", "SELECT data, "
			." entered at time zone 'UTC' as mytime, source from products"
			." WHERE pil = $1 and entered > (now() - '31 days'::interval)"
			." ORDER by entered DESC LIMIT 1");
	$rs = pg_execute($conn, "_LSELECT", array($pil));
} else {
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
	$ts = gmmktime( substr($e,8,2), substr($e,10,2), 0,
			substr($e,4,2), substr($e,6,2), substr($e,0,4) );
	$rs = pg_prepare($conn, "_LSELECT", "SELECT data,
			entered at time zone 'UTC' as mytime, source from products
			WHERE pil = $1 and entered between $2 and $3
			ORDER by entered $sortdir LIMIT 100");
	$rs = pg_execute($conn, "_LSELECT", Array($pil,
			date("Y-m-d H:i", $ts+$offset0),
			date("Y-m-d H:i", $ts+$offset1)));
}

$t->title = sprintf("%s from NWS %s", substr($pil,0,3), substr($pil,3,3));
$content = "<h3>National Weather Service Raw Text Product</h3>";

if (pg_numrows($rs) < 1){
	$content .= "<div class=\"alert alert-warning\">Sorry, could not find product.</div>";
}
for ($i=0; $row = @pg_fetch_assoc($rs, $i); $i++)
{
	if ($i == 0){ 
		$basets = strtotime($row["mytime"]); 
		$newe = date("YmdHi", $basets);
		$t->twitter_description = sprintf("%s issued by NWS %s at %s UTC",
				substr($pil,0,3), substr($pil,3,3), date("d M Y H:i", $basets));
		$t->twitter_image = "/wx/afos/${newe}_${pil}.png";
		$t->twitter_card = "summary_large_image";
		$dstamp = date("Y-m-d H:i", $basets);
		$listlink = sprintf("list.phtml?source=%s&amp;day=%s&amp;month=%s&amp;year=%s", 
				$row["source"], date("d", $basets), date("m", $basets), 
				date("Y", $basets));
		$date2 =  date("d M Y", $basets);
		$content .= <<<EOF
<div class="row">
<div class="col-sm-12">
<p>Displaying AFOS PIL: <strong>$pil</strong> 
Received: <strong>{$dstamp} UTC</strong>
</div>
</div>

<div class="row">
<div class="col-sm-2">
<a rel="nofollow" class="btn btn-primary" 
	href="p.php?dir=prev&pil=$pil&e=$newe"><i class="fa fa-arrow-left"></i> 
	Previous in Time</a>
</div>
<div class="col-sm-4">
	<a rel="nofollow" class="btn btn-primary" 
	href="{$listlink}">View All {$row["source"]} Products for {$date2}</a>
</div>
<div class="col-sm-2">
	<a rel="nofollow" class="btn btn-primary" 
	href="p.php?dir=next&pil=$pil&e=$newe">Next in Time <i class="fa fa-arrow-right"></i></a>
</div>
<div class="col-sm-4">
	<a rel="nofollow" class="btn btn-primary" 
	href="p.php?pil=$pil">Latest Product</a>
	<a rel="nofollow" class="btn btn-primary" 
	href="{$t->twitter_image}">View As Image</a>
</div>
</div><!-- ./row -->
EOF;
		
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