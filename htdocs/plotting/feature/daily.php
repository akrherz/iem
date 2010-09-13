<?php
include("../../../config/settings.inc.php");


$ts0 = mktime(0,0,0,1,1,2010);
$dates = Array();
$dates2 = Array();
$y1 = Array();
$y2 = Array();
$y3 = Array();

$fc = file('daily.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split ("\|", $line);
   $y1[] = floatval($tokens[1]);
   //$dates[] = $ts0 + (86400 * $line_num);
   $dates[] = strtotime( $tokens[0] );
 }
$yavg = Array();
$yavg[] = $y1[0];
$yavg[] = $y1[1];
$yavg[] = $y1[2];
for ($i=3;$i<(sizeof($y1)-3);$i++){
  $yavg[] = ($y1[$i-3] + $y1[$i-2] + $y1[$i-1] + $y1[$i] + $y1[$i+1] + $y1[$i+2] + $y1[$i+3]) / 7.0;
}
$yavg[] = $y1[sizeof($y1)-3];
$yavg[] = $y1[sizeof($y1)-2];
$yavg[] = $y1[sizeof($y1)-1];

$fc = file('daily2.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split ("\|", $line);
   $y2[] = floatval($tokens[1]);
   $dates2[] = $ts0 + (86400 * $line_num);
}
$yavg2 = Array();
$yavg2[] = $y2[0];
$yavg2[] = $y2[1];
$yavg2[] = $y2[2];
for ($i=3;$i<(sizeof($y2)-3);$i++){
  $yavg2[] = ($y2[$i-3] + $y2[$i-2] + $y2[$i-1] + $y2[$i] + $y2[$i+1] + $y2[$i+2] + $y2[$i+3]) / 7.0;
}
$yavg2[] = $y2[sizeof($y2)-3];
$yavg2[] = $y2[sizeof($y2)-2];
$yavg2[] = $y2[sizeof($y2)-1];
/*
$fc = file('daily3.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split (",", $line);
   $y3[] = floatval($tokens[1]);
}
*/

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_plotline.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,280,"example1");
$graph->SetScale("datelin",0,26);
$graph->img->SetMargin(40,5,35,50);
$graph->SetMarginColor('white');
$graph->SetFrame(false);
$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
//$graph->xaxis->SetTickLabels($years);
//$graph->xaxis->SetTextTickInterval(86400);
$graph->xaxis->HideTicks();
$graph->xaxis->SetTitleMargin(20);
$graph->yaxis->SetTitleMargin(22);
//$graph ->xaxis->scale-> SetDateAlign( MONTHADJ_1 );
$graph->xtick_factor = 1;

$graph->xaxis->SetLabelFormatCallback('DateCallback');


function DateCallback($aVal) {
  if (date('d',$aVal) == 1)
    return date('M d',$aVal);
  else
    return "";
}

$graph->yaxis->HideZeroLabel();
$graph->ygrid->SetFill(true,'pink@0.5','skyblue@0.5');
//$graph->xgrid->Show();
$graph->ygrid->Show();

$graph->yaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);
//$graph->xaxis->SetTitle("Year");
$graph->yaxis->SetTitle("Wind Speed [mph]");

$graph->title->Set("Des Moines Daily Average Wind Speed");
//$graph->subtitle->Set("6AM - 6 PM Daily, 1950-2010");
$graph->title->SetFont(FF_ARIAL,FS_NORMAL,13);
$graph->subtitle->SetFont(FF_ARIAL,FS_NORMAL,12);
$graph->yaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_NORMAL,12);

  $graph->tabtitle->SetFont(FF_ARIAL,FS_NORMAL,12);
  $graph->SetColor('wheat');

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->SetPos(0.01,0.17, 'right', 'top');
//$graph->legend->SetLineSpacing(3);



// Create the linear plot
$lineplot=new BarPlot($y1, $dates);
$lineplot->SetLegend("2010 Obs");
//$lineplot->SetFillGradient('white','darkgreen');
//$lineplot->SetStepStyle();
$lineplot->SetColor("blue");
$lineplot->SetWeight(3);
//$lineplot->SetAlign("left");
//$lineplot->SetFillColor("blue");
$graph->Add($lineplot);

// Create the linear plot
$lineplot2=new LinePlot($yavg2, $dates2);
$lineplot2->SetLegend("Climatology");
//$lineplot->SetFillGradient('white','darkgreen');
//$lineplot2->SetStepStyle();
$lineplot2->SetColor("black");
$lineplot2->SetWeight(3);
//$lineplot->SetAlign("left");
//$lineplot2->SetFillColor("blue");
$graph->Add($lineplot2);

// Create the linear plot
//$lineplot3=new LinePlot($y3, $dates);
//$lineplot3->SetLegend("2006");
//$lineplot->SetFillGradient('white','darkgreen');
//$lineplot3->SetStepStyle();
//$lineplot3->SetWeight(3);
//$lineplot3->SetColor("black");
//$lineplot->SetAlign("left");
//$lineplot2->SetFillColor("blue");
//$graph->Add($lineplot3);

//$graph->AddLine(new PlotLine(VERTICAL,strtotime("2009-01-28"),"gray",2));

// Display the graph
$graph->Stroke();
?>
