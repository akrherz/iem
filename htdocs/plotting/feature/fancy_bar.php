<?php
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_bar.php");

// 16 Oct 2007 select extract(year from day) as year, count(*) from (select day, count(*) from alldata WHERE precip >= 4 and year > 1950 and stationid IN (select stationid from alldata WHERE day = '1971-01-01') GROUP by day) as foo WHERE count > 1 GROUP by year ORDER by count ASC;


$d=array(-7, -2, -1, 0, 20, 20, 37);
$datax=array("1912", 
             "1942",
             "1979",
             "2010",
             "Average",
             "2009",
             "1939",
);

// Size of graph
$width=320; 
$height=280;

// Set the basic parameters of the graph 
$graph = new Graph($width,$height,'auto');
$graph->SetScale("textlin",-14,44);
$graph->img->SetAntiAliasing();


// No frame around the image
$graph->SetFrame(false);

// Rotate graph 90 degrees and set margin
$graph->Set90AndMargin(110,5,60,28);

// Set white margin color
$graph->SetMarginColor('white');

// Use a box around the plot area
$graph->SetBox();

// Use a gradient to fill the plot area
$graph->SetBackgroundGradient('blue','lightblue',GRAD_HOR,BGRAD_PLOT);

// Setup title
$graph->title->Set("Jan 1 - Jan 7 Average Temp [°F]");
$graph->subtitle->Set("IEM computed for Iowa 1893-2010");
$graph->title->SetFont(FF_VERDANA,FS_BOLD,12);
$graph->subtitle->SetFont(FF_VERDANA,FS_BOLD,10);

// Setup X-axis
$graph->xaxis->SetTickLabels($datax);
$graph->xaxis->SetFont(FF_VERDANA,FS_NORMAL,12);

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
$bplot->value->SetColor("white");
$bplot->value->SetFormat('%.0f');
//$bplot->SetLegend("2008");
//$bplot->SetValuePos('max');

$graph->Add($bplot);

// Add some explanation text
$txt = new Text("");
$txt->SetPos(280,300);
$txt->SetFont(FF_COMIC,FS_NORMAL,10);
$graph->Add($txt);

// .. and stroke the graph
$graph->Stroke();
?>
