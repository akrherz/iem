<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$dbconn = iemdb("access");
$asosdb = iemdb("asos");

$times1 = Array();
$dwpf1 = Array();
$times2 = Array();
$phour2 = Array();

$rs = pg_query($dbconn, "SELECT phour, station, valid from hourly_2010 WHERE
network = 'IA_ASOS' and station in ('AMW') and
valid >= '2010-08-01' ORDER by valid ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $phour2[] = $row["phour"];
  $times2[] = strtotime($row["valid"]);
}

$rs = pg_query($asosdb, "SELECT dwpf, valid from t2010 WHERE
station = 'AMW' and valid >= '2010-08-01' and dwpf > 0 ORDER by valid ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $dwpf1[] = $row["dwpf"];
  $times1[] = strtotime($row["valid"]);
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");

$graph = new Graph(320,280,"example1");
$graph->SetScale("datlin");
$graph->SetY2Scale("lin");
$graph->SetFrame(false);
$graph->SetBox(true);
$graph->img->SetMargin(40,40,20,30);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
//$graph->xaxis->SetTickLabels($hours);
//$graph->xaxis->SetTextTickInterval(6);
//$graph->xaxis->HideTicks();
//$graph->xaxis->SetTitleMargin(15);
//$graph->yaxis->SetTitleMargin(18);

//$graph->yaxis->SetColor('blue');
//$graph->yaxis->title->SetColor('blue');

$graph->xaxis->title->SetFont(FF_ARIAL,FS_NORMAL,10);
$graph->yaxis->title->SetFont(FF_ARIAL,FS_NORMAL,10);
$graph->xaxis->SetTitle("1  - 29 August 2010");
$graph->yaxis->SetTitle("Dew Point [F]");
$graph->y2axis->SetTitle("Precipitation [inch]");
//$graph->tabtitle->Set('Ames (1893-2009)');
$graph->title->Set("Ames Dew Point \n Hourly Precipitation");
//$graph->subtitle->Set("number of severe t'storm and tornado \ncounty based warnings");

  $graph->title->SetFont(FF_ARIAL,FS_NORMAL,12);
  $graph->subtitle->SetFont(FF_ARIAL,FS_NORMAL,10);
  $graph->SetColor('wheat');

//  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.0,0.65, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();

$lineplot=new LinePlot($dwpf1, $times1);
//$lineplot->SetLegend("Ames [Rock Star Late]");
$lineplot->SetColor("red");
$lineplot->SetWeight(3);
$graph->Add($lineplot);

$bp = new BarPlot($phour2, $times2);
$graph->AddY2($bp);

$graph->Stroke();
?>
