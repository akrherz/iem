<?php
include("../../../config/settings.inc.php");
include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_plotline.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");

$fthres = Array();
$fdates = Array();
$lthres = Array();
$ldates = Array();

$fc = file('earliest.txt');
while (list ($line_num, $line) = each ($fc)) {
   $tokens = split (",", $line);
   $fthres[] = floatval($tokens[0]);
   $fdates[] = strtotime( $tokens[1] );
}

$fc = file('latest.txt');
while (list ($line_num, $line) = each ($fc)) {
   $tokens = split (",", $line);
   $lthres[] = floatval($tokens[0]);
   $ldates[] = strtotime( $tokens[1] );
}





// Create the graph. These two calls are always required
$graph = new Graph(640,480,"auto");    
$graph->SetScale("datlin");

$graph->legend->Pos(0.05,0.94);
$graph->legend->SetLayout(LEGEND_HOR);


$graph->SetShadow();
$graph->img->SetMargin(45,20,10,75);

$graph->title->Set("First Temperature Exceedance");
$graph->subtitle->Set("Ames [1893-2009] after 1 January");

//$graph->xaxis->title->Set("Day of May 2008");
$graph->yaxis->title->Set("Temperature Threshold [F]");

$graph->title->SetFont(FF_ARIAL,FS_BOLD,14);
$graph->subtitle->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,10);
$graph->xaxis->SetFont(FF_ARIAL,FS_NORMAL,8);
$graph->yaxis->SetFont(FF_ARIAL,FS_NORMAL,8);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->SetTickLabels($x);
//$graph->xaxis->SetTextTickInterval(5);
//$graph->xaxis->HideTicks();
$graph->SetColor("lightyellow");
$graph->SetMarginColor("khaki");

$graph->xgrid->Show();
$graph->xgrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');

$graph->AddLine(new PlotLine(HORIZONTAL,32,"gray",2));

// Create the bar plots
$lplot = new LinePlot($fthres, $fdates);
$lplot->SetColor("red");
$lplot->SetLegend('Earliest Occurance');
$lplot->SetWeight(3);
//$lplot->SetAlign("left");
$graph->Add($lplot);

$l2plot = new LinePlot($lthres, $ldates);
$l2plot->SetColor("blue");
$l2plot->SetLegend('Latest Occurance');
$l2plot->SetWeight(3);
//$lplot->SetAlign("left");
$graph->Add($l2plot);

$txt=new Text("32 F");
$txt->SetPos(0.7,0.52);
$txt->SetColor('gray');
$txt->SetFont(FF_ARIAL,FS_BOLD);
$graph->AddText($txt);

// Display the graph
$graph->Stroke();
?>
