<?php
// $Id: groupbarex1.php,v 1.2 2002/07/11 23:27:28 aditus Exp $
include ("/mesonet/php/include/jpgraph/jpgraph.php");
include ("/mesonet/php/include/jpgraph/jpgraph_bar.php");

$datay1=array(511,227);
$datay2=array(509,137);

$xlabels = Array("2004", "2005");

$graph = new Graph(200,250,'auto');	
$graph->img->SetMargin(40,30,40,40);
$graph->SetScale("textint");
$graph->SetFrame(true,'blue',1);
$graph->SetColor('lightblue');
$graph->SetMarginColor('lightblue');
$graph->xaxis->SetTickLabels($xlabels);

$graph->xaxis->title->Set('Year');
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetColor('darkblue','black');

$graph->title->Set('May Tornado Stats');
$graph->title->SetFont(FF_FONT1,FS_BOLD);
$graph->yaxis->SetColor('lightblue','darkblue');
$graph->ygrid->SetColor('white');

$bplot1 = new BarPlot($datay1);
$bplot1->SetFillColor('darkblue');
$bplot1->SetWidth(0.4);
$bplot1->SetShadow('darkgray');
$bplot1->SetValuePos('top');
$bplot1->value->Show();
$bplot1->value->SetFont(FF_FONT1,FS_NORMAL,8);
$bplot1->value->SetFormat('%d');
$bplot1->value->SetColor("black","darkred");
$bplot1->SetLegend("Warnings");

$bplot2 = new BarPlot($datay2);
$bplot2->SetFillColor("brown");
$bplot2->SetShadow('darkgray');
$bplot2->SetWidth(0.4);
$bplot2->SetValuePos('top');
$bplot2->value->Show();
$bplot2->value->SetFont(FF_FONT1,FS_NORMAL,8);
$bplot2->value->SetFormat('%d');
$bplot2->value->SetColor("black","darkred");
$bplot2->SetLegend("Tornados");

$gbarplot = new GroupBarPlot(array($bplot1,$bplot2));
$gbarplot->SetWidth(0.8);
$graph->Add($gbarplot);

$graph->Stroke();
?>
