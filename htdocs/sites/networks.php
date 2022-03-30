<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 6);
require_once "../../include/database.inc.php";
require_once "../../include/myview.php";
require_once "../../include/forms.php";
require_once "../../include/imagemaps.php";
require_once "../../include/network.php";

$pgconn = iemdb("mesosite");

$network = isset($_GET['network']) ? xssafe($_GET['network']): 'IA_ASOS';

function attrs2str($arr){
    $s = "";
    if (is_array($arr)) { 
        foreach($arr as $key => $value){
            $s .= sprintf("%s=%s<br />", $key, $value);
        }
    }
    return $s;
}
function pretty_date($val){
    if ($val === null){
        return "";
    }
    if (is_string($val)){
        $val = strtotime($val);
    }
    return date("M d, Y", $val);
}

if ($network == '_ALL_'){
	$rs = pg_query(
        $pgconn,
        "SELECT id, name, elevation, archive_begin, archive_end, network, ".
        "ST_x(geom) as lon, ST_y(geom) as lat, null as attributes, state, ".
        "synop, country from stations WHERE online = 'y' ORDER by name");
    $cities = Array();
    for ($i=0; $row = pg_fetch_array($rs); $i++) {
        $cities[$row["id"]] = $row;
    }
} else if (isset($_GET["special"]) && $_GET["special"] == 'allasos'){
	$rs = pg_query(
        $pgconn,
        "SELECT id, name, elevation, archive_begin, archive_end, network, ".
        "ST_x(geom) as lon, ST_y(geom) as lat, null as attributes, state, ".
        "synop, country from stations WHERE online and ".
        "network ~* 'ASOS' ORDER by name");
    $cities = Array();
    for ($i=0; $row = pg_fetch_array($rs); $i++) {
        $cities[$row["id"]] = $row;
    }
} else {
	$nt = new NetworkTable($network);
    $cities = $nt->table;
}

$format = isset($_GET['format']) ? xssafe($_GET['format']): 'html';
$nohtml = isset($_GET['nohtml']);

$table = "";
if (strlen($network) > 0){
	if ($format == "html"){
		$table .= "<p><table class=\"table table-striped\">\n";
		$table .= "<caption><b>". $network ." Network</b></caption>\n";
		$table .= <<<EOM
<thead>
<tr>
<th>ID</th><th>Station Name</td><th>Latitude<sup>1</sup></th>
<th>Longitude<sup>1</sup></th><th>Elevation [m]</th>
<th>Archive Begins</th><th>Archive Ends</th><th>IEM Network</th>
<th>Attributes</th>
</tr>
</thead>
EOM;
		foreach($cities as $sid => $row) {
			$table .= "<tr>\n
			  <td><a href=\"site.php?station={$sid}&amp;network=". $row["network"] ."\">{$sid}</a></td>
			  <td>". $row["name"] ."</td>
			  <td>". round($row["lat"],5) . "</td>
			  <td>". round($row["lon"],5) . "</td>
			  <td>". $row["elevation"]. "</td>
			  <td>". pretty_date($row["archive_begin"]) . "</td>
			  <td>". pretty_date($row["archive_end"]) . "</td>
			  <td><a href=\"locate.php?network=". $row["network"] ."\">". $row["network"]. "</a></td>
			  <td>". attrs2str($row["attributes"]) ."</td>
              </tr>";
		}
		$table .= "</table>\n";

	} else if ($format == "csv") {
		if (! $nohtml) $table .= "<p><b>". $network ." Network</b></p>\n";
		if (! $nohtml) $table .= "<pre>\n";
		$table .= "stid,station_name,lat,lon,elev,begints,iem_network\n";
		foreach ($cities as $sid => $row) {
			$table .= $sid .","
					. $row["name"] .","
					. round($row["lat"],5). ","
					. round($row["lon"],5). ","
					. $row["elevation"]. ","
					. $row["archive_begin"]. ","
					. $row["network"]. "\n";
		}
		if (! $nohtml)  $table .= "</pre>\n";
	}
	else if ($format == "shapefile") {

		/* Create SHP,DBF bases */
		$filePre = "${network}_locs";
		if (! is_file("/var/webtmp/{$filePre}.zip")){
			$shpFname = "/var/webtmp/$filePre";
			@unlink($shpFname.".shp");
			@unlink($shpFname.".shx");
			@unlink($shpFname.".dbf");
			@unlink($shpFname.".zip");
			$shpFile = ms_newShapeFileObj($shpFname, MS_SHP_POINT);
			$dbfFile = dbase_create( $shpFname.".dbf", array(
					array("ID", "C", 6),
					array("NAME", "C", 50),
					array("NETWORK","C",20),
					array("BEGINTS","C",16),
			));
	
			foreach ($cities as $sid => $row) {
				$pt = ms_newPointobj();
				$pt->setXY( $row["lon"], $row["lat"], 0);
				$shpFile->addPoint($pt);
	
				dbase_add_record($dbfFile, array(
					$row["id"],
					$row["name"],
					$row["network"],
					substr($row["archive_begin"],0,16)));
			}
			unset($shpFile);
			dbase_close($dbfFile);
			chdir("/var/webtmp/");
			copy("/opt/iem/data/gis/meta/4326.prj", $filePre.".prj");
			popen("zip ".$filePre.".zip ".$filePre.".shp ".$filePre.".shx ".$filePre.".dbf ".$filePre.".prj", 'r');
		}
		$table .= "Shapefile Generation Complete.<br>";
		$table .= "Please download this <a href=\"/tmp/".$filePre.".zip\">zipfile</a>.";
		chdir("/opt/iem/htdocs/sites/");
}
else if ($format == "awips") {
	if (! $nohtml) $table .= "<pre>\n";
	foreach ($cities as $sid => $row) {
		$table .= sprintf("%s|%s|%-30s|%4.1f|%2.5f|%3.5f|GMT|||1||||\n", $row["id"], $row["id"], $row["name"], $row["elevation"], $row["lat"], $row["lon"]);
	} // End of for
	if (! $nohtml) $table .= "</pre>\n";
}

else if ($format == "madis") {
	if (! $nohtml) $table .= "<pre>\n";

	foreach ($cities as $sid => $row) {
		if (substr($row["network"],0,4) == "KCCI") $row["network"] = "KCCI-TV";
		if (substr($row["network"],0,4) == "KELO") $row["network"] = "KELO-TV";
		if (substr($row["network"],0,4) == "KIMT") $row["network"] = "KIMT-TV";
		$table .= sprintf("%s|%s|%-39s%-11s|%4.1f|%2.5f|%3.5f|GMT|||1||||\n", $row["id"], $row["id"], $row["name"], $row["network"], $row["elevation"], $row["lat"], $row["lon"]);
	} // End of for
	if (! $nohtml) $table .= "</pre>\n";
}

else if ($format == "gempak") {
	if (! $nohtml) $table .= "<pre>\n";
	foreach ($cities as $sid => $row) {
		$table .= str_pad($row["id"], 9)
		.  str_pad($row["synop"], 7)
		.  str_pad($row["name"], 33)
		.  str_pad($row["state"], 3)
		.  str_pad($row["country"], 2)
		.  sprintf("%6.0f", $row["lat"] * 100)
		.  sprintf("%7.0f", $row["lon"] * 100)
		.  sprintf("%6.0f", $row["elevation"])
		. "\n";
	}
	if (! $nohtml) $table .= "</pre>\n";
}
}


