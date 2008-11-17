<?php
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_bar.php");
include ("../../../include/database.inc.php");

$db = iemdb("postgis");

$svr = Array();
$tor = Array();
$sql = sprintf("SELECT extract(month from issue) as m, phenomena, count(*) as c 
 from warnings_2008 WHERE gtype = 'P' and significance = 'W' 
 GROUP by m, phenomena ORDER by m ASC");
$rs = pg_query($db, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $p = $row["phenomena"];
  if ($p == "TO") $tor[] = $row["c"];
  if ($p == "SV") $svr[] = $row["c"];
}


// Create the graph. These two calls are always required
$graph = new Graph(310,300,"auto");    
$graph->SetScale("textlin");
$graph->legend->Pos(0.05,0.08);
$graph->legend->SetLayout(LEGEND_HOR);

$graph->SetShadow();
$graph->img->SetMargin(50,10,40,40);

$graph->xaxis->SetTickLabels( Array("JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT") );

// Create the bar plots
$b1plot = new BarPlot($svr);
$b1plot->SetFillColor("yellow");
$b1plot->SetLegend('Severe Thunderstorm');

$b2plot = new BarPlot($tor);
$b2plot->SetFillColor("red");
$b2plot->SetLegend('Tornado');

// Create the grouped bar plot
$gbplot = new AccBarPlot(array($b1plot,$b2plot));

// ...and add it to the graPH
$graph->Add($gbplot);

$graph->title->Set("NWS Issued Warnings by Month");
$graph->xaxis->title->Set("Thru 20 Oct 2008");
$graph->yaxis->title->Set("Total Warnings");
$graph->yaxis->SetTitleMargin(38);

$graph->title->SetFont(FF_FONT1,FS_BOLD);
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD);

// Display the graph
$graph->Stroke();
?>
