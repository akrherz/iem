<?php
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_bar.php");
//include ("../../../include/jpgraph/jpgraph_date.php");
include ("../../../include/database.inc.php");
header("Content-type: text/plain");
$db = iemdb("coop");

$data = Array();
$x = Array();
$sql = sprintf("SELECT year, sum(case when high > 92 THEN 1 ELSE 0 END) as s
 from alldata WHERE stationid = 'ia0200' GROUP by year ORDER by year ASC");
$rs = pg_query($db, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $x[] = $row["year"];
  $data[] = $row["s"];
  //echo sprintf("%s,%s\n", $row["year"], $row["s"]);
}


// Create the graph. These two calls are always required
$graph = new Graph(630,480,"auto");    
$graph->SetScale("textlin");
$graph->legend->Pos(0.05,0.10);
$graph->legend->SetLayout(LEGEND_HOR);


$graph->SetShadow();
$graph->img->SetMargin(40,10,10,55);

// Create the bar plots
$b1plot = new BarPlot($data);
//$b1plot->SetOutlineColor("red");
//$b1plot->SetLegend('Severe Thunderstorm');
$b1plot->SetAlign("left"); 

// ...and add it to the graPH
$graph->Add($b1plot);

$graph->title->Set("93+ Degree Days in Ames");
//$graph->xaxis->title->Set("Day of May 2008");
$graph->yaxis->title->Set("Number of Days");

$graph->title->SetFont(FF_FONT1,FS_BOLD);
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d", true);
$graph->xaxis->SetTickLabels($x);
$graph->xaxis->SetTextTickInterval(5);
//$graph->xaxis->HideTicks();
$graph->SetColor("lightyellow");
$graph->SetMarginColor("khaki");

// Display the graph
$graph->Stroke();
?>
