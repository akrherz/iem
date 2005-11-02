<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
// 19 Nov 2002:  Darren requested a bigger image!
// 27 Nov 2002:  Get rid of status indicators
//  3 Jul 2003	We are going to support historical requests as well here
//		lets not support reg_globals anymore

/** We need these vars to make this work */
$subc = isset($_GET["subc"]) ? $_GET["subc"] : "";
$dwpf = isset($_GET["dwpf"]) ? $_GET["dwpf"] : "";
$tmpf = isset($_GET["tmpf"]) ? $_GET["tmpf"] : "";
$s0 = isset($_GET["s0"]) ? $_GET["s0"]: "";
$s1 = isset($_GET["s1"]) ? $_GET["s1"]: "";
$s2 = isset($_GET["s2"]) ? $_GET["s2"]: "";
$s3 = isset($_GET["s3"]) ? $_GET["s3"]: "";
$syear = isset($_GET["syear"]) ? $_GET["syear"] : date("Y");
$smonth = isset($_GET["smonth"]) ? $_GET["smonth"]: date("m");
$sday = isset($_GET["sday"]) ? $_GET["sday"] : date("d");
$days = isset($_GET["days"]) ? $_GET["days"]: 2;
  $station = isset($_GET['station']) ? $_GET["station"] : "";
  $mode = isset($_GET["mode"]) ? $_GET["mode"]: "rt";

/** Lets assemble a time period if this plot is historical */
if (strlen($days) > 0) {
  $sts = mktime(0,0,0, $smonth, $sday, $syear);
  $dbDateString = "'". strftime('%Y-%m-%d', $sts) ."'";
  $plotTitle = strftime('%a %d %b %Y', $sts) ."\n";
  for ($i=1; $i <= intval($days); $i++){
    $tts = $sts + ($i * 86400);
    $dbDateString .= ",'". strftime('%Y-%m-%d', $tts) ."'";
    $plotTitle .= strftime('%a %d %b %Y', $tts) ."\n";
  }
}

$tableName = "rwis_sf";
$dbName = "iowa";
//$station = 'RAME';

$c1 = iemdb('rwis2');

$val = "> -50";
if (isset($_GET["limit"])) $val = "between 25 and 35";

if ($mode == "rt"){
 //$c0 = pg_connect("10.10.10.10","5432", 'iowa');
 $c0 = iemdb('access');
 $q0 = "SELECT
    valid, gvalid, max(tmpf) as tmpf,
    max(dwpf) as dwpf, max(tcs0) as tcs0, max(tcs1) as tcs1,
    max(tcs2) as tcs2, max(tcs3) as tcs3, max(subc) as subc
 FROM
  (SELECT
  to_char(valid, 'mm/dd HH PM') as valid,
  newd || ':' || (case
              when minute > 39 THEN '40'::text
              WHEN minute > 19 THEN '20'::text
              ELSE '00'::text END)::text as gvalid,
  CASE WHEN tmpf ". $val ." THEN tmpf ELSE NULL END as tmpf,
  CASE WHEN dwpf ". $val ." THEN dwpf ELSE NULL END as dwpf,
  CASE WHEN tsf0 ". $val ." THEN tsf0 ELSE NULL END as tcs0,
  CASE WHEN tsf1 ". $val ." THEN tsf1 ELSE NULL END as tcs1,
  CASE WHEN tsf2 ". $val ." THEN tsf2 ELSE NULL END as tcs2,
  CASE WHEN tsf3 ". $val ." THEN tsf3 ELSE NULL END as tcs3,
  CASE WHEN rwis_subf ". $val ." THEN rwis_subf ELSE NULL END as subc
 FROM
   (SELECT
      *,
      to_char(valid, 'YYYY-MM-DD HH24') as newd,
      extract(minute from valid) as minute
    FROM
      current_log
    WHERE
      station = '$station' 
    ORDER by valid ASC) as foo)  as bar
 GROUP by valid, gvalid ORDER by gvalid ASC";
 $minInterval = 20;
} else {
 $c0 = iemdb('rwis');
 $tableName = "t". $syear;
 $q0 = "SELECT
    valid, gvalid, max(tmpf) as tmpf, 
    max(dwpf) as dwpf, max(tcs0) as tcs0, max(tcs1) as tcs1,
    max(tcs2) as tcs2, max(tcs3) as tcs3, max(subc) as subc
 FROM
  (SELECT 
  to_char(valid, 'mm/dd HH PM') as valid,
  newd || ':' || (case 
              when minute > 39 THEN '40'::text
              WHEN minute > 19 THEN '20'::text 
              ELSE '00'::text END)::text as gvalid, 
  CASE WHEN tmpf ". $val ." THEN tmpf ELSE NULL END as tmpf,
  CASE WHEN dwpf ". $val ." THEN dwpf ELSE NULL END as dwpf,
  CASE WHEN tfs0 ". $val ." THEN tfs0 ELSE NULL END as tcs0,
  CASE WHEN tfs1 ". $val ." THEN tfs1 ELSE NULL END as tcs1,
  CASE WHEN tfs2 ". $val ." THEN tfs2 ELSE NULL END as tcs2,
  CASE WHEN tfs3 ". $val ." THEN tfs3 ELSE NULL END as tcs3,
  CASE WHEN subf ". $val ." THEN subf ELSE NULL END as subc
 FROM 
   (SELECT 
      *, 
      to_char(valid, 'YYYY-MM-DD HH24') as newd, 
      extract(minute from valid) as minute 
    FROM 
      $tableName 
    WHERE 
      station = '$station' and 
      local_date(valid) IN ($dbDateString) 
    ORDER by valid ASC) as foo)  as bar 
 GROUP by valid, gvalid ORDER by gvalid ASC";
 $minInterval = 20;
}

