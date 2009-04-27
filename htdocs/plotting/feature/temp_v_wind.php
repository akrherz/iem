<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");

$tmpf = Array();
$stmpf = Array();
$drct = Array();
$sdrct = Array();

$f = fopen('/tmp/data.txt', 'w');
$dbconn = iemdb('asos');
$coop = iemdb('coop');

$snowdays = Array();
$rs = pg_query($coop, "SELECT day from alldata WHERE stationid = 'ia2203' and
       snowd > 3");
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $snowdays[ $row['day'] ] = 1;
}

for($year=1991;$year<2009;$year++)
{
  $sql = "SELECT date(valid) as d, tmpf, drct
  from t$year WHERE station = 'DSM' and valid BETWEEN '${year}-01-15' 
  and '${year}-01-25'
  and sknt > 0 and drct >= 0 and tmpf > -40 and extract(hour from valid) = 14";
  $rs = pg_query($dbconn, $sql);

  for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
  {
    if (array_key_exists($row['d'], $snowdays)){
      $stmpf[] = $row["tmpf"];
      $sdrct[] = $row["drct"];
      fwrite($f, sprintf("%s,%s,1\n", $row["tmpf"], $row["drct"]));
    } else {
      $tmpf[] = $row["tmpf"];
      $drct[] = $row["drct"];
      fwrite($f, sprintf("%s,%s,0\n", $row["tmpf"], $row["drct"]));
    }
    //$feel[] = wcht_idx($row['tmpf'], $row["sknt"] * 1.15);
  }
}
fclose($f);

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,480);
$graph->SetScale("lin");
$graph->img->SetMargin(45,10,5,45);

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
//$graph->xaxis->scale->SetAutoMax(5); 
//$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetTitleMargin(10);


$graph->yaxis->SetTitle("Predicted Pollen Competition [%]");
$graph->xaxis->SetTitle("Observed Outcrossing [%]");
//$graph->tabtitle->Set('Recent Comparison');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_VERT);
  $graph->legend->SetPos(0.01,0.01, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$sc1=new ScatterPlot($tmpf, $drct);
$sc1->SetLegend("9.4m R^2=0.003");
$sc1->mark->SetType(MARK_FILLEDCIRCLE);
$sc1->mark->SetFillColor("red");
$graph->Add($sc1);

// Create the linear plot
$sc2=new ScatterPlot($stmpf, $sdrct);
$sc2->SetLegend("9.4m R^2=0.003");
$sc2->mark->SetType(MARK_FILLEDCIRCLE);
$sc2->mark->SetFillColor("blue");
$graph->Add($sc2);



// Display the graph
$graph->Stroke();
?>
