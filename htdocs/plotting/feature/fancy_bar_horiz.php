<?php
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_bar.php");

// 16 Oct 2007 select extract(year from day) as year, count(*) from (select day, count(*) from alldata WHERE precip >= 4 and year > 1950 and stationid IN (select stationid from alldata WHERE day = '1971-01-01') GROUP by day) as foo WHERE count > 1 GROUP by year ORDER by count ASC;


//$datay1=array(4, 2, 6, 4, 2, 6, 6, 2, 1, 0, 0, 0, 0, 1, 1);
//$datay2=array(1, 4, 1, 3, 1, 1, 1, 0, 1, 3, 1, 1, 1, 1, 4);
$datay1=array(6, 1, 0, 0, 2, 0, 2, 7, 7, 4, 4, 5, 6, 7, 5);
$datay2=array(3, 2, 4, 5, 7, 6, 11, 7, 4, 2, 2, 2, 3, 2, 3);
$datax=array(-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7);

// Size of graph
$width=600; 
$height=360;

// Set the basic parameters of the graph 
$graph = new Graph($width,$height,'auto');
$graph->SetScale("textlin");
$graph->img->SetAntiAliasing();


// No frame around the image
$graph->SetFrame(false);

// Rotate graph 90 degrees and set margin
$graph->SetMargin(40,5,50,35);

// Set white margin color
$graph->SetMarginColor('white');

// Use a box around the plot area
$graph->SetBox();

// Use a gradient to fill the plot area
$graph->SetBackgroundGradient('white','tan',GRAD_HOR,BGRAD_PLOT);

// Setup title
$graph->title->Set("Daily High/Low Record Temperatures");
$graph->subtitle->Set("when a daily precipitation record is set [Ames]");
$graph->title->SetFont(FF_VERDANA,FS_BOLD,11);

// Setup X-axis
$graph->xaxis->SetTickLabels($datax);
$graph->xaxis->SetFont(FF_VERDANA,FS_NORMAL,8);

// Some extra margin looks nicer
$graph->xaxis->SetLabelMargin(10);

// Label align for X-axis
//$graph->xaxis->SetLabelAlign('right','center');

// Add some grace to y-axis so the bars doesn't go
// all the way to the end of the plot area
$graph->yaxis->scale->SetGrace(20);

// We don't want to display Y-axis
//$graph->yaxis->Hide();
$graph->yaxis->SetTitle("Current Records");
$graph->xaxis->SetTitle("Days Prior                             Day Of                               Days After  ");

// Now create a bar pot
$bplot1 = new BarPlot($datay1);

// Now create a bar pot
$bplot2 = new BarPlot($datay2);

$bplot1->SetFillColor('red@0.3');
//$bplot1->value->Show();
$bplot2->SetFillColor('blue@0.3');
//$bplot1->SetShadow('black@0.4');
//$bplot2->SetShadow('black@0.4');
$bplot1->SetLegend('Minimum High');
$bplot2->SetLegend('Maximum Low');

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->SetPos(0.01,0.24, 'right', 'top');

$gbarplot = new GroupBarPlot(array($bplot1,$bplot2));
$gbarplot->SetWidth(0.7);
$graph->Add($gbarplot);

// Add some explanation text
//$txt = new Text("[ Percent of time in a given condition ]");
//$txt->SetPos(280,220);
//$txt->SetFont(FF_COMIC,FS_NORMAL,8);
//$graph->Add($txt);

// .. and stroke the graph
$graph->Stroke();
?>
