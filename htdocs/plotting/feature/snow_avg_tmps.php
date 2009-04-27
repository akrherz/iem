<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");



$dbconn = iemdb('coop');
$times = Array("snow"=> Array(), "no"=> Array(), "avg" => Array() );
$hdata = Array("snow"=> Array(), "no"=> Array(), "avg" => Array() );
$ldata = Array("snow"=> Array(), "no"=> Array(), "avg" => Array() );

$sql = "SELECT sday, 
  (case when snowd > 0 THEN 'snow' ELSE 'no' END) as s, 
  avg(high) as ahigh, avg(low) as alow,
  count(*) as all from alldata WHERE sday != '0229' and year > 1963 and stationid = 'ia0200' and month > 10 GROUP by sday, s ORDER by sday, s ASC";
$rs = pg_query($dbconn, $sql);

for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $s = $row["s"];
  if ($s == "snow" and $row["all"] < 5) continue;
  $times[$s][] = strtotime("2000-". substr($row["sday"],0,2) ."-". substr($row["sday"],2,2) );
  $hdata[$s][] = $row["ahigh"];
  $ldata[$s][] = $row["alow"];
}

$sql = "SELECT sday, 
  (case when snowd > 0 THEN 'snow' ELSE 'no' END) as s, 
  avg(high) as ahigh, avg(low) as alow,
  count(*) as all from alldata WHERE sday != '0229' and year > 1963 and stationid = 'ia0200' and month < 4 GROUP by sday, s ORDER by sday, s ASC";
$rs = pg_query($dbconn, $sql);

for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $s = $row["s"];
  if ($s == "snow" and $row["all"] < 5) continue;
  $times[$s][] = strtotime("2001-". substr($row["sday"],0,2) ."-". substr($row["sday"],2,2) );
  $hdata[$s][] = $row["ahigh"];
  $ldata[$s][] = $row["alow"];
}


$sql = "SELECT sday, 
  avg(high) as ahigh, avg(low) as alow,
  count(*) as all from alldata WHERE sday != '0229' and year > 1963 and stationid = 'ia0200' and month > 10 GROUP by sday ORDER by sday ASC";
$rs = pg_query($dbconn, $sql);

for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $s = "avg";
  if ($s == "snow" and $row["all"] < 5) continue;
  $times[$s][] = strtotime("2000-". substr($row["sday"],0,2) ."-". substr($row["sday"],2,2) );
  $hdata[$s][] = $row["ahigh"];
  $ldata[$s][] = $row["alow"];
}

$sql = "SELECT sday, 
  avg(high) as ahigh, avg(low) as alow,
  count(*) as all from alldata WHERE sday != '0229' and year > 1963 and stationid = 'ia0200' and month < 4 GROUP by sday ORDER by sday ASC";
$rs = pg_query($dbconn, $sql);

for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $s = "avg";
  if ($s == "snow" and $row["all"] < 5) continue;
  $times[$s][] = strtotime("2001-". substr($row["sday"],0,2) ."-". substr($row["sday"],2,2) );
  $hdata[$s][] = $row["ahigh"];
  $ldata[$s][] = $row["alow"];
}



include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,480,"example1");
$graph->SetScale("datlin");
$graph->img->SetMargin(60,5,50,66);

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetTitleMargin(70);

//$graph->title->Set("Frequency of Sub Freezing Days");
//$graph->subtitle->Set('Ames [1893-2008]');

$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("Ames Hi/Lo Temperature [F]");
$graph->xaxis->SetFont(FF_FONT2,FS_BOLD,16);
$graph->yaxis->SetFont(FF_FONT2,FS_BOLD,16);
$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_VERT);
  $graph->legend->SetPos(0.05,0.01, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);
$graph-> legend-> SetColumns(2);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();

function tb($a){
  return date('M d', $a);
  //return '';
}

$graph->xaxis->SetLabelFormatCallback('tb');
//$graph->xaxis-> scale->ticks->Set(86400,86400*31);

reset($times["no"]);
while (list($k,$v) = each($times["no"]))
{
 if (date("d", $v) == 1) {
  // $graph->AddLine(new PlotLine(VERTICAL,$v,"gray",1));
 }
}
 
// Create the linear plot
$lineplot=new LinePlot($hdata["snow"], $times["snow"]);
$lineplot->SetLegend("Snow Highs");
$lineplot->SetColor("darkred");
$lineplot->SetWeight(2);
$graph->Add($lineplot);

$lineplot2=new LinePlot($ldata["snow"], $times["snow"]);
$lineplot2->SetLegend("Snow Lows");
$lineplot2->SetColor("darkblue");
$lineplot2->SetWeight(2);
$graph->Add($lineplot2);

$lineplot3=new LinePlot($hdata["no"], $times["no"]);
$lineplot3->SetLegend("No Snow Highs");
$lineplot3->SetColor("red");
$lineplot3->SetWeight(2);
$graph->Add($lineplot3);

$lineplot4=new LinePlot($ldata["no"], $times["no"]);
$lineplot4->SetLegend("No Snow Lows");
$lineplot4->SetColor("blue");
$lineplot4->SetWeight(2);
$graph->Add($lineplot4);

$lineplot5=new LinePlot($hdata["avg"], $times["avg"]);
$lineplot5->SetLegend("Avg Highs");
$lineplot5->SetColor("lightred");
$lineplot5->SetWeight(2);
$graph->Add($lineplot5);

$lineplot6=new LinePlot($ldata["avg"], $times["avg"]);
$lineplot6->SetLegend("Avg Lows");
$lineplot6->SetColor("lightblue");
$lineplot6->SetWeight(2);
$graph->Add($lineplot6);

// Display the graph
$graph->Stroke();
?>
