<?php
include("../../../config/settings.inc.php");


$ts0 = mktime(0,0,0,12,1,2009);
$dates = Array();
$cnt = Array();
$cnt2 = Array();
$cnt3 = Array();

$fc = file('daily.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split (" ", $line);
   $cnt[] = floatval($tokens[sizeof($tokens)-1]);
   $dates[] = $ts0 + (86400 * $line_num);
 }

$fc = file('daily2.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split (",", $line);
   $cnt2[] = floatval($tokens[1]);
}

$fc = file('daily3.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split (",", $line);
   $cnt3[] = floatval($tokens[1]);
}


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_plotline.php");


// Create the graph. These two calls are always required
$graph = new Graph(330,280,"example1");
$graph->SetScale("datelin");
$graph->img->SetMargin(40,5,65,50);
$graph->SetMarginColor('white');
$graph->SetFrame(false);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
//$graph->xaxis->SetTickLabels($years);
//$graph->xaxis->SetTextTickInterval(10);
//$graph->xaxis->HideTicks();
$graph->xaxis->SetTitleMargin(20);
$graph->yaxis->SetTitleMargin(22);

$graph->yaxis->HideZeroLabel();
$graph->ygrid->SetFill(true,'pink@0.5','skyblue@0.5');
$graph->xgrid->Show();
$graph->ygrid->Show();

$graph->yaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);
//$graph->xaxis->SetTitle("Year");
$graph->yaxis->SetTitle("Snow Depth [inch]");

$graph->title->Set("Des Moines Snow Depth");
$graph->subtitle->Set("Record stretch of 5+ inch depth\n9 Dec 2009 - current (57 days)");
$graph->title->SetFont(FF_ARIAL,FS_NORMAL,14);
$graph->subtitle->SetFont(FF_ARIAL,FS_NORMAL,12);
$graph->yaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);

  $graph->tabtitle->SetFont(FF_ARIAL,FS_NORMAL,12);
  $graph->SetColor('wheat');

//$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->SetPos(0.05,0.6, 'right', 'top');
//$graph->legend->SetLineSpacing(3);



// Create the linear plot
$lineplot=new LinePlot($cnt, $dates);
//$lineplot->SetLegend("Min Low");
//$lineplot->SetFillGradient('white','darkgreen');
//$lineplot->SetStepStyle();
$lineplot->SetColor("blue");
$lineplot->SetWeight(3);
//$lineplot->SetAlign("left");
//$lineplot->SetFillColor("blue");
$graph->Add($lineplot);

// Create the linear plot
$lineplot2=new LinePlot($cnt2, $dates);
$lineplot2->SetLegend("Min High");
//$lineplot->SetFillGradient('white','darkgreen');
//$lineplot2->SetStepStyle();
$lineplot2->SetColor("red");
$lineplot2->SetWeight(3);
//$lineplot->SetAlign("left");
//$lineplot2->SetFillColor("blue");
//$graph->Add($lineplot2);

// Create the linear plot
$lineplot3=new LinePlot($cnt3, $dates);
$lineplot3->SetLegend("Max Snowfall");
//$lineplot->SetFillGradient('white','darkgreen');
//$lineplot3->SetStepStyle();
$lineplot3->SetWeight(3);
$lineplot3->SetColor("black");
//$lineplot->SetAlign("left");
//$lineplot2->SetFillColor("blue");
//$graph->Add($lineplot3);

$graph->AddLine(new PlotLine(VERTICAL,strtotime("2009-01-28"),"gray",2));

// Display the graph
$graph->Stroke();
?>
