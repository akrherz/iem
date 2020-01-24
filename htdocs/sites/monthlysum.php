<?php 
// Summary of monthly data from IEMAccess
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "setup.php";
require_once "../../include/myview.php";

$month = isset($_GET["month"]) ? intval($_GET["month"]): date("m");
$year = isset($_GET["year"]) ? intval($_GET["year"]): date("Y");

$t = new MyView();
$t->thispage="iem-sites";
$t->title = "Monthly Summaries";
$t->sites_current="monthsum"; 

$pgconn = iemdb("iem");
$rs = pg_prepare($pgconn, "SELECT", "SELECT extract(year from day) as year,".
      "extract(month from day) as month, sum(pday) as precip, ".
      "avg(avg_rh) as avg_rh, avg(max_tmpf) as avg_high, ".
      "avg(min_tmpf) as avg_low, avg((max_tmpf + min_tmpf) / 2.) as avg_temp ".
      "from summary s ".
      "JOIN stations t on (s.iemid = t.iemid) WHERE t.id = $1 and t.network = $2 ".
      "GROUP by year, month ORDER by year, month");
$rs = pg_execute($pgconn, "SELECT", Array($station, $network));
$data = Array();
$minyear = 3000;
$maxyear = 1000;
for ($i=0; $row=pg_fetch_assoc($rs); $i++){
      if ($minyear > $row["year"]) $minyear = $row["year"];
      if ($maxyear < $row["year"]) $maxyear = $row["year"];
      $key = sprintf("%s_%s", $row["year"], $row["month"]);
      $data[$key] = $row;
}
$climo = Array();
$pgconn = iemdb("coop");
$rs = pg_prepare($pgconn, "SELECT", "SELECT ".
"extract(month from valid) as month, avg(high) as avg_high, ".
"avg(low) as avg_low, avg((high+low)/2.) as avg_temp, ".
"sum(precip) as precip from ncdc_climate81 WHERE station = $1".
" GROUP by month ORDER by month ASC");
$rs = pg_execute($pgconn, "SELECT", Array($metadata["ncdc81"]));
for ($i=0; $row=pg_fetch_assoc($rs); $i++){
      $climo[$row["month"]] = $row;
}

function f($data, $key1, $key2, $fmt){
      if (!array_key_exists($key1, $data) ||
          !array_key_exists($key2, $data[$key1])){
                return "M";
          }
      $val = $data[$key1][$key2];
      if ($val === NULL) return "M";
      return sprintf($fmt, $val);
}

function make_table($data, $key, $minyear, $maxyear, $fmt, $climo){
      $table = '<table class="table table-ruled table-condensed table-bordered">'.
      '<thead><tr><th>Year</th><th>Jan</th><th>Feb</th><th>Mar</th>'.
      '<th>Apr</th><th>May</th><th>Jun</th><th>Jul</th><th>Aug</th>'.
      '<th>Sep</th><th>Oct</th><th>Nov</th><th>Dec</th></tr></thead>'.
      '<tbody>';
      for ($year=$minyear; $year <= $maxyear; $year++){
            $table .= @sprintf("<tr><td>%s</td><td>%s</td><td>%s</td>".
            "<td>%s</td><td>%s</td><td>%s</td><td>%s</td>".
            "<td>%s</td><td>%s</td><td>%s</td><td>%s</td>".
            "<td>%s</td><td>%s</td></tr>", $year,
            f($data, "${year}_1", $key, $fmt),
            f($data, "${year}_2", $key, $fmt),
            f($data, "${year}_3", $key, $fmt),
            f($data, "${year}_4", $key, $fmt),
            f($data, "${year}_5", $key, $fmt),
            f($data, "${year}_6", $key, $fmt),
            f($data, "${year}_7", $key, $fmt),
            f($data, "${year}_8", $key, $fmt),
            f($data, "${year}_9", $key, $fmt),
            f($data, "${year}_10", $key, $fmt),
            f($data, "${year}_11", $key, $fmt),
            f($data, "${year}_12", $key, $fmt)
            );
      }
      if (sizeof($climo) > 0){
            $table .= @sprintf("<tr><td>%s</td><td>$fmt</td><td>$fmt</td>".
      "<td>$fmt</td><td>$fmt</td><td>$fmt</td><td>$fmt</td>".
      "<td>$fmt</td><td>$fmt</td><td>$fmt</td><td>$fmt</td>".
      "<td>$fmt</td><td>$fmt</td></tr>", "NCEI Climatology",
      $climo["1"][$key], $climo["2"][$key],
      $climo["3"][$key], $climo["4"][$key],
      $climo["5"][$key], $climo["6"][$key],
      $climo["7"][$key], $climo["8"][$key],
      $climo["9"][$key], $climo["10"][$key],
      $climo["11"][$key], $climo["12"][$key]);
      }
      $table .= "</tbody></table>";
      return $table;
}

