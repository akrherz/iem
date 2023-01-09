<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/forms.php";

/** We need these vars to make this work */
$subc = isset($_GET["subc"]) ? $_GET["subc"] : "";
$dwpf = isset($_GET["dwpf"]) ? $_GET["dwpf"] : "";
$tmpf = isset($_GET["tmpf"]) ? $_GET["tmpf"] : "";
$pcpn = isset($_GET["pcpn"]) ? $_GET["pcpn"] : "";
$s0 = isset($_GET["s0"]) ? $_GET["s0"]: "";
$s1 = isset($_GET["s1"]) ? $_GET["s1"]: "";
$s2 = isset($_GET["s2"]) ? $_GET["s2"]: "";
$s3 = isset($_GET["s3"]) ? $_GET["s3"]: "";
$syear = get_int404("syear", date("Y"));
$smonth = get_int404("smonth", date("m"));
$sday = get_int404("sday", date("d"));
$days = get_int404("days", 2);
$station = isset($_GET['station']) ? xssafe($_GET["station"]) : "";
$mode = isset($_GET["mode"]) ? xssafe($_GET["mode"]): "rt";

/** Lets assemble a time period if this plot is historical */
if (strlen($days) > 0) {
  $sts = mktime(0,0,0, $smonth, $sday, $syear);
  $dbDateString = "'". date('Y-m-d', $sts) ."'";
  $plotTitle = date('d M Y', $sts) ."\n";
  for ($i=1; $i < intval($days); $i++){
    $tts = $sts + ($i * 86400);
    $dbDateString .= ",'". date('Y-m-d', $tts) ."'";
    $plotTitle .= date('d M Y', $tts) ."\n";
  }
}

$dbName = "iowa";
//$station = 'RAME';


$val = "> -50";
if (isset($_GET["limit"])) $val = "between 25 and 35";

if ($mode == "rt"){
 $c1 = iemdb('rwis');
 $c0 = iemdb("iem");
 $q0 = "SELECT
    valid, gvalid, max(tmpf) as tmpf, max(pday) as pcpn,
    max(dwpf) as dwpf, max(tcs0) as tcs0, max(tcs1) as tcs1,
    max(tcs2) as tcs2, max(tcs3) as tcs3, max(subc) as subc
 FROM
  (SELECT
  to_char(valid, 'mm/dd HH PM') as valid,
  newd || ':' || (case
              when minute > 39 THEN '40'::text
              WHEN minute > 19 THEN '20'::text
              ELSE '00'::text END)::text as gvalid, pday,
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
      current_log c JOIN stations s on (s.iemid = c.iemid)
    WHERE
      s.id = '$station' 
    ORDER by valid ASC) as foo)  as bar
 GROUP by valid, gvalid ORDER by gvalid ASC";
 $minInterval = 20;
} else {
 $c0 = iemdb('rwis');
 $c1 = $c0;
 $q0 = "SELECT
    valid, gvalid, max(tmpf) as tmpf, max(pcpn) as pcpn,
    max(dwpf) as dwpf, max(tcs0) as tcs0, max(tcs1) as tcs1,
    max(tcs2) as tcs2, max(tcs3) as tcs3, max(subc) as subc
 FROM
  (SELECT 
  to_char(valid, 'mm/dd HH PM') as valid,
  newd || ':' || (case 
              when minute > 39 THEN '40'::text
              WHEN minute > 19 THEN '20'::text 
              ELSE '00'::text END)::text as gvalid, pcpn,
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
      alldata
    WHERE 
      station = '$station' and 
      date(valid) IN ($dbDateString) 
    ORDER by valid ASC) as foo)  as bar 
 GROUP by valid, gvalid ORDER by gvalid ASC";
 $minInterval = 20;
}

$q1 = "SELECT * from sensors WHERE station = '". $station ."' ";

//echo $q0;
$result = pg_exec($c0, $q0);
$r1 = pg_exec($c1, $q1);

$row = pg_fetch_array($r1);
$ns0 = $row['sensor0'];
$ns1 = $row['sensor1'];
$ns2 = $row['sensor2'];
$ns3 = $row['sensor3'];

$tcs0 = array();
$tcs1 = array();
$tcs2 = array();
$tcs3 = array();
$pcpn = array();
$Asubc = array();
$Atmpf = array();
$Adwpf = array();
$freezing = array();
$times= array();

function checker($v){
 if ($v == ""){ return $v;}
 if (floatval($v) > 200){ return '';}
 return $v;
}

