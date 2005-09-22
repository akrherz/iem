<?php
$connection = pg_connect("10.10.10.20","5432","scan");
 $station = isset($_GET["station"]) ? $_GET["station"] : "2031";
 $year = isset($_GET["year"]) ? $_GET["year"] : date("Y", time() - 3*86400);
 $month = isset($_GET["month"]) ? $_GET["month"] : date("m", time() - 3*86400);
 $day = isset($_GET["day"]) ? $_GET["day"] : date("d", time() - 3*86400);

$table = "t${year}_hourly";

$date = "$year-$month-$day";


$var = "phour";
$accum = 1;


$query2 = "SELECT ".$var.", to_char(valid, 'mmdd/HH24') as tvalid from ". $table ." WHERE 
	station = '". $station ."' and date(valid) >= ('". $date ."')  ORDER by tvalid ASC LIMIT 96";

$result = pg_exec($connection, $query2);

$ydata1 = array();

$xlabel= array();

$thisP = 0;

for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata1[$i]  = $row["phour"];
  $xlabel[$i] = $row["tvalid"];
}

pg_close($connection);

include ("../../include/scanLoc.php");
include ("../jpgraph/jpgraph.php");
include ("../jpgraph/jpgraph_bar.php");

// Create the graph. These two calls are always required
$graph = new Graph(660,450,"example1");
$graph->SetScale("textlin", 0, 2);
$graph->img->SetMargin(45,10,55,90);
//$graph->xaxis->SetFont(FS_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("Hourly Precipitation for ".$sites[$station]["city"]." SCAN Site");

$graph->yaxis->scale->ticks->Set(.25,.1);
//$graph->yaxis->scale->ticks->SetPrecision(2);

$graph->title->SetFont(FF_VERDANA,FS_BOLD,12);
$graph->yaxis->SetTitle("Precipitation [in]");
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->xaxis->SetTitle("Local Valid Time");
$graph->xaxis->SetTitleMargin(55);
$graph->yaxis->SetTitleMargin(35);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
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
