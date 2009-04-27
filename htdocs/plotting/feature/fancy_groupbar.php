<?php
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_bar.php");

// 16 Oct 2007 select extract(year from day) as year, count(*) from (select day, count(*) from alldata WHERE precip >= 4 and year > 1950 and stationid IN (select stationid from alldata WHERE day = '1971-01-01') GROUP by day) as foo WHERE count > 1 GROUP by year ORDER by count ASC;


$d2008=array(45.94, 48.33, 47.95, 49.42, 52.42);
$d1993=array(53.07, 63.19, 60.12, 58.88, 58.58);
$davg=array(33.15, 37.27, 33.41, 34.72, 39.34);
$datax=array("Waterloo", "Iowa City", "Cedar Rapids", "Des Moines", "Lamoni");

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
$graph->Set90AndMargin(90,20,20,28);

// Set white margin color
$graph->SetMarginColor('white');

// Use a box around the plot area
$graph->SetBox();

// Use a gradient to fill the plot area
$graph->SetBackgroundGradient('blue','lightblue',GRAD_HOR,BGRAD_PLOT);

// Setup title
$graph->title->Set("Yearly Rainfall Totals");
//$graph->subtitle->Set("Ames Climate Site AMSI4 since 1951");
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

$graph->legend->Pos(0.1,0.92);
$graph->legend->SetLayout(LEGEND_HOR);


// Now create a bar pot
$bplot = new BarPlot($d2008);
$bplot->SetShadow();
$bplot->SetFillGradient('purple','lightblue',GRAD_HOR);
$bplot->value->Show();
$bplot->value->SetFont(FF_ARIAL,FS_BOLD,10);
//$bplot->value->SetAlign('left','center');
$bplot->value->SetColor("white");
$bplot->value->SetFormat('%.2f');
$bplot->SetLegend("2008");
$bplot->SetValuePos('max');

$bplot2 = new BarPlot($d1993);
$bplot2->SetShadow();
$bplot2->SetFillGradient('red','orange',GRAD_HOR);
$bplot2->value->Show();
$bplot2->value->SetFont(FF_ARIAL,FS_BOLD,10);
//$bplot->value->SetAlign('left','center');
$bplot2->value->SetColor("white");
$bplot2->value->SetFormat('%.2f');
$bplot2->SetLegend("1993");
$bplot2->SetValuePos('max');

$bplot3 = new BarPlot($davg);
$bplot3->SetShadow();
$bplot3->SetFillGradient('green','darkblue',GRAD_HOR);
$bplot3->value->Show();
$bplot3->value->SetFont(FF_ARIAL,FS_BOLD,10);
//$bplot->value->SetAlign('left','center');
$bplot3->value->SetColor("white");
$bplot3->value->SetFormat('%.2f');
$bplot3->SetLegend("Climate");
$bplot3->SetValuePos('max');

// Add the bar to the graph
$gp = new GroupBarPlot( Array($bplot3,$bplot,$bplot2) );
$graph->Add($gp);

// Add some explanation text
$txt = new Text("* 2008 data unofficial, Sep 2008 very close");
$txt->SetPos(280,240);
$txt->SetFont(FF_COMIC,FS_NORMAL,8);
//$graph->Add($txt);

// .. and stroke the graph
$graph->Stroke();
?>
