<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");



$dbconn = iemdb('coop');
$sql = "SELECT sday, 
  SUM( case when high < 32 THEN 1 ELSE 0 END) as hcount, 
  SUM( case when low < 32 THEN 1 ELSE 0 END) as lcount, 
  count(*) as all from alldata WHERE stationid = 'ia0200' and sday != '0229' GROUP by sday ORDER by sday ASC";
$rs = pg_query($dbconn, $sql);

$times = Array();
$hdata = Array();
$ldata = Array();
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  if (intval(substr($row["sday"],0,2)) < 7){
  $times[] = mktime(6,0,0, substr($row["sday"],0,2), substr($row["sday"],2,2),2009);
  } else {
    $times[] = mktime(6,0,0, substr($row["sday"],0,2), substr($row["sday"],2,2),2008);
  }
  $hdata[] = $row["hcount"] / $row["all"] * 100;
  $ldata[] = $row["lcount"] / $row["all"] * 100;
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,480,"example1");
$graph->SetScale("datlin");
$graph->img->SetMargin(60,5,50,60);

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetTitleMargin(70);

$graph->title->Set("Frequency of Sub Freezing Days");

$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("Observed Frequency [%]");
$graph->xaxis->SetFont(FF_FONT2,FS_BOLD,16);
$graph->yaxis->SetFont(FF_FONT2,FS_BOLD,16);
$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->subtitle->Set('Ames [1893-2008]');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_VERT);
  $graph->legend->SetPos(0.6,0.15, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();

function tb($a){
  return date('M 1', $a);
  //return '';
}

$graph->xaxis->SetLabelFormatCallback('tb');
$graph->xaxis-> scale->ticks->Set(86400,86400*31);

reset($times);
while (list($k,$v) = each($times))
{
 if (date("d", $v) == 1) {
  // $graph->AddLine(new PlotLine(VERTICAL,$v,"gray",1));
 }
}
 
// Create the linear plot
$lineplot=new LinePlot($hdata, $times);
$lineplot->SetLegend("Highs");
$lineplot->SetColor("red");
$graph->Add($lineplot);

$lineplot2=new LinePlot($ldata, $times);
$lineplot2->SetLegend("Lows");
$lineplot2->SetColor("blue");
$graph->Add($lineplot2);



// Display the graph
$graph->Stroke();
?>
