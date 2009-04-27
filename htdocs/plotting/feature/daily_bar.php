<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$pgconn = iemdb('coop');

$times = Array();
$cnt = Array();
$highs = Array();
$min_high = Array();

$rs = pg_query($pgconn, "SELECT min_high, low from climate WHERE station = 'ia0200' ORDER by valid ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $highs[] = $row["low"];
  $min_high[] = $row["min_high"];
}


$ts0 = mktime(0,0,0,1,1,2000);

$fc = file('lows2.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split (",", $line);
   $times[] = $ts0 + (intval($tokens[0]) -1 )*86400;
   $cnt[] = intval($tokens[1]);
 }

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,300,"example1");
$graph->SetScale("datlin",0,40);
$graph->SetY2Scale("lin",-55,75);

$graph->SetBackgroundGradient('white','green',GRAD_HOR,BGRAD_PLOT);
$graph->SetMarginColor('white');
//$graph->SetColor('white');
//$graph->SetBackgroundGradient('navy','white',GRAD_HOR,BGRAD_MARGIN);
$graph->SetFrame(true,'white');

$graph->ygrid->Show();
$graph->xgrid->Show();
$graph->ygrid->SetColor('gray@0.5');
$graph->xgrid->SetColor('gray@0.5');

$graph->img->SetMargin(40,40,25,80);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
//$graph->xaxis->SetTickLabels($years);
//$graph->xaxis->SetTextTickInterval(10);
//$graph->xaxis->SetTitleMargin(70);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("# of Years [1893-2008]");
$graph->y2axis->SetTitle("Temperature [F]");
$graph->tabtitle->Set('Ames Daily High Temp & Average Low');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->SetPos(0.0,0.9, 'right', 'top');
//$graph->legend->SetLineSpacing(3);



// Create the linear plot
$lineplot=new BarPlot($cnt, $times);
$lineplot->SetLegend("# (High < Avg Low)");
$lineplot->SetFillColor("blue");
//$lineplot->SetWidth(1);
$graph->Add($lineplot);

$lineplot2=new LinePlot($min_high, $times);
$lineplot2->SetLegend("Min High");
$lineplot2->SetColor("red");
$lineplot2->SetWeight(2);
$graph->AddY2($lineplot2);

$lineplot3=new LinePlot($highs, $times);
$lineplot3->SetLegend("Avg Low");
$lineplot3->SetColor("black");
$lineplot3->SetWeight(2);
$graph->AddY2($lineplot3);



// Display the graph
$graph->Stroke();
?>
