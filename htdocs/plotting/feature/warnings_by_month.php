<?php
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_bar.php");
include ("../../../include/database.inc.php");

$db = iemdb("postgis");

$svr08 = Array();
$tor08 = Array();
$svr09 = Array();
$tor09 = Array();
$sql = sprintf("SELECT extract(month from issue) as m, phenomena, count(*) as c 
 from warnings_2008 WHERE gtype = 'P' and significance = 'W' and issue > '2008-01-01' and issue < '2008-12-03'
 GROUP by m, phenomena ORDER by m ASC");
$rs = pg_query($db, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $p = $row["phenomena"];
  if ($p == "TO") $tor08[] = $row["c"];
  if ($p == "SV") $svr08[] = $row["c"];
}

$sql = sprintf("SELECT extract(month from issue) as m, phenomena, count(*) as c 
 from warnings_2009 WHERE gtype = 'P' and significance = 'W' and issue > '2009-01-01' and issue < '2009-12-05'
 GROUP by m, phenomena ORDER by m ASC");
$rs = pg_query($db, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $p = $row["phenomena"];
  if ($p == "TO") $tor09[] = $row["c"];
  if ($p == "SV") $svr09[] = $row["c"];
}

// Create the graph. These two calls are always required
$graph = new Graph(1024,450,"auto");    
$graph->SetScale("textlin");
$graph->legend->Pos(0.0,0.07);
$graph->legend->SetLayout(LEGEND_HOR);

$graph->SetShadow();
$graph->img->SetMargin(50,10,49,40);

$graph->xaxis->SetTickLabels( Array("JAN", "FEB", "MAR", "APR", "MAY","JUN","JUL","AUG","SEP","OCT", "NOV", "DEC") );

// Create the bar plots
$b1plot = new BarPlot($svr08);
$b1plot->SetFillColor("yellow");
$b1plot->SetLegend('08 SVR');

$b2plot = new BarPlot($tor08);
$b2plot->SetFillColor("red");
$b2plot->SetLegend('08 TOR');

// Create the bar plots
$b3plot = new BarPlot($svr09);
$b3plot->SetFillColor("lightyellow");
$b3plot->SetLegend('09 SVR');

$b4plot = new BarPlot($tor09);
$b4plot->SetFillColor("lightred");
$b4plot->SetLegend('09 TOR');

$gbarplot = new GroupBarPlot(array($b1plot,$b2plot,$b3plot,$b4plot));
$gbarplot->SetWidth(0.8);
$graph->Add($gbarplot);


$graph->title->Set("NWS Issued Warnings by Month");
$graph->xaxis->title->Set("Thru 1 November");
$graph->yaxis->title->Set("Total Warnings");
$graph->yaxis->SetTitleMargin(38);

$graph->title->SetFont(FF_FONT1,FS_BOLD);
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD);

// Display the graph
$graph->Stroke();
?>
