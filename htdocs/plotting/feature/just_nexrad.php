<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");

$radtimes = Array();
$n0r = Array();
$dry = Array();
$dcnt = 0;
$fc = file('jun2010.txt');
while (list ($line_num, $line) = each ($fc)) {
  $tokens = split (" ", $line);
  $radtimes[] = strtotime( $tokens[0] ." ". $tokens[1] ) - (5*3600);
  $n0r[] = floatval($tokens[2]);
  if (floatval($tokens[2]) < 10){ $dcnt += 1.0/24.0; }
  else {$dcnt = 0;}
  $dry[] = $dcnt;
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/jpgraph/jpgraph_mgraph.php");

$pheight = 300;


// Create the graph. These two calls are always required
$graph = new Graph(640,$pheight,"example1");
$graph->SetScale("datlin");
//$graph->SetY2Scale("lin");
$graph->img->SetMargin(47,5,60,5);
$graph->SetColor("white");
$graph->SetMarginColor("white");
$graph->SetFrame(false);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTitleMargin(30);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,14);
//$graph->xaxis->SetTitle("25 JAN                         26 JAN");

//$graph->yaxis->SetColor("red");
//$graph->yaxis->title->SetColor("red");
$graph->yaxis->SetTitleMargin(24);
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,8);
$graph->yaxis->SetTitle("Est. Coverage [%]");

$graph->title->Set("June-August 2010 in Iowa");
$graph->subtitle->Set("a) coverage of 10+dBZ NEXRAD returns\n b) period with < 10% coverage");
$graph->title->SetFont(FF_ARIAL,FS_BOLD,14);

//$graph->y2axis->title->SetFont(FF_ARIAL,FS_BOLD,12);
//$graph->y2axis->SetColor("blue");
//$graph->y2axis->SetTitleMargin(34);
//$graph->y2axis->title->SetColor("blue");
//$graph->y2axis->SetTitle("Mean Wind Speed [mph]");


  $graph->legend->SetLayout(LEGEND_VERT);
  $graph->legend->SetPos(0.2,0.08, 'right', 'top');
//  $graph->legend->SetLineSpacing(10);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();

// Create the linear plot
$lineplot=new LinePlot($n0r,$radtimes);
//$lineplot->SetLegend("10+ dBZ NEXRAD Coverage");
$lineplot->SetColor("blue");
$lineplot->SetFillColor("blue");
$lineplot->SetWeight(2);
$graph->Add($lineplot);


// Create the graph. These two calls are always required
$graph2 = new Graph(640,$pheight,"example1");
$graph2->SetScale("datlin");
//$graph->SetY2Scale("lin");
$graph2->img->SetMargin(47,5,5,60);
$graph2->SetColor("white");
$graph2->SetMarginColor("white");
$graph2->SetFrame(false);

$graph2->xaxis->SetLabelAngle(90);
$graph2->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph2->xaxis->SetPos("min");
$graph2->xaxis->SetTitleMargin(30);
$graph2->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,14);
//$graph->xaxis->SetTitle("25 JAN                         26 JAN");

//$graph->yaxis->SetColor("red");
//$graph->yaxis->title->SetColor("red");
$graph2->yaxis->SetTitleMargin(28);
$graph2->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,10);
$graph2->yaxis->SetTitle("Dry Period [days]");

//$graph2->title->Set("Iowa Storm Systems");
//$graph2->subtitle->Set("coverage of 10+dBZ NEXRAD returns (Dec09-Jan10)");
$graph2->title->SetFont(FF_ARIAL,FS_BOLD,14);

//$graph->y2axis->title->SetFont(FF_ARIAL,FS_BOLD,12);
//$graph->y2axis->SetColor("blue");
//$graph->y2axis->SetTitleMargin(34);
//$graph->y2axis->title->SetColor("blue");
//$graph->y2axis->SetTitle("Mean Wind Speed [mph]");


  $graph2->legend->SetLayout(LEGEND_VERT);
  $graph2->legend->SetPos(0.2,0.08, 'right', 'top');
//  $graph->legend->SetLineSpacing(10);

  $graph2->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph2->ygrid->Show();
  $graph2->xgrid->Show();

// Create the linear plot
$lineplot2=new LinePlot($dry,$radtimes);
//$lineplot->SetLegend("10+ dBZ NEXRAD Coverage");
$lineplot2->SetColor("brown");
$lineplot2->SetFillColor("brown");
$lineplot2->SetWeight(2);
$graph2->Add($lineplot2);

/* Multi Graph */
$mgraph = new MGraph();
$mgraph->SetMargin(2,2,2,2);
$mgraph->SetFrame(true,'darkgray',2);
$mgraph->AddMix($graph,0,0);
$mgraph->AddMix($graph2,0,$pheight);
$mgraph->Stroke();

?>