$q1 = "SELECT * from sensors WHERE station = '". $station ."' ";

$result = pg_exec($c0, $q0);
$r1 = pg_exec($c1, $q1);

$row = @pg_fetch_array($r1, 0);
$ns0 = $row['sensor0'];
$ns1 = $row['sensor1'];
$ns2 = $row['sensor2'];
$ns3 = $row['sensor3'];

$tcs0 = array();
$tcs1 = array();
$tcs2 = array();
$tcs3 = array();
$Asubc = array();
$Atmpf = array();
$Adwpf = array();
$freezing = array();
$xlabel= array();


$shouldbe = 0;
$timestep = $minInterval * 60; # 20 minutes

$ai = 0;
$missing = 0;
for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ts = strtotime( substr($row["gvalid"],0,16) );

  if ($shouldbe == 0){
    $shouldbe = $ts;
  }
#  echo $row["valid"] ." || ". $ts ." || ". $shouldbe ."<br>";
  if ($shouldbe == $ts) {  // Good!!!
    $tcs0[$ai] = $row["tcs0"];
    $tcs1[$ai] = $row["tcs1"];
    $tcs2[$ai] = $row["tcs2"];
    $tcs3[$ai] = $row["tcs3"];
    $Asubc[$ai] = $row["subc"];
    $Atmpf[$ai] = $row["tmpf"];
    $Adwpf[$ai] = $row["dwpf"];
    $xlabel[$ai] = $row["valid"];
    $freezing[$ai] = 32; 
    $ai++;
    $shouldbe = $shouldbe + $timestep;
 } else if ($shouldbe < $ts) { // Observation is missing
    while ($shouldbe < $ts) {
      $shouldbe = $shouldbe + $timestep;
#      echo "== ". $row["valid"] ." || ". $ts ." || ". $shouldbe ."<br>";
      $tcs0[$ai] = "";
      $tcs1[$ai] = "";
      $tcs2[$ai] = "";
      $tcs3[$ai] = "";
      $Asubc[$ai] = "";
      $Atmpf[$ai] = "";
      $Adwpf[$ai] = "";
      $xlabel[$ai] = strftime("%m/%d %I %p", $shouldbe);
      $freezing[$ai] = 32; 
      $ai++;
      $missing++;
    }
    $tcs0[$ai] = $row["tcs0"];
    $tcs1[$ai] = $row["tcs1"];
    $tcs2[$ai] = $row["tcs2"];
    $tcs3[$ai] = $row["tcs3"];
    $Asubc[$ai] = $row["subc"];
    $Atmpf[$ai] = $row["tmpf"];
    $Adwpf[$ai] = $row["dwpf"];
    $xlabel[$ai] = $row["valid"];
    $freezing[$ai] = 32; 
    $ai++;
    $shouldbe = $shouldbe + $timestep;
  } else if ($shouldbe > $ts) { // Duplicate Ob!
    $i++;
  } 
}

pg_close($c0);
pg_close($c1);


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");

include ("$rootpath/include/rwisLoc.php");

// Create the graph. These two calls are always required
$graph = new Graph(650,550,"example1");
$graph->SetScale("textlin");
if (isset($limit))  $graph->SetScale("textlin", 25, 35);
$graph->img->SetMargin(40,10,105,90);
//$graph->xaxis->SetFont(FS_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);

$interval = intval( sizeof($xlabel) / 48 );
if ($interval > 1 ){
  $graph->xaxis->SetTextLabelInterval(2);
  $graph->xaxis->SetTextTickInterval($interval);
}
$graph->xaxis->SetLabelAngle(90);

