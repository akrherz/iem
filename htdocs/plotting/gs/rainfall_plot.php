<?php
include("../../../config/settings.inc.php");

$station = isset($_GET['station']) ? $_GET['station'] : "DSM";
$year = isset($_GET['year']) ? $_GET['year']: date("Y");
$smonth = isset($_GET['smonth']) ? $_GET['smonth'] : 5;
$emonth = isset($_GET['emonth']) ? $_GET['emonth'] : 10;
$sday = isset($_GET['sday']) ? $_GET['sday'] : 1;
$eday = isset($_GET['eday']) ? $_GET['eday'] : 1;
$sts = mktime(0,0,0,  $smonth, $sday, $year);
$ets = mktime(0,0,0, $emonth, $eday, $year);
$sdate = date("Y-m-d", $sts);
$edate = date("Y-m-d", $ets);
$s2date = date("2000-m-d", $sts);
$e2date = date("2000-m-d", $ets);


$today = time();

include("$rootpath/include/database.inc.php");
include("$rootpath/include/station.php");
$st = new StationData($station);
$st->load_station( $st->table[$station]['climate_site'] );
$cities = $st->table;
$coopdb = iemdb("coop");
$iem = iemdb("access");

$climate_site = $cities[$station]["climate_site"];

$q = "SELECT pday, day from summary_$year
		WHERE station = '$station' and day between '$sdate' and '$edate'
		ORDER by day ASC";
$rs = pg_exec($iem, $q);
$obs = Array();
$aobs = Array();
$atot = 0;
for ($i=0; $row = @pg_fetch_array($rs,$i); $i++)
{
	$p = $row["pday"];
	if ($p < 0) $p = 0;
	$atot += $p;
	$aobs[$i] = $atot;
	$obs[$i] = $p;
}

/* Now we need the climate data */
$q = "SELECT precip, valid from climate
		WHERE station = '". strtolower($climate_site) ."' and valid between '$s2date' and
		'$e2date'
		ORDER by valid ASC";
$rs = pg_exec($coopdb, $q);
$climate = Array();
$cdiff = Array();
$aclimate = Array();
$atot = 0;
$zeros = Array();
$times = Array();
for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) 
{
	$p = $row["precip"];
	$climate[$i] = $p;
	$atot += $p;
	if (@$aobs[$i] > 0) $cdiff[$i] = $aobs[$i] - $atot ;
    else $cdiff[$i] = "";
	$aclimate[$i] = $atot;
	$zeros[$i] = 0;
	$xlabels[$i] = "";
    $times[$i] = strtotime( $row["valid"] );
}

pg_close($coopdb);


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_plotline.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");

// Create the graph. These two calls are always required
$graph = new Graph(640,480,"example1");
$graph->SetScale("datlin");
$graph->img->SetMargin(45,10,80,60);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->yaxis->SetTitleMargin(30);
$graph->xaxis->SetPos("min");
//$graph->xaxis->SetTitle("Day of Month");
//$graph->xaxis->SetTickLabels($xlabels);
$graph->xaxis->SetLabelFormatString("M d", true);
$graph->xaxis->SetLabelAngle(90);


$graph->yaxis->SetTitle("Precipitation (in)");
$graph->title->Set( $cities[$station]["name"] ." [$station] Precipitation for ". $year );
$graph->subtitle->Set("Climate Site: ". $cities[strtoupper($climate_site)]["name"] ."[". $climate_site ."]");
$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.05, 0.1, "right", "top");

reset($times);
while (list($k,$v) = each($times))
{
 if (date("d", $v) == 1)
   $graph->AddLine(new PlotLine(VERTICAL,$v,"tan",1));
}


// Create the linear plot
$lp0 =new LinePlot($cdiff, $times);
$lp0->SetColor("green");
$lp0->SetLegend("Accum Difference");

$b2plot = new BarPlot($obs, $times);
$b2plot->SetFillColor("blue");
$b2plot->SetLegend("Obs Rain");

// Create the linear plot
$lp1=new LinePlot($aobs, $times);
$lp1->SetLegend("Actual Accum");
$lp1->SetColor("blue");
$lp1->SetWeight(3);

$lp2=new LinePlot($aclimate, $times);
$lp2->SetLegend("Climate Accum");
$lp2->SetColor("red");
$lp2->SetWeight(3);

$z = new LinePlot($zeros, $times);
$z->SetWeight(3);

// Add the plot to the graph
$graph->Add($lp0);
$graph->Add($lp1);
$graph->Add($lp2);
$graph->Add($b2plot);
$graph->Add($z);

// Display the graph
$graph->Stroke();
?>
