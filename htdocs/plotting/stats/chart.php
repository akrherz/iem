<?php

$hits = array(2000, 8000, 24000);
$obs = array(1, 150, 500);
$xlabel= array("2001", "2002", "2003");


include ("../jpgraph/jpgraph.php");
include ("../jpgraph/jpgraph_bar.php");


// Create the graph. These two calls are always required
$graph = new Graph(600,400,"example3");
$graph->SetScale("textlin",0,50);
$graph->img->SetMargin(40,30,40,40);
$graph->SetScale("textint");
$graph->SetFrame(true,'blue',1); 
$graph->SetColor('lightblue');
$graph->SetMarginColor('lightblue');

$graph->yaxis->SetColor('lightblue','darkblue');
$graph->ygrid->SetColor('white');
$graph->yaxis->scale->SetGrace(20);


//$graph->xaxis->SetFont(FS_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);

//$graph->yaxis->scale->ticks->Set(5,1);
//$graph->yaxis->scale->ticks->SetPrecision(0);

$graph->title->Set("The Iowa Environmental Mesonet Archive");
$graph->subtitle->Set("Archived observations in millions");
$graph->title->SetFont(FF_VERDANA,FS_BOLD,16);

$bplot = new BarPlot($obs);
$bplot->SetFillColor('darkblue');
$bplot->SetColor('darkblue');
$bplot->SetWidth(0.5);
$bplot->SetShadow('darkgray');

$bplot->value->Show();
// Must use TTF fonts if we want text at an arbitrary angle
$bplot->value->SetFont(FF_ARIAL,FS_NORMAL,8);
$bplot->value->SetFormat('%d');
// Black color for positive values and darkred for negative values
$bplot->value->SetColor("black","darkred");
$graph->Add($bplot);



// Display the graph
$graph->Stroke();
?>

