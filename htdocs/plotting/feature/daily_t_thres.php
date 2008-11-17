<?php
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_bar.php");
include ("../../../include/jpgraph/jpgraph_date.php");
include ("../../../include/database.inc.php");

$db = iemdb("coop");

$sts = mktime(0,0,0,1,1,2000);
$data = Array();
$ts = Array();
$sql = sprintf("SELECT sday, count(*) as c
 from alldata WHERE stationid = 'ia0200' and high >= 90 and month > 4 and month < 10 GROUP by sday ORDER by sday ASC");
$rs = pg_query($db, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $ts[] = mktime(0,0,0,intval(substr($row["sday"],0,2)), intval(substr($row["sday"],2,2)), 2000);
  $data[] = intval( $row["c"] /115 * 100);
}


// Create the graph. These two calls are always required
$graph = new Graph(310,300,"auto");    
$graph->SetScale("datlin");
$graph->legend->Pos(0.05,0.10);
$graph->legend->SetLayout(LEGEND_HOR);

$graph->SetShadow();
$graph->img->SetMargin(40,10,10,55);

// Create the bar plots
$b1plot = new BarPlot($data, $ts);
$b1plot->SetFillColor("yellow");
//$b1plot->SetLegend('Severe Thunderstorm');

// ...and add it to the graPH
$graph->Add($b1plot);

$graph->title->Set("90 Degree Days in Ames");
//$graph->xaxis->title->Set("Day of May 2008");
$graph->yaxis->title->Set("Percent of Years since 1893");

$graph->title->SetFont(FF_FONT1,FS_BOLD);
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);

// Display the graph
$graph->Stroke();
?>
