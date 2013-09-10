<?php

$memcache = new Memcache;
$memcache->connect('iem-memcached', 11211);
$cameras = $memcache->get("php/cameras.inc.php");
if ($cameras){
	return;
}

include_once(dirname(__FILE__)."/database.inc.php");

$mesosite = iemdb("mesosite");
$rs = pg_query($mesosite, "SELECT *, ST_x(geom) as lon,
		ST_y(geom) as lat from webcams ORDER by name ASC");
$cameras = Array();
for($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
	$cameras[ $row["id"] ] = Array(
			"sts" => strtotime($row["sts"]),
			"ets" => strtotime(($row["ets"] === NULL) ? time(): $row["ets"]),
			"name" => $row["name"],
			"removed" => ($row["removed"] == 't'),
			"active"=> ($row["online"] == 't'),
			"lat"=> $row["lat"],
			"lon"=> $row["lon"],
			"state" => $row["state"],
			"network"=> $row["network"],
			"moviebase" => $row["moviebase"],
			"ip" => $row["ip"],
			"county"=> $row["county"],
			"port"=>$row["port"],
	);
}
$memcache->set("php/cameras.inc.php", $cameras, false, 86400);
?>