$preciptable = make_table($data, "precip", $minyear, $maxyear, "%.2f",
      $climo);
$hightable = make_table($data, "avg_high", $minyear, $maxyear, "%.2f",
      $climo);
$lowtable = make_table($data, "avg_low", $minyear, $maxyear, "%.2f",
      $climo);
$temptable = make_table($data, "avg_temp", $minyear, $maxyear, "%.2f",
      $climo);
$noclimo = Array();
$rhtable = make_table($data, "avg_rh", $minyear, $maxyear, "%.1f%%",
      $noclimo);

$timestamp = mktime(0,0,0, $month, 1, $year);
$lmonth = $timestamp - 5*86400;
$nmonth = $timestamp + 35*86400;
$llink = sprintf("monthlysum.php?station=%s&amp;network=%s&amp;month=%s&amp;year=%s",
            $station, $network, date("m", $lmonth), date("Y", $lmonth));
$nlink = sprintf("monthlysum.php?station=%s&amp;network=%s&amp;month=%s&amp;year=%s",
            $station, $network, date("m", $nmonth), date("Y", $nmonth));
$ltext = date("M Y", $lmonth);
$ntext = date("M Y", $nmonth);

$ms = monthSelect($month);
$minyear = isset($metadata["archive_begin"]) ? intval(date("Y", $metadata["archive_begin"])): 1929;
$ys = yearSelect($minyear, $year);

$plot1 = sprintf("/plotting/auto/plot/17/month:%s"
      ."::year:%s::station:%s::network:%s::dpi:100.png", $month, 
      $year, $station, $network);
$plot2 = sprintf("/plotting/month/rainfall_plot.php?month=%s&amp;".
      "year=%s&amp;network=%s&amp;station=%s", $month, $year, $network, $station);

$jsextracaller = isset($_GET["year"]) ? "go();": "";
$t->jsextra = <<<EOM
<script>
function go(){
      document.getElementById("mycharts").scrollIntoView();
}
$(document).ready(function(){
      $("#gogogo").click(function(){
            go();
      });
      ${jsextracaller}
});
</script>
EOM;
$t->content = <<<EOF

<p><button id="gogogo" role="button" class="btn btn-primary"><i class="fa fa-arrow-down"></i> View Monthly Charts</button></p>

<p>The following tables present IEM computed monthly data summaries based on
daily data provided by or computed for the IEM. A <a href="/request/daily.phtml?network=${network}">download interface</a>
exists for the daily summary information.  The climatology is provided by the
nearest NCEI climate station ({$metadata["ncdc81"]}) within the current 1981-2010 
dataset.</p>

<p><i class="fa fa-table"></i> To load shown data into Microsoft Excel,
highlight the table information with your mouse and then copy/paste into Excel.</p>

<h3>Precipitation Totals [inch]</h3>

{$preciptable}

<h3>Average Daily High Temperature [F]</h3>

{$hightable}

<h3>Average Daily Low Temperature [F]</h3>

{$lowtable}

<h3>Average Daily Temperature (high+low)/2 [F]</h3>

{$temptable}


<h3>Average Relative Humidity [%]</h3>

<p>This value is computed via a simple average of available observations weighted
by the duration between observations.</p>

{$rhtable}

<h3 id="mycharts">Monthly Plots</h3>

<form method="GET" name="changemonth" action="monthlysum.php#plots">
 <input type="hidden" name="station" value="{$station}">
 <input type="hidden" name="network" value="{$network}">
 <h3>Select month and year:</h3>
 <div class="row">
 <div class="col-sm-3">
 <a href="{$llink}" class="btn btn-default">{$ltext} <i class="fa fa-arrow-left"></i></a>
	</div>
	<div class="col-sm-6">
  {$ms} {$ys}
 <input type="submit" value="Generate Plot">
 </div>
 <div class="col-sm-3">
 <a href="{$nlink}" class="btn btn-default"><i class="fa fa-arrow-right"></i> {$ntext}</a>
</div>
</div>
</form>

<div class="row">
<div class="col-md-12">
<img src="{$plot1}" alt="Monthly Plot" class="img img-responsive">
</div>
</div>

<div class="row">
<div class="col-md-12">
<img src="{$plot2}" alt="Monthly Plot" class="img img-responsive">
</div>
</div>


EOF;
$t->render('sites.phtml');
?>
