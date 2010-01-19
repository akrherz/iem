<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");

$highs = Array();
$lows = Array();
$highs2 = Array();
$lows2 = Array();

$coop = iemdb('coop');

$rs = pg_query($coop, "SELECT * from alldata WHERE stationid = 'ia0200' and
       month = 11");
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  if ($row["year"] < 2009){
    $highs[] = $row["high"];
    $lows[] = $row["low"];
  } else {
    $highs2[] = $row["high"];
    $lows2[] = $row["low"];
  }
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");


// Create the graph. These two calls are always required
$graph = new Graph(300,300);
$graph->SetScale("lin");
$graph->img->SetMargin(45,10,45,45);

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
//$graph->xaxis->scale->SetAutoMax(5); 
//$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetTitleMargin(10);


$graph->yaxis->SetTitle("High Temperature [F]");
$graph->xaxis->SetTitle("Low Temperature [F]");
$graph->title->Set("Ames November Temperatures\n 1893-2009");

  $graph->tabtitle->SetFont(FF_ARIAL,FS_BOLD,10);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_VERT);
  $graph->legend->SetPos(0.06,0.65, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$sc1=new ScatterPlot($highs, $lows);
$sc1->SetLegend("1893-2008");
$sc1->mark->SetType(MARK_FILLEDCIRCLE);
$sc1->mark->SetFillColor("blue");
$graph->Add($sc1);

$sc2=new ScatterPlot($highs2, $lows2);
$sc2->SetLegend("2009");
$sc2->mark->SetType(MARK_FILLEDCIRCLE);
$sc2->mark->SetFillColor("red");
$graph->Add($sc2);

// Display the graph
$graph->Stroke();
?>
