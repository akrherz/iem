<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");

$highs = Array( -0.577999,   10.6345,   13.3761,   13.4771,   9.18349,   7.77061,    0.7248,   -2.8899,  -10.8807,  -14.4312,   -17.266,   -8.3854);
$lows = Array( -3.39446,  10.1249,  12.4679,   12.055,  10.8624,   6.6881, 0.623898,  -3.1376, -11.8991, -10.4221, -14.2018,  -9.7339);


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");


// Create the graph. These two calls are always required
$graph = new Graph(600,480,"example1");
$graph->SetScale("textlin",-20,20);

$graph->SetBackgroundGradient('red@0.7','blue@0.7',GRAD_HOR,BGRAD_PLOT);
$graph->SetMarginColor('white');
//$graph->SetColor('white');
//$graph->SetBackgroundGradient('navy','white',GRAD_HOR,BGRAD_MARGIN);
$graph->SetFrame(true,'white');

$graph->ygrid->Show();
$graph->xgrid->Show();
$graph->ygrid->SetColor('gray@0.5');
$graph->xgrid->SetColor('gray@0.5');

$graph->img->SetMargin(45,5,25,25);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTickLabels( Array("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT","NOV","DEC") );
//$graph->xaxis->SetTextTickInterval(10);
//$graph->xaxis->SetTitleMargin(70);

$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,10);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,14);
//$graph->xaxis->SetTitle("* thru September 18th");
//$graph->xaxis->title->SetMargin(20);
$graph->yaxis->SetTitle('Temp Difference [°F]');
$graph->title->Set('Ames Daily Climatology Difference');
$graph->subtitle->Set('between the first and last of the month');
$graph->title->SetFont(FF_ARIAL,FS_BOLD,10);

//$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->SetPos(0.1,0.2, 'right', 'top');
//$graph->legend->SetLineSpacing(3);



// Create the linear plot
$lineplot=new BarPlot( $highs );
$lineplot->SetLegend("High Temp");
$lineplot->SetFillColor("red");
$lineplot->value->Show();
$lineplot->SetValuePos('center');
$lineplot->value->SetFont(FF_ARIAL,FS_BOLD,10);
$lineplot->value->SetColor("white");
$lineplot->value->SetFormat('%.0f');
//$lineplot->SetWidth(1);

// Create the linear plot
$lineplot2=new BarPlot( $lows );
$lineplot2->SetLegend("Low Temp");
$lineplot2->SetFillColor("blue");
$lineplot2->value->Show();
$lineplot2->SetValuePos('center');
$lineplot2->value->SetFont(FF_ARIAL,FS_BOLD,10);
$lineplot2->value->SetFormat('%.0f');
$lineplot2->value->SetColor("white");
//$lineplot->SetWidth(1);

$gp = new GroupBarPlot(Array($lineplot,$lineplot2));
$graph->Add($gp);


// Display the graph
$graph->Stroke();
?>