//$graph->title->Set("Recent Meteogram for ". $station);
//$graph->title->SetFont(FF_FONT1,FS_BOLD,16);

$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Local Valid Time");
$graph->xaxis->SetTitleMargin(60);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

$graph->legend->Pos(0.01, 0.01);
$graph->legend->SetLayout(LEGEND_VERT);

// Create the linear plot
$lineplot=new LinePlot($tcs0);
$lineplot->SetLegend("0: ".$ns0);
$lineplot->SetColor("blue");
$lineplot->SetWeight(3);

// Create the linear plot
$lineplot2=new LinePlot($tcs1);
$lineplot2->SetLegend("1: ".$ns1);
$lineplot2->SetColor("pink");
$lineplot2->SetWeight(3);

// Create the linear plot
$lineplot3=new LinePlot($tcs2);
$lineplot3->SetLegend("2: ".$ns2);
$lineplot3->SetColor("gray");
$lineplot3->SetWeight(3);

// Create the linear plot
$lineplot4=new LinePlot($tcs3);
$lineplot4->SetLegend("3: ".$ns3);
$lineplot4->SetColor("purple");
$lineplot4->SetWeight(3);

// Create the linear plot
$lineplot5=new LinePlot($Asubc);
$lineplot5->SetLegend("Sub Surface");
$lineplot5->SetColor("black");
$lineplot5->SetWeight(3);

// Create the linear plot
$lineplot6=new LinePlot($Atmpf);
$lineplot6->SetLegend("Air Temperature");
$lineplot6->SetColor("red");
$lineplot6->SetWeight(3);

// Create the linear plot
$lineplot7=new LinePlot($Adwpf);
$lineplot7->SetLegend("Dew Point");
$lineplot7->SetColor("green");
$lineplot7->SetWeight(3);


// Create the linear plot
$fz=new LinePlot($freezing);
$fz->SetColor("blue");

// Title Box
$tx1 = new Text($Rcities[$station]['city'] ." \nMeteogram ");
$tx1->Pos(0.01,0.01, 'left', 'top');
$tx1->SetFont(FF_FONT1, FS_BOLD, 16);

$tx2 = new Text("Time series showing temperatures
   from the pavement sensors and 
   the sub-surface sensor ");
$tx2->Pos(0.01,0.11, 'left', 'top');
$tx2->SetFont(FF_FONT1, FS_NORMAL, 10);

include ("$rootpath/include/mlib.php");
/*
include ("$rootpath/include/currentSFOb.php");
$mySOb = currentSFOb($station);
include ("$rootpath/include/currentOb.php");
$myOb = currentOb($station);
*/
$mySOb = Array();


if ($mode == "hist"){
 $ptext = "Historical Plot for dates:\n";
 $tx3 = new Text($ptext . $plotTitle);
} else {
/*
 $tx3 = new Text("Last Ob @ ". strftime("%m/%d %I:%M %p", $mySOb['ts']) ." 
  Sensor 0: ". $mySOb['tmpf0'] ." F 
  Sensor 1: ". $mySOb['tmpf1'] ." F 
  Sensor 2: ". $mySOb['tmpf2'] ." F 
  Sensor 3: ". $mySOb['tmpf3'] ." F 
 Air  Temp: ". $myOb['tmpf'] ." F
 Dew Point: ". $myOb['dwpf'] ." F
 SubS Temp: ". $mySOb['subt'] ." F
");
*/
}
//$tx3->Pos(0.31,0.001, 'left', 'top');
//$tx3->SetFont(FF_FONT1, FS_NORMAL, 8);
//$tx3->SetColor("blue");

$graph->AddText($tx1);
$graph->AddText($tx2);
//$graph->AddText($tx3);

// Add the plot to the graph
$graph->Add($fz);
if (max($tcs0) != "" && isset($_GET["s0"]) )
  $graph->Add($lineplot);
if (max($tcs1) != "" && isset($_GET["s1"]) )
  $graph->Add($lineplot2);
if (max($tcs2) != "" && isset($_GET["s2"]) )
  $graph->Add($lineplot3);
if (max($tcs3) != "" && isset($_GET["s3"]) )
  $graph->Add($lineplot4);
if (max($Asubc) != "" && isset($_GET["subc"]) )
  $graph->Add($lineplot5);
if (max($Atmpf) != "" && isset($_GET["tmpf"]) )
  $graph->Add($lineplot6);
if (max($Adwpf) != "" && isset($_GET["dwpf"]) )
  $graph->Add($lineplot7);


// Display the graph
$graph->Stroke();
?>

