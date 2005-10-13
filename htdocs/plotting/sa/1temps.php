<?php

$tableName = "grinell_daily";
$connection = pg_connect("localhost","5432", "sa");


$query2 = "SELECT p24m, soilm_avg, to_char(valid, 'yymmdd/HH24MI') as valid from ". $tableName ." ORDER by valid ASC";

$result = pg_exec($connection, $query2);

$ydata = array();
$ydata2 = array();
$xlabel= array();

for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["p24m"];
  $ydata2[$i]  = $row["soilm_avg"];
  $xlabel[$i] = $row["valid"];
}

pg_close($connection);


include ("../dev15/jpgraph.php");
include ("../dev15/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,350,"example1");
$graph->SetScale("textlin");
$graph->SetY2Scale("lin");
$graph->img->SetMargin(40,40,55,90);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("24 h Meteogram for ". $station);

$interval = intval( sizeof($xlabel) / 24 );
if ($interval > 1 ){
  $graph->xaxis->SetTextLabelInterval($interval);
}


$graph->title->SetFont(FF_FONT1,FS_BOLD,16);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Time [GMT]");
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

$graph->legend->Pos(0.01, 0.07);
$graph->legend->SetLayout(LEGEND_HOR);

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetLegend("prec (mm)");
$lineplot->SetColor("blue");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetLegend("SM (%)");
$lineplot2->SetColor("red");


// Add the plot to the graph
$graph->Add($lineplot);
$graph->AddY2($lineplot2);

// Display the graph
$graph->Stroke();
?>

