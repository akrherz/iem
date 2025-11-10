<?php
/* Generate a CSV file based on a request */
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/forms.php";
$mesosite = iemdb("mesosite");
$access = iemdb("iem");
$asos = iemdb("asos");
pg_query($access, "SET TIME ZONE 'UTC'");
pg_query($asos, "SET TIME ZONE 'UTC'");

$stations = array("AMW");

if (array_key_exists("lat", $_GET) && array_key_exists("lon", $_GET)) {
    /* Figure out what station(s) fits the bill */
    $lat = get_float404("lat", null);
    $lon = get_float404("lon", null);
    $sql = sprintf("SELECT id,
      ST_DistanceSphere(geom, ST_geometryfromtext('POINT(%.4f %.4f)',4326)) as dist from stations
      WHERE network ~* 'ASOS' ORDER by dist ASC
      LIMIT 5", $lon, $lat);
    $rs = pg_query($mesosite, $sql);
    for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
        $stations[$i] = $row["id"];
    }
}

$result = "id,valid,tmpf,dwpf,sknt,drct,phour,alti,gust,lon,lat\n";
$prepared = null;
foreach ($stations as $k => $id) {
    if (array_key_exists("date", $_REQUEST)) {
        $ts = strtotime(get_str404("date", null));
        if (is_null($prepared)) {
            $stname = iem_pg_prepare($asos, sprintf("SELECT station as id, valid,
            max(tmpf) as tmpf, max(dwpf) as dwpf, max(sknt) as sknt, max(drct) as drct,
            max(p01i) as phour, max(alti) as alti, max(gust) as gust,
            max(ST_x(s.geom)) as lon, max(ST_y(s.geom)) as lat from alldata t, stations s
            where s.id = $1 and s.network ~* 'ASOS'
            and t.station = s.id and t.valid BETWEEN '%s'::date
            and '%s'::date + '9 days'::interval GROUP by station, valid
            ORDER by valid ASC", date("Y-m-d", $ts), date("Y-m-d", $ts)));
        }
        $rs = pg_execute($asos, $stname, array($id));
    } else {
        $rs = pg_query($access, "SELECT s.id, valid, max(tmpf) as tmpf, max(dwpf) as dwpf,
      max(sknt) as sknt, max(drct) as drct,
      max(phour) as phour, max(alti) as alti, max(gust) as gust,
      max(ST_x(s.geom)) as lon, max(ST_y(s.geom)) as lat from current_log c, stations s
      WHERE s.id = '$id' and s.iemid = c.iemid
      GROUP by id, valid ORDER by valid ASC");
    }
    if (pg_num_rows($rs) == 0) {
        continue;
    }
    while ($row = pg_fetch_assoc($rs)) {
        $result .= sprintf(
            "%s,%s,%s,%s,%s,%s,%s,%s,%s,%.4f,%.4f\n",
            $row["id"],
            $row["valid"],
            $row["tmpf"],
            $row["dwpf"],
            $row["sknt"],
            $row["drct"],
            $row["phour"],
            $row["alti"],
            $row["gust"],
            $row["lon"],
            $row["lat"]
        );
    }
    break;
}

header("Content-type: text/plain");
echo $result;
