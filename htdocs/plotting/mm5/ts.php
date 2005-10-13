<?php
$ydata = array();
$ydata2 = array();
$xlabel= array();

$fcontents = file('/home/akrherz/time_series.out');
//$fcontents = file('/home/mm5/frost/tfd.out');
$i = 0;
$k = 0;
while (list ($line_num, $line) = each ($fcontents)) {
     $parts = preg_split ("/[\s,]+/", $line);
     if ( $parts[2] >= 0 ) {
	$xlabel[$k] = $parts[1] ;
	$ydata[$k] = $parts[2];
	$ydata2[$k] = $parts[3];
	$k++;
    }
}


include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(650,300,"example1");
//$graph->SetScale("textlin",0,.050);
$graph->SetScale("textlin");
$graph->img->SetMargin(60,10,30,100);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetTextTicks(60);
$graph->xaxis->SetLabelAngle(90);
//$graph->yaxis->scale->ticks->Set(.005,.001);
//$graph->yaxis->scale->ticks->SetPrecision(4);
$graph->title->Set("ISU MM5 Forecast");
$graph->legend->Pos(0.01,0.01);

$graph->title->SetFont(FF_FONT1,FS_BOLD,16);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Time");
$graph->xaxis->SetTitleMargin(68);
$graph->yaxis->SetTitleMargin(48);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);


// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetLegend("Air Temp");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetLegend("Dew point");
$lineplot2->SetColor("blue");

$graph->Add($lineplot);
$graph->Add($lineplot2);

// Display the graph
$graph->Stroke();
?>

