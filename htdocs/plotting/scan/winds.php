<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/network.php";
require_once "../../../include/forms.php";
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_scatter.php";
$nt = new NetworkTable("SCAN");

$connection = iemdb("scan");

$station = isset($_GET["station"]) ? xssafe($_GET["station"]) : "S2031";
$year = get_int404("year", date("Y", time() - 3 * 86400));
$month = get_int404("month", date("m", time() - 3 * 86400));
$day = get_int404("day", date("d", time() - 3 * 86400));

$date = "$year-$month-$day";

$stname = iem_pg_prepare($connection, "SELECT sknt, drct, 
        to_char(valid, 'mmdd/HH24') as tvalid 
        from alldata WHERE 
        station = $1 and date(valid) >= $2  
        ORDER by tvalid ASC LIMIT 96");

$result = pg_execute($connection, $stname, Array($station, $date));

$ydata1 = array();
$ydata2 = array();

$xlabel= array();

for( $i=0; $row = pg_fetch_assoc($result); $i++) 
{ 
  $ydata1[$i]  = $row["drct"];
  $ydata2[$i]  = $row["sknt"];
  $xlabel[$i] = $row["tvalid"];
}

// Create the graph. These two calls are always required
$graph = new Graph(660,450,"example1");
$graph->SetScale("textlin", 0, 360);
$graph->SetY2Scale("lin");
$graph->img->SetMargin(40,50,55,90);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("Wind Direction/Speed for ".$nt->table[$station]["name"]." SCAN Site");

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
