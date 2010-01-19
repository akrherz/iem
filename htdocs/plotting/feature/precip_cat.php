<?php
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_bar.php");
include ("../../../include/database.inc.php");

$fc = file('ames_precip.txt');
$d005 = Array();
$d025 = Array();
$d050 = Array();
$d100 = Array();
$d101 = Array();

while (list ($line_num, $line) = each ($fc)) {
  $tokens = split(" ", $line);
  $d005[] = $tokens[1] * $tokens[6];
  $d025[] = $tokens[2] * $tokens[6];
  $d050[] = $tokens[3] * $tokens[6];
  $d100[] = $tokens[4] * $tokens[6];
  $d101[] = $tokens[5] * $tokens[6];
}


// Create the graph. These two calls are always required
$graph = new Graph(320,300,"auto");    
$graph->SetScale("textlin",0,5.5);
$graph->legend->Pos(0.05,0.07);
$graph->legend->SetLayout(LEGEND_VERT);

$graph->SetShadow();
$graph->img->SetMargin(40,10,40,40);

$b005 = new BarPlot($d005);
$b005->SetFillColor("blue");
$b005->SetLegend('0-0.05');

$b025 = new BarPlot($d025);
$b025->SetFillColor("green");
$b025->SetLegend('0.5-0.25');

$b050 = new BarPlot($d050);
$b050->SetFillColor("yellow");
$b050->SetLegend('0.25-0.5');

$b100 = new BarPlot($d100);
$b100->SetFillColor("orange");
$b100->SetLegend('0.5-1');

$b101 = new BarPlot($d101);
$b101->SetFillColor("red");
$b101->SetLegend('1+');

// Create the grouped bar plot
$gbplot = new AccBarPlot(array($b005,$b025,$b050,$b100,$b101));

// ...and add it to the graPH
$graph->Add($gbplot);

$graph->title->Set("Ames Monthly Precip by Daily Amount");
$graph->subtitle->Set("1900-2009");
//$graph->xaxis->title->Set("Day of May 2008");
$graph->yaxis->title->Set("Precipitation [inch]");

$graph->title->SetFont(FF_FONT1,FS_BOLD);
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels( Array("JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC") );

// Display the graph
$graph->Stroke();
?>