$lastp = 0;
for( $i=0; $row = pg_fetch_array($result); $i++) 
{ 
  $times[] = strtotime( substr($row["gvalid"],0,16) );
  $tcs0[] = checker($row["tcs0"]);
  $tcs1[] = checker($row["tcs1"]);
  $tcs2[] = checker($row["tcs2"]);
  $tcs3[] = checker($row["tcs3"]);
  $Asubc[] = checker($row["subc"]);
  $Atmpf[] = checker($row["tmpf"]);
  $Adwpf[] = checker($row["dwpf"]);
  $p = floatval($row["pcpn"]);
  $newp = 0;
  if ($p > $lastp) { $newp = $p - $lastp; }
  if ($p < $lastp && $p > 0) {$newp = $p; }
  $pcpn[] = $newp;
  $lastp = $p;
  $freezing[] = 32; 
}
pg_close($c0);
//pg_close($c1);

require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_bar.php";
require_once "../../../include/jpgraph/jpgraph_date.php";

require_once "../../../include/network.php";
$nt = new NetworkTable("IA_RWIS");
$cities = $nt->table;

// Create the graph. These two calls are always required
$graph = new Graph(650,550,"example1");
$graph->SetScale("datlin");
$graph->SetMarginColor("white");
$graph->SetColor("lightyellow");
if (max($pcpn) != "" && isset($_GET["pcpn"])) $graph->SetY2Scale("lin");
if (isset($limit))  $graph->SetScale("datlin", 25, 35);
$graph->img->SetMargin(40,55,105,105);
//$graph->xaxis->SetFont(FS_FONT1,FS_BOLD);

if (max($pcpn) != "" && isset($_GET["pcpn"])) {
 $graph->y2axis->SetTitle("Precipitation [inch]");
 $graph->y2axis->SetTitleMargin(40);
}

$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);

$graph->xaxis->SetTitle("Time Period: ". date('Y-m-d h:i A', $times[0]) ." thru ". date('Y-m-d h:i A', max($times)) );
$graph->xaxis->SetTitleMargin(67);
$graph->xaxis->title->SetFont(FF_VERA,FS_BOLD,12);
$graph->xaxis->title->SetColor("brown");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M-j h A", true);

$graph->legend->Pos(0.01, 0.01);
$graph->legend->SetLayout(LEGEND_VERT);


// Create the linear plot
$lineplot=new LinePlot($tcs0, $times);
$lineplot->SetLegend("0: ".$ns0);
$lineplot->SetColor("blue");
$lineplot->SetWeight(3);

// Create the linear plot
$lineplot2=new LinePlot($tcs1, $times);
$lineplot2->SetLegend("1: ".$ns1);
$lineplot2->SetColor("pink");
$lineplot2->SetWeight(3);

// Create the linear plot
$lineplot3=new LinePlot($tcs2, $times);
$lineplot3->SetLegend("2: ".$ns2);
$lineplot3->SetColor("gray");
$lineplot3->SetWeight(3);

// Create the linear plot
$lineplot4=new LinePlot($tcs3, $times);
$lineplot4->SetLegend("3: ".$ns3);
$lineplot4->SetColor("purple");
$lineplot4->SetWeight(3);

// Create the linear plot
$lineplot5=new LinePlot($Asubc, $times);
$lineplot5->SetLegend("Sub Surface");
$lineplot5->SetColor("black");
$lineplot5->SetWeight(3);

// Create the linear plot
$lineplot6=new LinePlot($Atmpf, $times);
$lineplot6->SetLegend("Air Temperature");
$lineplot6->SetColor("red");
$lineplot6->SetWeight(3);

// Create the linear plot
$lineplot7=new LinePlot($Adwpf, $times);
$lineplot7->SetLegend("Dew Point");
$lineplot7->SetColor("green");
$lineplot7->SetWeight(3);

$bp1=new BarPlot($pcpn, $times);
$bp1->SetLegend("Precip");
$bp1->SetFillColor("black");
$bp1->SetAbsWidth(1.0);


// Create the linear plot
$fz=new LinePlot($freezing, $times);
$fz->SetColor("blue");

// Title Box
$tx1 = new Text($cities[$station]['name'] ." \nMeteogram ");
$tx1->SetPos(0.01,0.01, 'left', 'top');
$tx1->SetFont(FF_FONT1, FS_BOLD, 16);

$tx2 = new Text("Time series showing temperatures
   from the pavement sensors and 
   the sub-surface sensor ");
$tx2->SetPos(0.01,0.11, 'left', 'top');
$tx2->SetFont(FF_FONT1, FS_NORMAL, 10);

require_once "../../../include/mlib.php";
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
//$tx3->SetPos(0.31,0.001, 'left', 'top');
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

if (max($pcpn) != "" && isset($_GET["pcpn"]) )
  $graph->AddY2($bp1);


$graph->Stroke();
