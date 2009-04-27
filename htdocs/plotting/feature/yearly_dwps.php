<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");

$t2008 = Array();
$t2009 = Array();
$d2008 = Array();
$d2009 = Array();

$dbconn = iemdb('asos');
$sql = "SELECT extract(doy from valid) as d, avg(dwpf) as dew
  from t2008 WHERE station = 'DSM' and dwpf > -99 and
  valid BETWEEN '2008-03-01' and '2008-05-01'
  GROUP by d ORDER by d ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $t2008[] = mktime(12,0,0,1,1,2000) + (intval($row["d"]) * 86400);
  $d2008[] = $row["dew"];
}
$sql = "SELECT extract(doy from valid) as d, avg(dwpf) as dew
  from t2009 WHERE station = 'DSM' and dwpf > -99 
  and valid BETWEEN '2009-03-01' and '2009-05-01'
  GROUP by d ORDER by d ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $t2009[] = mktime(12,0,0,1,1,2000) + (intval($row["d"]) * 86400);
  $d2009[] = $row["dew"];
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(620,600,"example1");
$graph->SetScale("datlin");
//$graph->SetY2Scale("lin");
$graph->img->SetMargin(40,5,50,85);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("Md h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

//$graph->y2axis->SetTitleMargin(20);
//$graph->y2axis->SetColor("blue");
//$graph->y2axis->title->SetColor("blue");
//$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->y2axis->SetTitle("Visibility [mile]");

$graph->xaxis->SetTitleMargin(70);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->SetTitle("Valid Local Time");
//$graph->yaxis->SetTitle("Temp [F] or Wind [MPH]");
$graph->yaxis->SetTitle("Temp [F]");
//$graph->tabtitle->Set('Recent Comparison');
$graph->title->Set('Waterloo [KALO] Time Series');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.01,0.07, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new LinePlot($d2009, $t2009);
$lineplot->SetLegend("2009");
$lineplot->SetColor("blue");
$graph->Add($lineplot);

// Create the linear plot
$lineplot2=new LinePlot($d2008,$t2008);
$lineplot2->SetLegend("2008");
$lineplot2->SetColor("red");
$graph->Add($lineplot2);

$graph->AddLine(new PlotLine(HORIZONTAL,32,"blue",2));

// Display the graph
$graph->Stroke();
?>
