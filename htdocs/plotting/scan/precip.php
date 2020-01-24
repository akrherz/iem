<?php
include("../../../config/settings.inc.php");
include("../../../include/database.inc.php");
$connection = iemdb("scan");
include("../../../include/network.php");
$nt = new NetworkTable("SCAN");

 $station = isset($_GET["station"]) ? $_GET["station"] : "S2031";
 $year = isset($_GET["year"]) ? $_GET["year"] : date("Y", time() - 3*86400);
 $month = isset($_GET["month"]) ? $_GET["month"] : date("m", time() - 3*86400);
 $day = isset($_GET["day"]) ? $_GET["day"] : date("d", time() - 3*86400);

$date = "$year-$month-$day";
$var = "phour";
$accum = 1;

$rs = pg_prepare($connection, "SELECT", "SELECT sknt, drct, phour,
		to_char(valid, 'mmdd/HH24') as tvalid 
		from alldata WHERE 
		station = $1 and date(valid) >= $2  and phour >= 0
		ORDER by tvalid ASC LIMIT 96");

$result = pg_execute($connection, "SELECT", Array($station, $date));

$ydata1 = array();

$xlabel= array();

$thisP = 0;

for( $i=0; $row = pg_fetch_array($result); $i++) 
{ 
  $ydata1[$i]  = $row["phour"];
  $xlabel[$i] = $row["tvalid"];
}

pg_close($connection);

include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_bar.php");

// Create the graph. These two calls are always required
$graph = new Graph(660,450,"example1");
$graph->SetScale("textlin", 0, 2);
$graph->img->SetMargin(45,10,55,90);
//$graph->xaxis->SetFont(FS_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("Hourly Precipitation for ".$nt->table[$station]["name"]." SCAN Site");

$graph->yaxis->scale->ticks->Set(.25,.1);
//$graph->yaxis->scale->ticks->SetPrecision(2);

$graph->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->yaxis->SetTitle("Precipitation [in]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Local Valid Time");
$graph->xaxis->SetTitleMargin(55);
$graph->yaxis->SetTitleMargin(35);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
if ($i > 72){
  $graph->xaxis->SetTextTickInterval(6);
}
$graph->yaxis->SetColor("blue");

// Create the linear plot
$bar1=new BarPlot($ydata1);
$bar1->SetColor("black");
$bar1->SetLegend("1h Precip [inch]");

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.10, 0.06, "right", "top");


// Add the plot to the graph
$graph->Add($bar1);

// Display the graph
$graph->Stroke();

?>