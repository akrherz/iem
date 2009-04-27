<?php
include("../../../config/settings.inc.php");


$times = Array();
$cnt = Array();
$ncnt = Array();
$ratio = Array();
$obs = Array();

$ts0 = mktime(0,0,0,1,1,2001);

$fc = file('cnt_next_freeze.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split (",", $line);
   if ($tokens[0] < 200){ $times[] = ($tokens[0] - 1 + 365) * 86400 + $ts0; }
   else { $times[] = ($tokens[0] - 1) * 86400 + $ts0; }
   $cnt[] = $tokens[1];
   $ncnt[] = $tokens[2];
   if ($tokens[1] == 0){ $ratio[] = 0; }
   else { $ratio[] = $tokens[2] / $tokens[1] * 100; }
   $obs[] = $tokens[1] / 116.0 * 100.0;
 }


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,300,"example1");
$graph->SetScale("datlin");
$graph->img->SetMargin(40,10,50,50);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

$graph->xaxis->SetTitleMargin(70);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("Frequency [%]");
//$graph->tabtitle->Set('Recent Comparison');
$graph->title->Set('Ames high temps below freezing');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.01,0.07, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new LinePlot($ratio, $times);
$lineplot->SetLegend("When Previous Day < 32");
$lineplot->SetColor("blue");
$graph->Add($lineplot);

$lineplot2=new LinePlot($obs, $times);
$lineplot2->SetLegend("Overall");
$lineplot2->SetColor("red");
$graph->Add($lineplot2);


// Display the graph
$graph->Stroke();
?>
