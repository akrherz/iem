<?php
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_bar.php");

// 16 Oct 2007 select extract(year from day) as year, count(*) from (select day, count(*) from alldata WHERE precip >= 4 and year > 1950 and stationid IN (select stationid from alldata WHERE day = '1971-01-01') GROUP by day) as foo WHERE count > 1 GROUP by year ORDER by count ASC;


$datay=array(11,11,10,9,8,7);
$datax=array("Oct 1978 -\nAug 1979","Jan 1993 -\nNov 1993", "Dec 2007 -\nSep 2008", "Jan 1996 -\nSep 1996", "Jan 1972 -\nAug 1972", "May 1967 -\nNov 1967");

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
$graph->Set90AndMargin(80,20,60,30);

// Set white margin color
$graph->SetMarginColor('white');

// Use a box around the plot area
$graph->SetBox();

// Use a gradient to fill the plot area
$graph->SetBackgroundGradient('blue','lightblue',GRAD_HOR,BGRAD_PLOT);

// Setup title
$graph->title->Set("Consecutive months below\n normal temperature");
$graph->subtitle->Set("Ames Climate Site AMSI4 since 1951");
$graph->title->SetFont(FF_VERDANA,FS_BOLD,11);

// Setup X-axis
$graph->xaxis->SetTickLabels($datax);
$graph->xaxis->SetFont(FF_VERDANA,FS_NORMAL,8);

// Some extra margin looks nicer
$graph->xaxis->SetLabelMargin(10);

// Label align for X-axis
$graph->xaxis->SetLabelAlign('right','center');

// Add some grace to y-axis so the bars doesn't go
// all the way to the end of the plot area
$graph->yaxis->scale->SetGrace(20);

// We don't want to display Y-axis
$graph->yaxis->Hide();

// Now create a bar pot
$bplot = new BarPlot($datay);
$bplot->SetShadow();

//You can change the width of the bars if you like
//$bplot->SetWidth(0.5);

// Set gradient fill for bars
$bplot->SetFillGradient('purple','orange',GRAD_HOR);

// We want to display the value of each bar at the top
$bplot->value->Show();
$bplot->value->SetFont(FF_ARIAL,FS_BOLD,10);
//$bplot->value->SetAlign('left','center');
$bplot->value->SetColor("white");
$bplot->value->SetFormat('%.0f');
$bplot->SetValuePos('max');

// Add the bar to the graph
$graph->Add($bplot);

// Add some explanation text
$txt = new Text("* 2008 data unofficial, Sep 2008 very close");
$txt->SetPos(280,240);
$txt->SetFont(FF_COMIC,FS_NORMAL,8);
$graph->Add($txt);

// .. and stroke the graph
$graph->Stroke();
?>
