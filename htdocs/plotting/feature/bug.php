<?php
$dwpf = Array ( 64.6, 63.2, 61.6, 61.4 );
$years = Array ( 2004, 2005, 2006, 2007 );

include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_bar.php");


// Create the graph. These two calls are always required
$graph = new Graph(620,600,"example1");
$graph->SetScale("textlin",55,71);
$graph->img->SetMargin(40,5,50,85);

$graph->xaxis->SetTickLabels($years);
$graph->yaxis->SetTitle("Temp [F]");
$graph->title->Set('Waterloo [KALO] Time Series');
$graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
$graph->SetColor('wheat');

$graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
$graph->ygrid->Show();
$graph->xgrid->Show();


// Create the linear plot
$bplot=new BarPlot($dwpf);
$bplot->SetLegend("2009");
$bplot->SetColor("blue");
$graph->Add($bplot);

// Display the graph
$graph->Stroke();
?>
