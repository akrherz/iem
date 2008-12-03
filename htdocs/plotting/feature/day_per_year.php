<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");

$dbconn = iemdb('asos');

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(800,600,"example1");
$graph->SetScale("datlin");
$graph->img->SetMargin(80,5,5,105);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetTitleMargin(40);


$graph->xaxis->SetTitle("Local Time on each December 1");
$graph->yaxis->SetTitle("Des Moines Temperature [F]");
//$graph->tabtitle->Set('Recent Comparison');

$graph->xaxis->SetFont(FF_FONT2,FS_BOLD,32);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,32);
$graph->yaxis->SetFont(FF_FONT2,FS_BOLD,32);
$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,32);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.15,0.01, 'left', 'top');
  $graph->legend->SetFont(FF_FONT2,FS_BOLD,32);
  $graph-> legend-> SetColumns(2);
  $graph->legend->SetLineWeight(2);
  $graph->legend->SetVColMargin(2);
  $graph->legend->SetHColMargin(2);
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();

$colors = Array(
 2000 => "tan",
 2001 => "yellow",
 2002 => "sienna1",
 2003 => "steelblue1",
 2004 => "tomato4",
 2005 => "violet",
 2006 => "springgreen4",
 2007 => "red",
 2008 => "black"
);

for($year=2000;$year<2009;$year++)
{
  $sql = "SELECT extract(EPOCH from (valid + '". (2008-$year) ." years'::interval)) as epoch, tmpf, dwpf, sknt
  from t$year WHERE station = 'DSM' and date(valid) = '${year}-12-01' and dwpf > -99 ORDER by valid ASC";
  $rs = pg_query($dbconn, $sql);

  $times = Array();
  $tmpf = Array();
  for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
  {
    $times[] = $row["epoch"];
    $tmpf[] = $row["tmpf"];
    //$dwpf[] = $row["dwpf"];
    //$feel[] = wcht_idx($row['tmpf'], $row["sknt"] * 1.15);
  }

  // Create the linear plot
  $lineplot=new LinePlot($tmpf, $times);
  $lineplot->SetLegend($year);
  $lineplot->SetColor($colors[$year]);
  $lineplot->SetWeight(4);

  $graph->Add($lineplot);
}

// Display the graph
$graph->Stroke();
?>
