<?php
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_bar.php");

// 16 Oct 2007 select extract(year from day) as year, count(*) from (select day, count(*) from alldata WHERE precip >= 4 and year > 1950 and stationid IN (select stationid from alldata WHERE day = '1971-01-01') GROUP by day) as foo WHERE count > 1 GROUP by year ORDER by count ASC;


$d=array(12.26, 10.35, 10.32, 10.19);
$datax=array("1993\n28 Jun - 29 Jul", 
             "2008\n23 May - 23 Jun",
             "2010\n24 May - 24 Jun",
             "1926\n29 Aug - 29 Sep",
);

// Size of graph
$width=640; 
$height=480;

// Set the basic parameters of the graph 
$graph = new Graph($width,$height,'auto');
$graph->SetScale("textlin");
$graph->img->SetAntiAliasing();


// No frame around the image
$graph->SetFrame(false);

// Rotate graph 90 degrees and set margin
$graph->Set90AndMargin(190,5,32,40);

// Set white margin color
$graph->SetMarginColor('white');

// Use a box around the plot area
$graph->SetBox();

// Use a gradient to fill the plot area
$graph->SetBackgroundGradient('blue','lightblue',GRAD_HOR,BGRAD_PLOT);

// Setup title
$graph->title->Set("Wettest 31 days in Iowa");
$graph->subtitle->Set("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nIEM Estimated statewide average [inch]");
$graph->title->SetFont(FF_VERDANA,FS_BOLD,20);
$graph->subtitle->SetFont(FF_VERDANA,FS_BOLD,20);

// Setup X-axis
$graph->xaxis->SetTickLabels($datax);
$graph->xaxis->SetFont(FF_VERDANA,FS_NORMAL,16);

// Some extra margin looks nicer
$graph->xaxis->SetLabelMargin(10);

// Label align for X-axis
$graph->xaxis->SetLabelAlign('right','center');
$graph->xaxis->SetPos("min");

// Add some grace to y-axis so the bars doesn't go
// all the way to the end of the plot area
$graph->yaxis->scale->SetGrace(20);

// We don't want to display Y-axis
$graph->yaxis->Hide();

$graph->legend->Pos(0.1,0.92);
$graph->legend->SetLayout(LEGEND_HOR);


// Now create a bar pot
$bplot = new BarPlot($d);
$bplot->SetShadow();
$bplot->SetFillGradient('orange','red',GRAD_HOR);
$bplot->value->Show();
$bplot->value->SetFont(FF_ARIAL,FS_BOLD,14);
//$bplot->value->SetAlign('left','center');
$bplot->value->SetColor("black");
$bplot->value->SetFormat('%.2f');
//$bplot->SetLegend("2008");
$bplot->SetValuePos('max');

$graph->Add($bplot);

// Add some explanation text
$txt = new Text("* IEM Computed [1893-2010]");
$txt->SetPos(1,-5);
$txt->SetFont(FF_COMIC,FS_NORMAL,10);
$graph->Add($txt);

// .. and stroke the graph
$graph->Stroke();
?>
