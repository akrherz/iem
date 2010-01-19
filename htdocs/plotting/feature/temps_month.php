<?php
include("../../../config/settings.inc.php");
include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");
include("$rootpath/include/database.inc.php");

$mydb = iemdb("coop");

$maxs = Array();
$mins = Array();
$rs = pg_query($mydb, "select month, max(range), min(range) from (select year, month, max(high) - min(low) as range from alldata GROUP by year, month) as foo GROUP by month ORDER by month ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $maxs[] = $row["max"];
  $mins[] = $row["min"];
}
$d2009 = Array();
$rs = pg_query($mydb, "select month, max(range), min(range) from (select year, month, max(high) - min(low) as range from alldata where year = 2009 GROUP by year, month) as foo GROUP by month ORDER by month ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $d2009[] = $row["max"];
}


// Size of graph
$width=640; 
$height=480;

// Set the basic parameters of the graph 
$graph = new Graph($width,$height);
$graph->SetScale("linlin",20,140,0,13);
$graph->img->SetAntiAliasing();

// No frame around the image
$graph->SetFrame(false);

// Rotate graph 90 degrees and set margin
$graph->SetMargin(40,15,50,40);
$graph->legend->SetLayout(LEGEND_HOR);

// Set white margin color
$graph->SetMarginColor('white');

// Use a box around the plot area
$graph->SetBox();

// Use a gradient to fill the plot area
$graph->SetBackgroundGradient('white','tan',GRAD_HOR,BGRAD_PLOT);

// Setup title
$graph->title->Set("Iowa Monthly Temperature Range");
$graph->subtitle->Set("Max High minus Min Low (1893-2009)");
$graph->title->SetFont(FF_VERDANA,FS_BOLD,11);

// Setup X-axis
//$graph->xaxis->SetTickLabels($datax);
$graph->xaxis->SetFont(FF_VERDANA,FS_NORMAL,8);

// Some extra margin looks nicer
//$graph->xaxis->SetLabelMargin(10);

// Label align for X-axis
//$graph->xaxis->SetLabelAlign('right','center');

// Add some grace to y-axis so the bars doesn't go
// all the way to the end of the plot area
//$graph->yaxis->scale->SetGrace(20);
//$graph->xaxis->SetLabelFormat('%.0f');
//$graph->xaxis->SetTitle("Day of July");
//$graph->xaxis->scale->SetAutoMax(13);
//$graph->xaxis->HideFirstLastLabel();
$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetTextTickInterval(1);
//$graph->xaxis->SetTextLabelInterval( 1 );
$graph->xaxis->scale->ticks->Set(1,1);
$graph->xaxis->SetTickLabels( Array("","JAN","FEB","MAR","APR","MAY","JUN","JUL",
                                "AUG","SEP","OCT","NOV","DEC", "") );

// We don't want to display Y-axis
//$graph->yaxis->Hide();
$graph->yaxis->SetTitle("Temperature Range [F] ");
$graph->yaxis->SetPos("min");
$graph->yaxis->SetTitleMargin(30);

// Now create a bar pot
$bplot1 = new ScatterPlot($maxs, Array(1,2,3,4,5,6,7,8,9,10,11,12) );
$bplot1->SetColor('blue@0.3');
$bplot1->mark->SetType(MARK_FILLEDCIRCLE);
$bplot1->SetLegend('Largest');
$bplot1->value->Show();
$bplot1->value->SetFormat('%.0f');
$bplot1->value->SetMargin(13);
$graph->Add($bplot1);

$sc = new ScatterPlot( $mins, Array(1,2,3,4,5,6,7,8,9,10,11,12) );
$sc->mark->SetType(MARK_FILLEDCIRCLE);
$sc->mark->SetFillColor("green");
$sc->SetLegend("Smallest");
$sc->value->Show();
$sc->value->SetFormat('%.0f');
$sc->value->SetMargin(-13);
$graph->Add($sc);

$sc2 = new ScatterPlot( $d2009, Array(1,2,3,4,5,6,7,8,9,10,11,12) );
$sc2->mark->SetType(MARK_STAR);
$sc2->mark->SetFillColor("red");
$sc2->SetLegend("2009");
$sc2->value->Show();
$sc2->value->SetFormat('%.0f');
$sc2->value->SetMargin(13);
$graph->Add($sc2);


// .. and stroke the graph
$graph->Stroke();
?>
