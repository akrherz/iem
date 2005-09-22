<?php

include ("../../dev15/jpgraph.php");
include ("../../dev15/jpgraph_line.php");


$fcontents = file('junjul.dat');

$ydata = Array();

while (list ($line_num, $line) = each ($fcontents)) {
  $parts = split("\|", $line);
  $ydata[] = $parts[1];
}

$xlabel = Array(0 => "1900", 
  10 => "1910",
  20 => "1920",
  30 => "1930",
  40 => "1940",
  50 => "1950",
  60 => "1960",
  70 => "1970",
  80 => "1980",
  90 => "1990",
 100 => "2000",
);


$graph = new Graph(640,480,"example1");
$graph->SetScale("textlin", 68, 80);

$graph->img->SetMargin(40,40,40,40);
$graph->SetShadow();

$graph->title->Set("IA,IL,IN,OH,MO Jun/Jul Avg Temperature");
$graph->title->SetFont(FF_FONT1,FS_BOLD);

$graph->yaxis->SetTitle("Temperature [F]");

$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetTextTickInterval(10);

$p1 = new LinePlot($ydata);
$p1->SetFillColor("orange");
$p1->mark->SetType(MARK_FILLEDCIRCLE);
$p1->mark->SetFillColor("red");
$p1->mark->SetWidth(4);


$graph->Add($p1);

$graph->Stroke();
?>
