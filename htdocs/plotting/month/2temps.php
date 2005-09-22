<?php

$query1 = "select * , round( montotalclimo(valid, station), 2) as tot0, round( montotal(valid, 'AMW') / 25.4 , 2) as tot, round( daytotal(valid, 'AMW')/25.4, 2) as tot2 from precip_accum  WHERE station = 'am0200' and date_part('month', valid) = 6 ;";

$ydata = array( 0.08, 0.01, 0.00, 0.00, 0.34, 0.00, 0.00, 0.00, 0.00, 0.12, 0.00, 1.15, 0.00, 0.50, 0.02, 0.17, 0.00, 0.00, 0.00, 0.07, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00 );

$ydata2 = array( 0.14, 0.28, 0.42, 0.56, 0.70, 0.85, 1.00, 1.16, 1.35, 1.53, 1.73, 1.93, 2.14, 2.33, 2.52, 2.71
 ,2.89, 3.07, 3.24, 3.39, 3.54, 3.69, 3.85, 4.02, 4.19, 4.36, 4.52, 4.69, 4.85, 5.02);

$ydata3 = array(0.08, 0.09, 0.09, 0.09, 0.43, 0.43, 0.43, 0.43, 0.43, 0.55, 0.55, 1.70, 1.70, 2.20, 2.22, 2.39, 2.39,
2.39, 2.39, 2.46, 2.46, 2.46, 2.46, 2.46, 2.46, 2.46, 2.46, 2.46, 2.46, 2.46);

$xlabel= array('2000-06-01', '2000-06-02', '2000-06-03', '2000-06-04', '2000-06-05', '2000-06-06', '2000-06-07','2000-06-08', '2000-06-09'
, '2000-06-10', '2000-06-11', '2000-06-12', '2000-06-13', '2000-06-14', '2000-06-15', '2000-06-16', '2000-06-17', '2000-06-18', '2000-06-19'
, '2000-06-20', '2000-06-21', '2000-06-22', '2000-06-23', '2000-06-24', '2000-06-25', '2000-06-26', '2000-06-27', '2000-06-28', '2000-06-29', '2000-06-30');

include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");
include ("../dev/jpgraph_bar.php");

// Create the graph. These two calls are always required
$graph = new Graph(350,400,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(30,10,60,90);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("Ames Precipitation for June 2001");
$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.05, 0.1, "right", "top");

// Create the linear plot
$lineplot=new LinePlot($ydata2);
$lineplot->SetLegend("Normal");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($ydata3);
$lineplot2->SetLegend("Acual Accum");
$lineplot2->SetColor("blue");

// Create Bar plot
$l2plot = new BarPlot($ydata);
$l2plot->SetFillColor("blue");
$l2plot->SetLegend("Acual");

// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);
$graph->Add($l2plot);

// Display the graph
$graph->Stroke();
?>

