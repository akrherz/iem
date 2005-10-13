<?php
$connection = pg_connect("10.10.10.20","5432","scan");

 $station = isset($_GET["station"]) ? $_GET["station"] : "2031";
 $year = isset($_GET["year"]) ? $_GET["year"] : date("Y", time() - 3*86400);
 $month = isset($_GET["month"]) ? $_GET["month"] : date("m", time() - 3*86400);
 $day = isset($_GET["day"]) ? $_GET["day"] : date("d", time() - 3*86400);

$table = "t${year}_hourly";

$queryData = "sknt, drct";

$date = "$year-$month-$day";

$query2 = "SELECT ". $queryData .", to_char(valid, 'mmdd/HH24') as tvalid from ". $table ." WHERE 
	station = '". $station ."' and date(valid) >= ('". $date ."')  ORDER by tvalid ASC LIMIT 96";

$result = pg_exec($connection, $query2);

$ydata1 = array();
$ydata2 = array();

$xlabel= array();

for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata1[$i]  = $row["drct"];
  $ydata2[$i]  = $row["sknt"];
  $xlabel[$i] = $row["tvalid"];
}

pg_close($connection);

include ("../../include/scanLoc.php");
include ("../jpgraph/jpgraph.php");
include ("../jpgraph/jpgraph_line.php");
include ("../jpgraph/jpgraph_scatter.php");

// Create the graph. These two calls are always required
$graph = new Graph(660,450,"example1");
$graph->SetScale("textlin", 0, 360);
$graph->SetY2Scale("lin");
$graph->img->SetMargin(40,50,55,90);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("Wind Direction/Speed for ".$sites[$station]["city"]." SCAN Site");

$graph->yaxis->scale->ticks->Set(90,15);
//$graph->yaxis->scale->ticks->SetPrecision(0);

$graph->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->yaxis->SetTitle("Wind Direction [Deg]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Local Valid Time");
$graph->y2axis->SetTitle("Wind Speed [knots]");
$graph->y2axis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->y2axis->SetTitleMargin(35);
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
if ($i > 72){
  $graph->xaxis->SetTextTickInterval(6);
}
//$graph->y2axis->SetColor("blue");
$graph->yaxis->SetColor("blue");

// Create the linear plot
$sp1=new ScatterPlot($ydata1);
$sp1->mark->SetType(MARK_FILLEDCIRCLE);
$sp1->mark->SetFillColor("blue");
$sp1->mark->SetWidth(3);

$sp1->SetLegend("Wind Dir");

// Create the linear plot
$lineplot1=new LinePlot($ydata2);
$lineplot1->SetColor("black");
$lineplot1->SetLegend("Wind Speed");

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.10, 0.06, "right", "top");


// Add the plot to the graph
$graph->Add($sp1);
$graph->AddY2($lineplot1);

// Display the graph
$graph->Stroke();
