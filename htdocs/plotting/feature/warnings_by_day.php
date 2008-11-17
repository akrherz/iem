<?php
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_bar.php");
include ("../../../include/database.inc.php");

$db = iemdb("postgis");

$svr = Array();
$tor = Array();
$sts = mktime(0,0,0,10,1,2008);
$ets = mktime(0,0,0,10,18,2008);
$days = intval( ($ets-$sts)/86400);
for($i=0;$i<$days;$i++)
{
  $tor[] = 0;
  $svr[] = 0;
}
$sql = sprintf("SELECT date(issue) as d, phenomena, count(*) as c 
 from warnings_%s WHERE gtype = 'P' and significance = 'W' 
 and issue > '%s' and issue < '%s' GROUP by d, phenomena", date("Y", $sts), 
 date("Y-m-d H:i", $sts), date("Y-m-d H:i", $ets) );
$rs = pg_query($db, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $p = $row["phenomena"];
  $ts = strtotime( $row["d"] );
  $offset = intval( ($ts-$sts) / 86400);
  if ($p == "TO") $tor[$offset] = $row["c"];
  if ($p == "SV") $svr[$offset] = $row["c"];
}


// Create the graph. These two calls are always required
$graph = new Graph(310,300,"auto");    
$graph->SetScale("textlin");
$graph->legend->Pos(0.05,0.10);
$graph->legend->SetLayout(LEGEND_HOR);

$graph->SetShadow();
$graph->img->SetMargin(40,10,40,40);

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

$graph->title->Set("NWS Issued Warnings");
$graph->xaxis->title->Set("Day of May 2008");
$graph->yaxis->title->Set("Total Warnings");

$graph->title->SetFont(FF_FONT1,FS_BOLD);
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD);

// Display the graph
$graph->Stroke();
?>
