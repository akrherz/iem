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

if (is_null($pil) || trim($pil) == ""){
	die("No 'pil' provided by URL, it is required.");
}

$conn = iemdb("afos");

function locate_product($conn, $e, $pil, $dir){
	// Attempt to locate this product and redirect to stable URI if so
	$ts = gmmktime( substr($e,8,2), substr($e,10,2), 0,
			substr($e,4,2), substr($e,6,2), substr($e,0,4) );
	$sortdir = ($dir == 'next') ? "ASC" : "DESC";
	$sign = ($dir == 'next') ? ">": "<";
	$table = sprintf("products_%s_%s", date('Y', $ts),
		(intval(date("m", $ts)) > 6)? "0712": "0106");
	// first attempt shortcut
	$rs = pg_prepare($conn, "_LSELECT", "SELECT ".
		"entered at time zone 'UTC' as mytime from $table ".
		"WHERE pil = $1 and entered $sign $2 ".
		"ORDER by entered $sortdir LIMIT 1");
	$rs = pg_execute($conn, "_LSELECT", Array($pil,
			date("Y-m-d H:i", $ts)));
	if (pg_numrows($rs) == 0){
		// widen the net
		$rs = pg_prepare($conn, "_LSELECT2", "SELECT ".
			"entered at time zone 'UTC' as mytime from products ".
			"WHERE pil = $1 and entered $sign $2 ".
			"ORDER by entered $sortdir LIMIT 1");
		$rs = pg_execute($conn, "_LSELECT2", Array($pil,
			date("Y-m-d H:i", $ts)));
	}
	if (pg_numrows($rs) == 0) return $rs;

	$row = pg_fetch_assoc($rs, 0);
	$uri = sprintf("p.php?pil=%s&e=%s",
		$pil, date("YmdHi", strtotime($row["mytime"])));
	header("Location: $uri");
	die();
}
function last_product($conn, $pil){
	// Get the latest
	$rs = pg_prepare($conn, "_LSELECT3", "SELECT data, "
			." entered at time zone 'UTC' as mytime, source from products"
			." WHERE pil = $1 and entered > (now() - '31 days'::interval)"
			." ORDER by entered DESC LIMIT 1");
	$rs = pg_execute($conn, "_LSELECT3", array($pil));
	if (pg_numrows($rs) == 1){
		$row = pg_fetch_assoc($rs, 0);
		$uri = sprintf("p.php?pil=%s&e=%s",
			$pil, date("YmdHi", strtotime($row["mytime"])));
		header("Location: $uri");
		die();
	}
	return $rs;
}

// Okay, lets see if we can find the product we are looking for!
if (is_null($e)){
	// Option 1: We only pil= set and no time, find the last product
	$rs = last_product($conn, $pil);
}
elseif (! is_null($e) && ! is_null($dir)){
	// Option 2: We have a time set and some directionality set
	$rs	= locate_product($conn, $e, $pil, $dir);
	// if the above fails, just go to last product
	$rs = last_product($conn, $pil);
}
else {
	// Option 3: Explicit request
	$ts = gmmktime( substr($e,8,2), substr($e,10,2), 0,
			substr($e,4,2), substr($e,6,2), substr($e,0,4) );
	$rs = pg_prepare($conn, "_LSELECT", "SELECT data,
			entered at time zone 'UTC' as mytime, source, wmo from products
			WHERE pil = $1 and entered = $2");
	$rs = pg_execute($conn, "_LSELECT", Array($pil,
			date("Y-m-d H:i", $ts)));
}

$t->title = sprintf("%s from NWS %s", substr($pil,0,3), substr($pil,3,3));
$content = "<h3>National Weather Service Raw Text Product</h3>";

if (is_null($rs) || pg_numrows($rs) < 1){
	$content .= "<div class=\"alert alert-warning\">Sorry, could not find product.</div>";
}
$img = "";
for ($i=0; $row = pg_fetch_assoc($rs); $i++)
{
	if ($i == 0){
		$basets = strtotime($row["mytime"]); 
		$newe = date("YmdHi", $basets);
        $product_id = sprintf(
            "%s-%s-%s-%s", $newe, $row["source"], $row["wmo"], $pil);
		$t->twitter_description = sprintf("%s issued by NWS %s at %s UTC",
				substr($pil,0,3), substr($pil,3,3), date("d M Y H:i", $basets));
		if (substr($pil, 0, 3) == "SPS"){
            $t->twitter_image = "/plotting/auto/plot/217/pid:${product_id}.png";
            $img = <<<EOM
<p><img src="/plotting/auto/plot/217/pid:${product_id}.png" class="img img-responsive"></p>
EOM;
        } else {
            $t->twitter_image = "/wx/afos/${newe}_${pil}.png";
        }
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

$content .= $img;

$t->content = $content;
$t->render('single.phtml');
?>