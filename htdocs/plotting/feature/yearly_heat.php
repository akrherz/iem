<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");

$dbconn = iemdb('asos');
for($year=2010;$year<2011;$year++){
  $maxv = 0;
  $sql = "SELECT tmpf, dwpf, valid
  from t${year} WHERE station = 'DSM' 
  and valid < '${year}-06-24' and dwpf > -99 and tmpf > 80 ORDER by valid ASC";
  $rs = pg_query($dbconn, $sql);
  for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
  {
    $relh = relh( f2c($row["tmpf"]), f2c($row["dwpf"]));
    $feel = heat_idx($row["tmpf"], $relh);
    if ($feel > $maxv){
      $maxv = $feel;
    }
    if ($feel > 105){
      print_r($row);
    }
  }
  echo sprintf("%s|%s\n", $year, $maxv);
}

?>
