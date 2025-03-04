<?php
require_once dirname(__FILE__) . "/memcache.php";
require_once dirname(__FILE__) . "/database.inc.php";

$cached_cameras = cacheable("php/cameras.inc.php", 43200)(function(){
    $mesosite = iemdb("mesosite");
    $rs = pg_query($mesosite, "SELECT *, ST_x(geom) as lon, ".
            "ST_y(geom) as lat from webcams ORDER by name ASC");
    $cameras = array();
    while ($row = pg_fetch_assoc($rs)) {
        $cameras[$row["id"]] = array(
            "sts" => strtotime($row["sts"]),
            "ets" => ($row["ets"] === NULL) ? time() + 86400 :
                strtotime($row["ets"]),
            "name" => $row["name"],
            "removed" => ($row["removed"] == 't'),
            "active" => ($row["online"] == 't'),
            "is_vapix" => ($row["is_vapix"] == 't'),
            "lat" => $row["lat"],
            "lon" => $row["lon"],
            "state" => $row["state"],
            "scrape_url" => $row["scrape_url"],
            "network" => $row["network"],
            "moviebase" => $row["moviebase"],
            "ip" => $row["ip"],
            "county" => $row["county"],
            "port" => $row["port"],
        );
    }
    return $cameras;
});

$cameras = $cached_cameras();