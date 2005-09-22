<?php
$ts = mktime(0,0,0, $month, $day, $year);
$sqlDate = strftime("%Y-%m-%d", $ts);
$fancyDate = strftime("%d %B %Y", $ts);
$c = pg_connect("10.10.10.20", 5432, "wepp");

function aSortBySecondIndex($multiArray, $secondIndex) {
        while (list($firstIndex, ) = each($multiArray))
                $indexMap[$firstIndex] = $multiArray[$firstIndex][$secondIndex];
        arsort($indexMap);
        while (list($firstIndex, ) = each($indexMap))
                if (is_numeric($firstIndex))
                        $sortedArray[] = $multiArray[$firstIndex];
                else $sortedArray[$firstIndex] = $multiArray[$firstIndex];
        return $sortedArray;
}


$q = "select r.run_id, round(r.runoff / 25.4, 2) as runoff, 
       c.hrap_i as hrap_i, m.name as man_name,
       round( r.loss * 4.463, 2) as loss, 
       round( r.precip / 25.4, 2) as precip,
       n.steep as steep
       from results r, combos c, nri n, managements m
       WHERE c.id = r.run_id and c.nri_id = n.id and
       n.man_id = m.man_id and c.model_twp = '$twp' 
       and r.valid = '$sqlDate' ";
$rs = pg_exec($c, $q);

$url = "<a href=\"township.phtml?twp=$twp&year=$year&month=$month&day=$day&sortcol=";
echo "<p><b>$fancyDate runs producing erosion:</b><br>
  <table border=1>
  <tr>
    <th>". $url ."run_id\">Run ID</a></th>
    <th>". $url ."hrap_i\">HRAP ID:</a></th>
    <th>". $url ."man_name\">Management:</a></th>
    <th>". $url ."steep\">Slope:</a></th>
    <th>". $url ."runoff\">Runoff</a>[in]</th>
    <th>". $url ."loss\">Soil Loss</a> [t/a]</th>
    <th>". $url ."precip\">Rainfall</a> [in]</th></tr>\n";

$ar = Array();
for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) 
{
$ar[] = $row;
}

if (! isset($sortcol) ) $sortcol = "run_id";
$fa = Array();
if (sizeof($ar) > 0) 
$fa = aSortBySecondIndex($ar, $sortcol);

while (list ($key, $val) = each ($fa))  {
  echo "<tr><td> ". $fa[$key]["run_id"] ."</td><td>". $fa[$key]["hrap_i"] ."</td><td><a href=\"/wepp/meta/management.phtml?man_id=". $fa[$key]["man_name"] ."\">". $fa[$key]["man_name"] ."</a></td><td>". $fa[$key]["steep"] ."</td><td>". $fa[$key]["runoff"] ."</td><td>". $fa[$key]["loss"] ."</td><td>". $fa[$key]["precip"] ."</td></tr>\n";

}
if ($i == 0) echo "<tr><th colspan=7>No Events Found</th></tr>";

echo "</table>";

?>
