<?php
include("../../../config/settings.inc.php");


$years = Array();
$cnt = Array();

$ts0 = mktime(0,0,0,1,1,1893);

$fc = file('lows_year.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split (",", $line);
   $cnt[] = intval($tokens[1]);
   $years[] = $tokens[0];
 }

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,600,"example1");
$graph->SetScale("textlin",-150,150);
$graph->img->SetMargin(40,10,50,50);

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTickLabels($years);
$graph->xaxis->SetTextTickInterval(10);
$graph->xaxis->SetTitleMargin(70);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("Number of Days");
$graph->tabtitle->Set('Ames High Temperature');
$graph->title->Set('Yearly sum days above average');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

//  $graph->legend->SetLayout(LEGEND_HOR);
//  $graph->legend->SetPos(0.01,0.07, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new BarPlot($cnt);
//$lineplot->SetLegend("When Previous Day < 32");
$lineplot->SetColor("blue");
$graph->Add($lineplot);



// Display the graph
$graph->Stroke();
?>
