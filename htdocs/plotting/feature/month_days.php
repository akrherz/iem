<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$coop = iemdb('coop');
$iem = iemdb('access');

$climate = Array();

$rs = pg_query($coop, "SELECT high from climate WHERE station = 'ia0200' and valid != '2000-02-29' ORDER by valid ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $climate[] = $row["high"];
}

$month = Array(0,0,0,0,0,0,0,0,0);

$rs = pg_query($iem, "SELECT extract(month from day) as m, max_tmpf from summary WHERE station = 'AMW' ORDER by day ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  if ($row["max_tmpf"] > $climate[$i]){
    $month[ intval($row["m"]) - 1 ] += 1;
  } 
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,300,"example1");
$graph->SetScale("textlin");

$graph->SetBackgroundGradient('white','green',GRAD_HOR,BGRAD_PLOT);
$graph->SetMarginColor('white');
//$graph->SetColor('white');
//$graph->SetBackgroundGradient('navy','white',GRAD_HOR,BGRAD_MARGIN);
$graph->SetFrame(true,'white');

$graph->ygrid->Show();
$graph->xgrid->Show();
$graph->ygrid->SetColor('gray@0.5');
$graph->xgrid->SetColor('gray@0.5');

$graph->img->SetMargin(40,10,25,80);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTickLabels( Array("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP") );
//$graph->xaxis->SetTextTickInterval(10);
//$graph->xaxis->SetTitleMargin(70);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,14);
$graph->xaxis->SetTitle("* thru September 18th");
$graph->xaxis->title->SetMargin(20);
$graph->yaxis->SetTitle("Days");
$graph->title->Set('2009 Ames Daily High Temp Above Average');
$graph->title->SetFont(FF_ARIAL,FS_BOLD,10);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->SetPos(0.0,0.9, 'right', 'top');
//$graph->legend->SetLineSpacing(3);



// Create the linear plot
$lineplot=new BarPlot( $month );
//$lineplot->SetLegend("# (High < Avg Low)");
$lineplot->SetFillColor("blue");
$lineplot->value->Show();
$lineplot->value->SetFont(FF_ARIAL,FS_BOLD,10);
$lineplot->value->SetFormat('%.0f');
//$lineplot->SetWidth(1);
$graph->Add($lineplot);

// Display the graph
$graph->Stroke();
?>
