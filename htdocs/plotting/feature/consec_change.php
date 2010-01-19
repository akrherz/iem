<?php
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_bar.php");
//include ("../../../include/jpgraph/jpgraph_date.php");
include ("../../../include/database.inc.php");
header("Content-type: text/plain");
$db = iemdb("coop");

$up = Array();
$down = Array();
for ($i=0;$i<12;$i++){ $up[$i] = 0; $down[$i] = 0; }

$sql = sprintf("SELECT high, month
       from alldata WHERE stationid = 'ia0200' ORDER by day ASC");
$rs = pg_query($db, $sql);
$last = null;
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  if ($last == null){ $last = $row["high"]; }
  $high = $row["high"];
  if ($high >= ($last + 20)){ $up[ intval($row["month"]) -1 ] += 1.0/117.0; }
  if ($high <= ($last - 20)){ $down[ intval($row["month"]) -1 ] += 1.0/117.0; }
  $last = $high;
}

// Create the graph. These two calls are always required
$graph = new Graph(320,280,"auto");    
$graph->SetScale("textlin");
$graph->legend->Pos(0.05,0.10);
$graph->legend->SetLayout(LEGEND_HOR);


//$graph->SetShadow();
$graph->img->SetMargin(50,10,10,55);

// Create the bar plots
$b1plot = new BarPlot($up);
$b1plot->SetFillColor("red");
$b1plot->SetLegend('Warmer');
//$graph->Add($b1plot);

// Create the bar plots
$b2plot = new BarPlot($down);
$b2plot->SetFillColor("blue");
$b2plot->SetLegend('Cooler');
//$graph->Add($b2plot);

$graph->legend->SetPos(0.01,0.17, 'right', 'top');

$gp = new GroupBarPlot(Array($b1plot,$b2plot));
$graph->Add($gp);

$graph->title->Set("Day to Day 20+ Degree High Temp Change");
$graph->title->SetFont(FF_ARIAL,FS_BOLD,12);

$graph->subtitle->Set("Ames [1893-2008]");
$graph->subtitle->SetFont(FF_ARIAL,FS_NORMAL,10);

$graph->yaxis->title->Set("Average Number of Days");
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,10);
$graph->yaxis->SetTitleMargin(36);

$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d", true);
$graph->xaxis->SetTickLabels(Array("JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC") );
//$graph->xaxis->SetTextTickInterval(5);
//$graph->xaxis->HideTicks();
$graph->SetColor("lightyellow");
$graph->SetMarginColor("khaki");

// Display the graph
$graph->Stroke();
?>