if (! $nohtml || $format == 'shapefile') {
	$t = new MyView();	
	$t->title = "Network Station Tables";
	$page = 'full.phtml';
	$sextra = "";
	if (isset($_REQUEST['station'])){
		$t->sites_current = "tables";
		include("setup.php");
		$page = 'sites.phtml';
		$sextra = sprintf("<input type=\"hidden\" value=\"%s\" name=\"station\">",
			xssafe($_REQUEST["station"]));
	}

	$ar = Array(
		"html" => "HTML Table",
		"csv" => "Comma Delimited",
		"shapefile" => "ESRI Shapefile",
		"gempak" => "GEMPAK Station Table",
		"awips" => "AWIPS Station Table",
		"madis" => "MADIS Station Table"
	);
	$fselect = make_select("format", $format, $ar);
	$nselect = selectNetwork($network, Array("_ALL_"=>"All Networks"));
	$t->content = <<<EOF
<h3>Network Location Tables</h3>

<div class="well pull-right">
<a href="new-rss.php"><img src="/images/rss.gif" style="border: 0px;" alt="RSS" /></a> Feed of newly 
added stations.

<br /><strong>Special Table Requests</strong>
<ul>
 <li><a href="networks.php?special=allasos&format=gempak&nohtml">Global METAR in GEMPAK Format</a></li>
</ul>
</div>


<p>With this form, you can generate a station table for any
of the networks listed below.  If there is a particular format for a station
table that you need, please <a href="/info/contacts.php">let us know</a>.</p>

<form method="GET" action="networks.php" name="networkSelect">
<table>
<tr>
  <th>Select Observing Network:</th>
  <td>{$nselect}</td>
</tr>
<tr>
  <th>Select Format:</th>
<td>
{$fselect}
</td></tr>

<tr>
 <td colspan="2"><input type="checkbox" name="nohtml">Just Table, no HTML</td></tr>

<tr><td colspan="2">
<input type="submit" value="Create Table">
</form>
</td></tr>
</table>

{$table}
<p><h3>Notes</h3>
<ol>
<li>Latitude and Longitude values are in decimal degrees.</li>
<li>Elevation is expressed in meters above sea level.</li>
</ol>
EOF;
	$t->render($page);
} else{
	header("Content-type: text/plain");
	echo $table;
}
