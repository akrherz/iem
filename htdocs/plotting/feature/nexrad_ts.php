<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$dbconn = iemdb('access');
include("$rootpath/include/mlib.php");

$rs = pg_query($dbconn, "SELECT valid, sknt, gust from current_log 
      WHERE station = 'AIO' and 
      valid BETWEEN '2010-05-03 17:00' and '2010-05-03 19:00' 
      ORDER by valid ASC");
$tmpf = Array();
$gust = Array();
$times = Array();
for ($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $tmpf[] = $row["sknt"] * 1.15;
  $gust[] = $row["gust"] * 1.15;
  $times[] = strtotime( $row["valid"] );
}

$radtimes = Array();
$n0r = Array();
$fc = file('ames.txt');
while (list ($line_num, $line) = each ($fc)) {
  $tokens = split (" ", $line);
  $radtimes[] = strtotime( $tokens[0] ." ". $tokens[1] ) - (5*3600);
  //if ( floatval($tokens[3]) > 0){
    $n0r[] = floatval($tokens[3]);
  //} else {
  //  $n0r[] = "";
  //}
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,280,"example1");
$graph->SetScale("datlin",0,60);
$graph->SetY2Scale("lin", 0, 40);
$graph->img->SetMargin(47,45,40,70);
$graph->SetColor("white");
$graph->SetMarginColor("white");
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("h:i A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

$graph->yaxis->SetColor("red");
$graph->yaxis->title->SetColor("red");
$graph->y2axis->SetColor("blue");
$graph->y2axis->title->SetColor("blue");
$graph->xaxis->SetTitleMargin(40);
$graph->yaxis->SetTitleMargin(32);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->SetTitle("Afternoon of 3 May 2010");
$graph->y2axis->SetTitle("NEXRAD Base Reflect. [dBZ]");
$graph->yaxis->SetTitle("Wind Speed [mph]");
$graph->title->Set("Altantic Iowa (KAIO) Timeseries");

//  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.2,0.08, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();

$l = new LinePlot($tmpf, $times);
$l->SetColor("red");
$l->SetLegend("Wind Speed");
$graph->Add($l);

$sp = new ScatterPlot($gust, $times);
$sp->mark->SetColor("red");
$sp->mark->SetFillColor("red");
$sp->SetLegend("Wind Gust");
$graph->Add($sp);

// Create the linear plot
$lineplot2=new LinePlot($n0r,$radtimes);
//$lineplot2->SetLegend("NEXRAD");
$lineplot2->SetFillColor("blue");
$lineplot2->SetWeight(3);
$lineplot2->SetStepStyle();
$graph->AddY2($lineplot2);


// Display the graph
$graph->Stroke();
?>
