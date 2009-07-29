<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$conn = iemdb("coop");
$station1 = isset($_GET["station1"]) ? strtolower($_GET["station1"]) : 'ia0200';
$station2 = isset($_GET["station2"]) ? strtolower($_GET["station2"]) : '';

$slimiter = "and stationid = '$station1'";
if ($station1 == "iowa"){ $slimiter = ""; }

$xdata = Array();
$ydata = Array();
for($thres=-40;$thres<11;$thres++)
{
  $sql = "SELECT y1, count(*) from 
          ((SELECT year as y1, low from alldata 
           WHERE month IN (12) $slimiter) UNION 
          (SELECT year - 1 as y1, low from alldata 
           WHERE month IN (1,2) $slimiter)) as foo 
         WHERE low < ${thres} GROUP by y1";
  $rs = pg_exec($conn, $sql);
  $xdata[] = $thres;
  $ydata[] = pg_numrows($rs);
}
$yrs = pg_numrows($rs);
$pct = Array();
while( list($k,$v) = each($ydata))
{
  $pct[] = $v / $yrs * 100.0;
}

if ($station2 != "")
{
  $slimiter = "and stationid = '$station2'";
  $ydata = Array();
  for($thres=-40;$thres<11;$thres++)
  {
    $sql = "SELECT y1, count(*) from 
          ((SELECT year as y1, low from alldata 
           WHERE month IN (12) $slimiter) UNION 
          (SELECT year - 1 as y1, low from alldata 
           WHERE month IN (1,2) $slimiter)) as foo 
         WHERE low < ${thres} GROUP by y1";
    $rs = pg_exec($conn, $sql);
    $ydata[] = pg_numrows($rs);
  }
  $yrs2 = pg_numrows($rs);
  $pct2 = Array();
  while( list($k,$v) = each($ydata))
  {
    $pct2[] = $v / $yrs2 * 100.0;
  }

}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_plotline.php");
include("$rootpath/include/network.php");     
$nt = new NetworkTable("IACLIMATE");
$cities = $nt->table;


$graph = new Graph(500,400);
$graph->SetScale("lin");
$graph->img->SetMargin(40,10,50,0);

$graph->title->Set("Winter [DJF] Low Temp Thresholds");

$graph->yaxis->SetTitle("Percentage of years");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);

$graph->xaxis->SetTitle("Low Temperature [F] Threshold");
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);

$graph->legend->Pos(0.5, 0.07);

for ($i=-30; $i < 10; $i=$i+10){
  $graph->AddLine(new PlotLine(VERTICAL, $i ,"tan",1));
}

$lineplot2=new LinePlot($pct, $xdata);
$lineplot2->SetColor("blue");
$lineplot2->SetWeight(3);
$lineplot2->SetLegend("$yrs years at ". $cities[strtoupper($station1)]["name"] );
$graph->Add($lineplot2);

if ($station2 != "")
{
  $lineplot3=new LinePlot($pct2, $xdata);
  $lineplot3->SetColor("red");
  $lineplot3->SetWeight(3);
  $lineplot3->SetLegend("$yrs2 years at ". $cities[strtoupper($station2)]["name"] );
  $graph->Add($lineplot3);
}


$graph->Stroke();


?>
