<?php
// Giveme JSON data listing products
header("Content-type: application/vnd.geo+json");
require_once '../../config/settings.inc.php';
require_once "../../include/database.inc.php";

$ts = isset($_REQUEST["ts"]) ? strtotime($_REQUEST["ts"]) : 0;
$network = isset($_REQUEST["network"]) ? substr($_REQUEST["network"],0,4): "KCCI";

$connect = iemdb("mesosite");

if ($ts > 0){
	if ($network != 'TV'){
  		$result = pg_exec($connect, 
  		sprintf("SELECT *, ST_x(geom) as lon, ST_y(geom) as lat
    			from camera_log c, webcams w
    			WHERE valid = '%s' and c.cam = w.id
  				and w.network = '%s' ORDER by name ASC", 
    			date('Y-m-d H:i', $ts), $network));
	} else {
		$result = pg_exec($connect,
				sprintf("SELECT *, ST_x(geom) as lon, ST_y(geom) as lat
    			from camera_log c, webcams w
    			WHERE valid = '%s' and c.cam = w.id
				and w.network in ('KCRG', 'KCCI', 'KELO', 'ISUC', 'MCFC')
  				ORDER by name ASC",
						date('Y-m-d H:i', $ts)));
	}
} else if ($network == 'TV'){
	$result = pg_exec($connect, "SELECT *, ST_x(geom) as lon, ST_y(geom) as lat
			from camera_current c, webcams w
			WHERE valid > (now() - '15 minutes'::interval)
			and c.cam = w.id and
			w.network in ('KCCI','KELO','KCRG', 'ISUC', 'MCFC')
			ORDER by name ASC");
} else {
  $result = pg_exec($connect, "SELECT *, ST_x(geom) as lon, ST_y(geom) as lat
  from camera_current c, webcams w 
  WHERE valid > (now() - '15 minutes'::interval) 
  and c.cam = w.id and w.network = '$network'
  ORDER by name ASC");
}


$ar = Array("type"=>"FeatureCollection",
      "features" => Array()
);


for( $i=0; $row = pg_fetch_assoc($result); $i++)
{
	$valid = strtotime($row["valid"]);
  $url = sprintf("//mesonet.agron.iastate.edu/archive/data/".
  		"%s/camera/%s/%s_%s.jpg", gmdate("Y/m/d", $valid), $row["cam"],
  		$row["cam"], gmdate("YmdHi", $valid) );
  $z = Array("type"=>"Feature", "id"=>$row["id"],
            "properties"=>Array(
                "valid" => gmdate("Y-m-d\\TH:i:s\\Z", $valid),
                "cid" => $row["id"],
                "name" => $row["name"],
                "county" => $row["county"],
                "state" => $row["state"],
             	"angle" => $row["drct"],
                "url" => $url
            ),
             "geometry"=>Array("type"=>"Point",
                         "coordinates"=>Array(floatval($row["lon"]),
                         					  floatval($row["lat"]))));

  $ar["features"][] = $z;
}

echo json_encode($ar);
