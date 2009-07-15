<?php
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_bar.php");
include ("../../../include/database.inc.php");

$db = iemdb("postgis");

$svr = Array();
$tor = Array();
$sts = mktime(0,0,0,5,10,2009);
$ets = mktime(0,0,0,6,18,2009);
$days = intval( ($ets-$sts)/86400);
$xlabels = Array();
for($i=0;$i<$days;$i++)
{
  $tor[] = 0;
  $svr[] = 0;
  $xlabels[] = date("d M", $sts + ($i * 86400));
}
$year = date("Y", $sts);
$rs = pg_prepare($db, "SELECT", "SELECT date(issue) as d, phenomena, 
 count(*) as c from warnings_$year WHERE gtype = 'P' and significance = 'W' 
 and issue > $1 and issue < $2 GROUP by d, phenomena");
$rs = pg_execute($db, "SELECT", Array(date("Y-m-d H:i", $sts), date("Y-m-d H:i", $ets)));
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $p = $row["phenomena"];
  $ts = strtotime( $row["d"] );
  $offset = intval( ($ts-$sts) / 86400);
  if ($p == "TO") $tor[$offset] = $row["c"];
  if ($p == "SV") $svr[$offset] = $row["c"];
}


// Create the graph. These two calls are always required
$graph = new Graph(630,300,"auto");    
$graph->SetScale("textlin");
$graph->legend->Pos(0.05,0.07);
$graph->legend->SetLayout(LEGEND_HOR);

$graph->SetShadow();
$graph->img->SetMargin(40,10,30,60);

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

$graph->title->Set("NWS Issued Warnings 10 May - 17 Jun 2009");
//$graph->xaxis->title->Set("Day of May 2008");
$graph->yaxis->title->Set("Total Warnings");

$graph->title->SetFont(FF_FONT1,FS_BOLD);
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetTickLabels($xlabels);
$graph->xaxis->SetTextTickInterval(3);

// Display the graph
$graph->Stroke();
?>
