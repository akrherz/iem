<?php
include("../../../config/settings.inc.php");

$hours = Array();
$dwpf = Array();
$tmpf = Array();

$fc = file('hourly.txt');
while (list ($line_num, $line) = each ($fc)) {
   $tokens = split (",", $line);
   $tmpf[] = floatval($tokens[2]);
   $dwpf[] = floatval($tokens[1]);
   $hours[] = $tokens[0];
 }

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");

$graph = new Graph(620,480,"example1");
$graph->SetScale("textlin");
//$graph->SetY2Scale("lin");
$graph->SetFrame(false);
$graph->SetBox(true);
$graph->img->SetMargin(40,35,20,50);

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTickLabels($hours);
$graph->xaxis->SetTextTickInterval(6);
//$graph->xaxis->HideTicks();
$graph->xaxis->SetTitleMargin(20);
//$graph->yaxis->SetTitleMargin(18);

//$graph->yaxis->SetColor('blue');
//$graph->yaxis->title->SetColor('blue');

$graph->xaxis->title->SetFont(FF_ARIAL,FS_NORMAL,10);
$graph->yaxis->title->SetFont(FF_ARIAL,FS_NORMAL,10);
$graph->xaxis->SetTitle("48 hours before and after last sub 32F");
$graph->yaxis->SetTitle("Temperature [F]");
//$graph->tabtitle->Set('Ames (1893-2009)');
$graph->title->Set("1973-2009 Des Moines Temperature\nComposite around Last Spring Sub 32F");
//$graph->subtitle->Set("number of severe t'storm and tornado \ncounty based warnings");

  $graph->title->SetFont(FF_ARIAL,FS_NORMAL,12);
  $graph->subtitle->SetFont(FF_ARIAL,FS_NORMAL,10);
  $graph->SetColor('wheat');

//  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.5,0.15, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();

$lineplot=new LinePlot($tmpf);
$lineplot->SetLegend("Air Temp");
$lineplot->SetColor("red");
$lineplot->SetWeight(3);
$graph->Add($lineplot);

$lineplot2=new LinePlot($dwpf);
$lineplot2->SetLegend("Dew Point");
$lineplot2->SetColor("blue");
$lineplot2->SetWeight(3);
$graph->Add($lineplot2);


$graph->Stroke();
?>
