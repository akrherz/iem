<?php 
/* Generate a CSV file based on a request */
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$mesosite = iemdb("mesosite");
$access = iemdb("access");
pg_exec($access, "SET TIME ZONE 'GMT'");

$stations = Array("AMW");

if (isset($_GET["lat"]) && isset($_GET["lon"]))
{
  /* Figure out what station(s) fits the bill */
  $sql = sprintf("SELECT id, 
      distance(geom, geometryfromtext('POINT(%.4f %.4f)',4326)) from stations
      WHERE (network ~* 'ASOS' or network ~* 'AWOS') ORDER by distance ASC
      LIMIT 5", $_GET["lon"], $_GET["lat"]);
  $rs = pg_exec($mesosite, $sql);
  for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
  {
    $stations[$i] = $row["id"];
  }
}

$result = "id,valid,tmpf,dwpf,sknt,drct,phour,alti,gust\n";
while(list($k,$id) = each($stations))
{
  $rs = pg_exec($access, "SELECT s.id, valid, max(tmpf) as tmpf, max(dwpf) as dwpf, 
  max(sknt) as sknt, max(drct) as drct,
  max(phour) as phour, max(alti) as alti, max(gust) as gust from current_log c, stations s
  WHERE s.id = '$id' and s.iemid = c.iemid
        GROUP by id, valid ORDER by valid ASC");
  if (pg_num_rows($rs) == 0){ continue; }
  for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
  {
    $result .= sprintf("%s,%s,%s,%s,%s,%s,%s,%s,%s\n", $row["id"],$row["valid"], 
    $row["tmpf"], $row["dwpf"], $row["sknt"], $row["drct"], $row["phour"], $row["alti"],
    $row["gust"]);
  }
  break;
}

header("Content-type: text/plain");
echo $result;

?>
