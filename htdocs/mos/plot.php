<?php
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");

$ts = strtotime("2009-01-13 00:00");
$runtimes = Array(); $vals = Array(); $times = Array();
$sqlSelector = "(";
for ($i=0;$i<6;$i++)
{
  $runtimes[] = $ts - (43200 * $i);
  $s = date("Y-m-d H:i", $ts - (43200 * $i));
  $sqlSelector .= sprintf("'%s',", $s);
  $vals[$s] = Array();
  $times[$s] = Array();
}
$sqlSelector = substr($sqlSelector,0,-1) . ")";

$dbconn = iemdb('mos');
pg_query($dbconn, "SET TIME ZONE 'GMT'");
$sql = "SELECT * from t2009 WHERE model = 'GFS' and 
    station = 'KEST' and runtime IN $sqlSelector ORDER by runtime, ftime ASC";
//echo $sql;
$rs = pg_query($dbconn, $sql);


for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $runtime = substr($row["runtime"], 0, 16);
  $vals[$runtime][] = $row["wsp"];
  $times[$runtime][] = strtotime(substr($row["ftime"],0,16));
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,300,"example1");
$graph->SetScale("datlin");
$graph->img->SetMargin(40,5,50,100);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d H \Z", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

//$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetTitleMargin(70);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->SetTitle("GMT Time");
$graph->yaxis->SetTitle("Wind Speed [kts]");
//$graph->tabtitle->Set('Recent Comparison');
$graph->title->Set('Esterville [KEST] Time Series');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.2,0.06, 'right', 'top');
$graph-> legend-> SetColumns(2);
//  $graph->legend->SetLineSpacing(3);
  $graph->legend->SetLineWeight(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


$ar = Array();

$colors = Array("black", "red", "lightblue", "darkgreen", "purple", "tan");

while( list($k,$v) = each($runtimes))
{
  $lk = date("Y-m-d H:i", $v);
  if (sizeof($vals[$lk]) == 0) continue;
  $ar[$k]=new LinePlot($vals[$lk], $times[$lk]);
  $ar[$k]->SetLegend(date('M d H', $v) ."Z");
  $ar[$k]->SetColor($colors[$k]);
  $ar[$k]->SetWeight(3);
  $graph->Add($ar[$k]);
}


// Display the graph
$graph->Stroke();
?>
