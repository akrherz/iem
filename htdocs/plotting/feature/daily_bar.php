<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$pgconn = iemdb('access');

$times = Array();
$freq = Array();

$rs = pg_query($pgconn, "SELECT day, max(pday) as rain from summary_2010 WHERE network in ('IA_ASOS','AWOS') and day >= '2010-06-01' GROUP by day ORDER by day ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  //$times[] = strtotime( $row["day"] );
  $times[] = date("d", strtotime( $row["day"] ) );
  $freq[] = $row["rain"];
}

//$times = Array();
//$freq = Array();

//$fc = file('daily2.txt');
//while (list ($line_num, $line) = each ($fc)) {
//      $tokens = split (",", $line);
//   $times[] = strtotime($tokens[0]);
//   $freq[] = floatval($tokens[1]);
// }

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,280,"example1");
$graph->SetScale("textlin");
//$graph->SetY2Scale("lin",-55,75);

$graph->SetBackgroundGradient('white','green',GRAD_HOR,BGRAD_PLOT);
$graph->SetMarginColor('white');
//$graph->SetColor('white');
//$graph->SetBackgroundGradient('navy','white',GRAD_HOR,BGRAD_MARGIN);
$graph->SetFrame(true,'white');

$graph->ygrid->Show();
$graph->xgrid->Show();
$graph->ygrid->SetColor('gray@0.5');
$graph->xgrid->SetColor('gray@0.5');

$graph->img->SetMargin(45,5,25,80);

//$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTickLabels($times);
$graph->xaxis->SetTextTickInterval(1);
$graph->yaxis->SetTitleMargin(30);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->SetTitle("Day of June 2010");
$graph->yaxis->SetTitle("Precipitation [in]");
//$graph->y2axis->SetTitle("Temperature [F]");
$graph->title->Set("Daily Maximum Precipitation\nmeasured by Iowa ASOS/AWOS");

$graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->SetPos(0.0,0.9, 'right', 'top');
//$graph->legend->SetLineSpacing(3);



// Create the linear plot
$lineplot=new BarPlot($freq);
//$lineplot->SetLegend("# (High < Avg Low)");
$lineplot->SetFillColor("blue");
//$lineplot->SetWidth(1);
//$lineplot->SetStepStyle();
$lineplot->value->Show();
$lineplot->value->SetFont(FF_ARIAL,FS_BOLD,10);
$lineplot->value->SetColor("black");
$lineplot->value->SetFormat('%.2f');

$graph->Add($lineplot);


// Display the graph
$graph->Stroke();
?>
