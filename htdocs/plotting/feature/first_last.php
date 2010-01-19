<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");

$first = Array();
$last = Array();

$coop = iemdb('coop');

$rs = pg_query($coop, "select first.year, f, l from (select year, sum(precip) as f from alldata WHERE month = 11 and stationid = 'ia0200' and sday < '1115' GROUP by year) as first, (select year, sum(precip) as l from alldata WHERE month = 11 and stationid = 'ia0200' and sday >= '1115' GROUP by year) as second WHERE first.year = second.year ORDER by f ASC");
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $first[] = $row["f"];
  $last[] = $row["l"];
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,300);
$graph->SetScale("lin");
$graph->img->SetMargin(45,10,35,45);

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
//$graph->xaxis->scale->SetAutoMax(5); 
//$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetTitleMargin(14);
$graph->yaxis->SetTitleMargin(30);


$graph->yaxis->SetTitle("Last 15 Days Rainfall [inch]");
$graph->xaxis->SetTitle("First 15 Days Rainfall [inch]");
$graph->title->Set('Ames September Rainfall [1893-2008]');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_VERT);
  $graph->legend->SetPos(0.5,0.01, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$sc1=new ScatterPlot($last, $first);
//$sc1->SetLegend("Ames May 17");
$sc1->mark->SetType(MARK_FILLEDCIRCLE);
$sc1->mark->SetFillColor("blue");
$graph->Add($sc1);

// Display the graph
$graph->Stroke();
?>
