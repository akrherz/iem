<?php
/** POC for line plots of forecasts Daryl (3 Sep 2003) */

$c = pg_connect("10.10.10.10","5432","ndfd");
$q = "SELECT * from point_forecasts";
$rs = pg_exec($c, $q);
pg_close($c);

$ydata = Array();

for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) {
  $ydata[] = $row["value"];
} // End for

include ("../jpgraph/jpgraph.php");
include ("../jpgraph/jpgraph_line.php");


$graph = new Graph(600,400);
$graph->SetScale("textlin");

$lineplot=new LinePlot($ydata);
$lineplot->SetColor("red");

$graph->Add($lineplot);

$graph->Stroke();
?>
