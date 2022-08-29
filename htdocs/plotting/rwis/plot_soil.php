<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/forms.php";

/** We need these vars to make this work */
$syear = get_int404("syear", date("Y"));
$smonth = get_int404("smonth", date("m"));
$sday = get_int404("sday", date("d"));
$days = get_int404("days", 2);
$station = isset($_GET['station']) ? xssafe($_GET["station"]) : "";
$mode = isset($_GET["mode"]) ? xssafe($_GET["mode"]): "rt";

$sts = time() - (3.*86400.);
$ets = time();

$data = Array();
$times = Array();
for ($i=0;$i<15;$i++){
	$data["s${i}temp"] = Array();
}

/** Lets assemble a time period if this plot is historical */
if ($mode != 'rt') {
  $sts = mktime(0,0,0, $smonth, $sday, $syear);
  $ets = $sts + ($days * 86400.0);

	$dbconn = iemdb('rwis');
	$rs = pg_prepare($dbconn, "SELECT", "SELECT * from alldata_soil
  WHERE station = $1 and valid > $2 and valid < $3 ORDER by valid ASC");
	$rs = pg_execute($dbconn, "SELECT", Array($station,
       date("Y-m-d H:i", $sts), date("Y-m-d H:i", $ets)) );

	for( $i=0; $row = pg_fetch_array($rs); $i++) 
	{ 
    	$times[] = strtotime(substr($row["valid"],0,16));
		for($j=0;$j<15;$j++){
			$data["s${j}temp"][] = $row["s${j}temp"];
		}
	}
	pg_close($dbconn);
} else {
	$dbconn = iemdb('iem');
	$rs = pg_prepare($dbconn, "SELECT", "SELECT d.* from 
		rwis_soil_data_log d, rwis_locations l
		WHERE l.id = d.location_id and l.nwsli = $1
		ORDER by valid ASC");
	$rs = pg_execute($dbconn, "SELECT", Array($station));
	$lts = 0;
	for( $i=0; $row = pg_fetch_array($rs); $i++) 
	{
		$ts = strtotime(substr($row["valid"],0,16));
		if ($lts != $ts){ $times[] = $ts; $lts = $ts;}
		$data["s". $row["sensor_id"]."temp"][] = $row["temp"];
	}
	pg_close($dbconn);
}

require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_bar.php";
require_once "../../../include/jpgraph/jpgraph_date.php";
require_once "../../../include/jpgraph/jpgraph_led.php";

if (pg_num_rows($rs) == 0){
	$led = new DigitalLED74();
    $led->StrokeNumber('NO SOIL DATA AVAILABLE',LEDC_GREEN);
    die();
}

include ("../../../include/network.php");
$nt = new NetworkTable("IA_RWIS");
$cities = $nt->table;

// Create the graph. These two calls are always required
$graph = new Graph(650,550,"example1");
$graph->SetScale("datlin");
$graph->SetMarginColor("white");
$graph->SetColor("lightyellow");
//$graph->img->SetMargin(40,55,105,105);
//$graph->xaxis->SetFont(FS_FONT1,FS_BOLD);

$graph->title->Set($cities[$station]['name'] ." RWIS Soil Probe Data");
$graph->subtitle->Set("Values at 15 different depths [inch] shown");

$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);

//$graph->xaxis->SetTitle("Time Period:");
$graph->xaxis->SetTitleMargin(67);
$graph->xaxis->title->SetFont(FF_VERA,FS_BOLD,12);
$graph->xaxis->title->SetColor("brown");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M-j h A", true);

$graph->legend->Pos(0.01, 0.01);
$graph->legend->SetLayout(LEGEND_VERT);

$labels = Array(1,3,6,9,12,18,24,30,36,42,48,54,60,66,72);
$colors = Array("green", "black", "blue", "red",
 "purple", "tan", "pink", "lavender", "teal", "maroon","brown","yellow",
 "skyblue", "skyblue", "white");

for($j=0;$j<15;$j++){
	// Create the linear plot
    $lineplot=new LinePlot($data["s${j}temp"], $times);
    $lineplot->SetLegend($labels[$j]);
	$lineplot->SetColor($colors[$j]);
	$lineplot->SetWeight(3);
	$graph->add($lineplot);
}

$graph->Stroke();
