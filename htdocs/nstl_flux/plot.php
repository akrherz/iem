<?php
putenv("TZ=GMT"); /* Hack around timezone problem */
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
/* We need to get some CGI vars! */
$year = isset($_GET['year']) ? $_GET['year'] : die();
$month = isset($_GET['month']) ? $_GET['month'] : die();
$day = isset($_GET['day']) ? $_GET['day'] : die();
$pvar = isset($_GET['pvar']) ? $_GET['pvar'] : die();
$sts = mktime(0,0,0,$month, $day, $year);

$vars = Array();
$pgconn = iemdb("other");

$sql = "SELECT * from flux_vars ORDER by details ASC";
$rows = pg_exec($pgconn, $sql);
for( $i=0; $row = @pg_fetch_array($rows,$i); $i++)
{
  $vars[ $row["name"] ] = Array("units" => $row["units"], "details" => $row["details"]);
}

$rs = pg_prepare($pgconn, "SELECT", "SELECT * from flux${year} WHERE
      date(valid) = $1 and $pvar IS NOT NULL ORDER by valid ASC");
$rs = pg_prepare($pgconn, "METADATA", "SELECT * from flux_meta WHERE 
      sts < $1 and ets > $1");

$rs = pg_execute($pgconn, "SELECT", Array(date('Y-m-d', $sts)));

$data = Array("nstl11" => Array(),
   "nstl10" => Array(),
   "nstl30ft" => Array(),
   "nstl110" => Array(),
   "nstlnsp" => Array() );
$times = Array("nstl11" => Array(),
   "nstl10" => Array(),
   "nstl30ft" => Array(),
   "nstl110" => Array(),
   "nstlnsp" => Array() );

for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) 
{ 
  $ts = strtotime( substr($row["valid"],0,16) );
  $stid = $row["station"];
  $val = floatval($row[$pvar]);
  if ($val > -90000){
    $data[$stid][] = floatval($row[$pvar]);
    $times[$stid][] = $ts;
  }
}

$labels = Array("nstlnsp" => "Unknown", "nstl11" => "Unknown", 
        "nstl10" => "Unknown", "nstl30ft" => "Unknown", "nstl110" => "Unknown");
$rs = pg_execute($pgconn, "METADATA", Array(date('Y-m-d', $sts)));
for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
{
  $st = $row["station"];
  $labels[$st] =  $row["surface"];
}

$ts_lbl = date("d M Y", $sts);

pg_close($pgconn);

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");

// Create the graph. These two calls are always required
$graph = new Graph(640,350);
$graph->SetScale("datlin");
$graph->img->SetMargin(65,8,45,70);
$graph->SetMarginColor('white');
// Box around plotarea
$graph->SetBox();

// Setup the X and Y grid
$graph->ygrid->SetFill(true,'#DDDDDD@0.5','#BBBBBB@0.5');
$graph->ygrid->SetLineStyle('dashed');
$graph->ygrid->SetColor('gray');
$graph->xgrid->Show();
$graph->xgrid->SetLineStyle('dashed');
$graph->xgrid->SetColor('gray');

$graph->xaxis->SetFont(FF_FONT1, FS_NORMAL);
$graph->xaxis->title->SetFont(FF_GEORGIA,FS_BOLD,12);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetPos("min");
$graph->xaxis->SetLabelFormatString("h A", true);
$graph->xaxis->SetTitleMargin(35);

$graph->tabtitle->Set($vars[$pvar]["details"]);
$graph->tabtitle->SetFont(FF_GEORGIA,FS_BOLD,14);

$graph->yaxis->title->SetFont(FF_GEORGIA,FS_BOLD,10);
$graph->xaxis->SetTitle("Timeseries for ${ts_lbl}");
$graph->yaxis->SetTitle($vars[$pvar]["details"] ." [". $vars[$pvar]["units"] ."]");
$graph->yaxis->SetTitleMargin(45);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.10, 0.92, "left", "top");

// Create the linear plot
if (sizeof($data["nstl11"]) > 1) {
 $lineplot=new LinePlot($data["nstl11"], $times["nstl11"]);
 $lineplot->SetColor("red");
 $lineplot->SetLegend( $labels["nstl11"] );
 $lineplot->SetWeight(2);
 $graph->Add($lineplot);
}

if (sizeof($data["nstl10"]) > 1) {
 $lineplot2=new LinePlot($data["nstl10"], $times["nstl10"]);
 $lineplot2->SetColor("blue");
 $lineplot2->SetLegend( $labels["nstl10"] );
 $lineplot2->SetWeight(2);
 $graph->Add($lineplot2);
}

// Create the linear plot
if (sizeof($data["nstlnsp"]) > 1) {
 $lineplot3=new LinePlot($data["nstlnsp"], $times["nstlnsp"]);
 $lineplot3->SetColor("black");
 $lineplot3->SetLegend( $labels["nspr"] );
 $lineplot3->SetWeight(2);
 $graph->Add($lineplot3);
}

// Create the linear plot
if (sizeof($data["nstl30ft"]) > 1) {
 $lineplot4=new LinePlot($data["nstl30ft"], $times["nstl30ft"]);
 $lineplot4->SetColor("green");
 $lineplot4->SetLegend( $labels["nstl30ft"] );
 $lineplot4->SetWeight(2);
 $graph->Add($lineplot4);
}

// Create the linear plot
if (sizeof($data["nstl110"]) > 1) {
 $lineplot5=new LinePlot($data["nstl110"], $times["nstl110"]);
 $lineplot5->SetColor("yellow");
 $lineplot5->SetLegend( $labels["nstl110"] );
 $lineplot5->SetWeight(2);
 $graph->Add($lineplot5);
}


// Display the graph
$graph->Stroke();
?>
