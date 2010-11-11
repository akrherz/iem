<?php
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_bar.php");

// 16 Oct 2007 select extract(year from day) as year, count(*) from (select day, count(*) from alldata WHERE precip >= 4 and year > 1950 and stationid IN (select stationid from alldata WHERE day = '1971-01-01') GROUP by day) as foo WHERE count > 1 GROUP by year ORDER by count ASC;


$d=array(139, 136, 127, 126, 122, 118);
$datax=array("#1 1977\n 1 May - 16 Sep", 
             "#2 1988\n11 May - 23 Sep",
             "#3 2005\n27 May - 22 Sep",
             "#4 1978\n19 May - 21 Sep",
             "#5 1933\n15 May - 13 Sep",
             "#9 2010\n21 May - 15 Sep",
);

// Size of graph
$width=300; 
$height=300;

// Set the basic parameters of the graph 
$graph = new Graph($width,$height,'auto');
$graph->SetScale("textlin");
$graph->img->SetAntiAliasing();


// No frame around the image
$graph->SetFrame(false);

// Rotate graph 90 degrees and set margin
$graph->Set90AndMargin(130,5,40,40);

// Set white margin color
$graph->SetMarginColor('white');

// Use a box around the plot area
$graph->SetBox();

// Use a gradient to fill the plot area
$graph->SetBackgroundGradient('blue','lightblue',GRAD_HOR,BGRAD_PLOT);

// Setup title
$graph->title->Set("Consec. Days with High Above 70°F\nAmes [1893-2010]");
//$graph->subtitle->Set("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nIEM Estimated statewide average [inch]");
$graph->title->SetFont(FF_VERDANA,FS_BOLD,11);
$graph->subtitle->SetFont(FF_VERDANA,FS_BOLD,20);

// Setup X-axis
$graph->xaxis->SetTickLabels($datax);
$graph->xaxis->SetFont(FF_VERDANA,FS_NORMAL,11);

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
$bplot->value->SetFont(FF_ARIAL,FS_BOLD,10);
//$bplot->value->SetAlign('left','center');
$bplot->value->SetColor("black");
$bplot->value->SetFormat('%.0f');
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
