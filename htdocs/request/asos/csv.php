<?php 
/* Generate a CSV file based on a request */
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
$mesosite = iemdb("mesosite");
$access = iemdb("iem");
$asos = iemdb("asos");
pg_exec($access, "SET TIME ZONE 'UTC'");
pg_exec($asos, "SET TIME ZONE 'UTC'");

$stations = Array("AMW");

if (isset($_GET["lat"]) && isset($_GET["lon"]))
{
  /* Figure out what station(s) fits the bill */
  $sql = sprintf("SELECT id, 
      ST_DistanceSphere(geom, ST_geometryfromtext('POINT(%.4f %.4f)',4326)) as dist from stations
      WHERE (network ~* 'ASOS' or network ~* 'AWOS') ORDER by dist ASC
      LIMIT 5", $_GET["lon"], $_GET["lat"]);
  $rs = pg_exec($mesosite, $sql);
  for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
  {
    $stations[$i] = $row["id"];
  }
}

$result = "id,valid,tmpf,dwpf,sknt,drct,phour,alti,gust,lon,lat\n";
$prepared = null;
while(list($k,$id) = each($stations))
{
	if (isset($_REQUEST["date"])){
		$ts = strtotime($_REQUEST["date"]);
		if ($prepared == null){
		  $prepared = pg_prepare($asos, "SELECT", sprintf("SELECT station as id, valid,
		    max(tmpf) as tmpf, max(dwpf) as dwpf, max(sknt) as sknt, max(drct) as drct,
		    max(p01i) as phour, max(alti) as alti, max(gust) as gust, 
		    max(ST_x(s.geom)) as lon, max(ST_y(s.geom)) as lat from alldata t, stations s
		    where s.id = $1 and (s.network ~* 'ASOS' or s.network ~* 'AWOS')
		    and t.station = s.id and t.valid BETWEEN '%s'::date 
		    and '%s'::date + '9 days'::interval GROUP by station, valid 
		    ORDER by valid ASC", date("Y-m-d", $ts), date("Y-m-d", $ts) ));
		}
		$rs = pg_execute($asos, "SELECT", Array($id));	
	} else {
    $rs = pg_exec($access, "SELECT s.id, valid, max(tmpf) as tmpf, max(dwpf) as dwpf, 
      max(sknt) as sknt, max(drct) as drct,
      max(phour) as phour, max(alti) as alti, max(gust) as gust,
      max(ST_x(s.geom)) as lon, max(ST_y(s.geom)) as lat from current_log c, stations s
      WHERE s.id = '$id' and s.iemid = c.iemid
      GROUP by id, valid ORDER by valid ASC");
	}
  if (pg_num_rows($rs) == 0){ continue; }
  for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
  {
    $result .= sprintf("%s,%s,%s,%s,%s,%s,%s,%s,%s,%.4f,%.4f\n", $row["id"],$row["valid"], 
    $row["tmpf"], $row["dwpf"], $row["sknt"], $row["drct"], $row["phour"], $row["alti"],
    $row["gust"], $row["lon"], $row["lat"]);
  }
  break;
}

header("Content-type: text/plain");
echo $result;

?>
