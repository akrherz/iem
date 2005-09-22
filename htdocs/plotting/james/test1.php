<?php
// Sample plot of some data from David James

$fc = file('qtesthourly325.dat');

$xdata = Array();

while (list ($line_num, $line) = each ($fc)) {
  $parts = split ("\t", $line);
  $xdata[] = (float)$parts[2];
}


include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");

$graph = new Graph(600,300,"example1");
$graph->SetScale("textlin");

$lineplot=new LinePlot($xdata);
$lineplot->SetColor("black");

$graph->Add($lineplot);
$graph->Stroke();
?>
