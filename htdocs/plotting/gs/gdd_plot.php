<?php
 include("../../../config/settings.inc.php");

$station = isset($_GET['station']) ? $_GET['station'] : "DSM";
$year = isset($_GET['year']) ? $_GET['year']: date("Y");
$sts = mktime(0,0,0,  5, 1, $year);
$ets = mktime(0,0,0, 10, 1, $year);
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

function calcGDD($high,$low)
{
	if ($low < 50)  $low = 50.00;
    if ($high > 86) $high = 86.00;
    if ($high < 50) return 0.00;
    return (($high+$low)/2.00) - 50.00;

}

$climate_site = $cities[$station]["climate_site"];

$rs = pg_prepare($iem, "SELECT", "SELECT max_tmpf, min_tmpf, day from summary_$year
		WHERE station = $1 and day between $2 and $3 ORDER by day ASC");
$rs = pg_execute($iem, "SELECT", Array($station, $sdate, $edate));
$obs = Array();
$aobs = Array();
$atot = 0;
for ($i=0; $row = @pg_fetch_array($rs,$i); $i++)
{
	$hi = (float)$row["max_tmpf"];
	$lo = (float)$row["min_tmpf"];
	$gdd = calcGDD($hi, $lo);
	$atot += $gdd;
	$aobs[$i] = $atot;
	$obs[$i] = $gdd;
}

/* Now we need the climate data */
$q = "SELECT gdd50, valid from climate
		WHERE station = '". strtolower($climate_site) ."' and valid between '$s2date' and
		'$e2date'
		ORDER by valid ASC";
$rs = pg_exec($coopdb, $q);
$climate = Array();
$cdiff = Array();
$aclimate = Array();
$atot = 0;
$zeros = Array();
$xlabels = Array();
for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) 
{
	$gdd = (float)$row["gdd50"];
	$atot += $gdd;
	if (@$aobs[$i] > 0)
	{
		$cdiff[$i] = $aobs[$i] - $atot ;
	}
    else $cdiff[$i] = "";
	$aclimate[$i] = $atot;
	$zeros[$i] = 0;
	$xlabels[$i] = "";
}

pg_close($coopdb);

$xlabels[0] = "May 1";
$xlabels[30] = "Jun 1";
$xlabels[61] = "Jul 1";
$xlabels[91] = "Aug 1";
$xlabels[122] = "Sep 1";

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,400,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(45,10,80,30);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->yaxis->SetTitleMargin(30);
$graph->xaxis->SetPos("min");
//$graph->xaxis->SetTitle("Day of Month");
$graph->xaxis->SetTickLabels($xlabels);
$graph->xscale->ticks->SupressTickMarks();

$graph->yaxis->SetTitle("Growing Degree Days");
$graph->title->Set( $cities[$station]["name"] ." [$station] Growing Degree Days (base=50) for $year");
$graph->subtitle->Set("Climate Site: ". $cities[$climate_site]["name"] ."[". $climate_site ."]");
$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.05, 0.1, "right", "top");

$graph->AddLine(new PlotLine(VERTICAL,30,"tan",1));
$graph->AddLine(new PlotLine(VERTICAL,61,"tan",1));
$graph->AddLine(new PlotLine(VERTICAL,91,"tan",1));
$graph->AddLine(new PlotLine(VERTICAL,122,"tan",1));
$graph->AddLine(new PlotLine(VERTICAL,153,"tan",1));


// Create the linear plot
$b1plot =new BarPlot($cdiff);
//$b1plot->SetFillColor("red");
$b1plot->SetLegend("Accum Difference");

// Create the linear plot
$lp1=new LinePlot($aobs);
$lp1->SetLegend("Actual Accum");
$lp1->SetColor("blue");
$lp1->SetWeight(2);

$lp2=new LinePlot($aclimate);
$lp2->SetLegend("Climate Accum");
$lp2->SetColor("red");
$lp2->SetWeight(2);

$z = new LinePlot($zeros);
$z->SetWeight(2);

// Add the plot to the graph
$graph->Add($lp1);
$graph->Add($lp2);
$graph->Add($b1plot);
$graph->Add($z);

// Display the graph
$graph->Stroke();
?>
