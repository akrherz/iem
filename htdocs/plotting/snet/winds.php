<?php
$connection = pg_connect("10.10.10.40","5432","snet");


$query2 = "SELECT sknt, drct, to_char(valid, 'mmdd/HH24MI') as valid from t2004 WHERE station = '". $station ."' 
	and valid + '1 day' > CURRENT_TIMESTAMP ORDER by valid ASC";

$result = pg_exec($connection, $query2);

$ydata = array();
$ydata2 = array();
$xlabel= array();

for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["sknt"];
  $ydata2[$i]  = $row["drct"];
  $xlabel[$i] = $row["valid"];
}

//  $xlabel = array_reverse( $xlabel );
//  $ydata2 = array_reverse( $ydata2 );
//  $ydata  = array_reverse( $ydata );
 

pg_close($connection);


include ("../dev15/jpgraph.php");
include ("../dev15/jpgraph_line.php");
include ("../dev15/jpgraph_scatter.php");
include ("../../include/snetLoc.php");


// Create the graph. These two calls are always required
$graph = new Graph(400,350,"example1");
$graph->SetScale("textlin", 0, 50);
$graph->yaxis->scale->ticks->Set(5,1);
$graph->yaxis->scale->ticks->SetPrecision(0);
$graph->SetY2Scale("lin", 0, 360);
$graph->y2axis->scale->ticks->Set(30,15);
$graph->y2axis->scale->ticks->SetPrecision(0);
$graph->img->SetMargin(40,40,55,90);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("24 h winds for ". $Scities[$station]["city"]);

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);
$graph->yaxis->SetTitle("Wind Speed [knots]");
$graph->y2axis->SetTitle("Direction [N 0]");
$graph->yaxis->SetColor("red");
$graph->y2axis->SetColor("blue");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Local Valid Time");
$graph->xaxis->SetTextLabelInterval(3);
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);

$graph->legend->Pos(0.01, 0.09);
$graph->legend->SetLayout(LEGEND_HOR);

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetLegend("Wind Speed");
$lineplot->SetColor("red");

// Create the linear plot
$sp1=new ScatterPlot($ydata2);
$sp1->mark->SetType(MARK_FILLEDCIRCLE);
$sp1->mark->SetFillColor("blue");
$sp1->mark->SetWidth(3);
$sp1->SetLegend("Wind Direction");

// Add the plot to the graph
$graph->Add($lineplot);
$graph->AddY2($sp1);

// Display the graph
$graph->Stroke();
?>

