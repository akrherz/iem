<?php
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
$con = iemdb("postgis");

$eightbit = isset($_GET["8bit"]);
$metroview = isset($_GET["metro"]);
$thumbnail = isset($_GET["thumbnail"]);

if (!isset($_GET["valid"])) {
    $sql = "SELECT max(valid) as valid from roads_current";
    $rs = pg_query($con, $sql);

    $row = pg_fetch_array($rs, 0);
    $ts = strtotime(substr($row["valid"], 0, 16));
} else {
    $ts = strtotime($_GET["valid"]);
}


$map = new MapObj("roads.map");
if ($eightbit) {
    $map->selectOutputFormat("png");
} else {
    $map->selectOutputFormat("png24");
}
$map->imagecolor->setRGB(140, 144, 90);
$map->outputformat->set('imagemode', MS_IMAGEMODE_RGB);
$map->outputformat->set('transparent', MS_OFF);

$map->setextent(200000, 4440000, 710000, 4940000);
if ($metroview) {
    $map->setextent(376000, 4560000, 535000, 4680000);
}
$height = 496;
$width = 640;
if ($thumbnail) {
    $height = 240;
    $width = 320;
}
$map->set("width", $width);
$map->set("height", $height);


$img = $map->prepareImage();


if (isset($_GET["nexrad"])) {
    $radarfn = gmstrftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/n0q_%Y%m%d%H%M.png", $ts);
    $radar = $map->getlayerbyname("nexrad_n0q");
    $radar->set("status", MS_ON);
    $radar->set("data", $radarfn);
    $radar->draw($img);
}

$counties = $map->getlayerbyname("counties");
if ($metroview) {
    $counties->set("status", MS_ON);
    $counties->draw($img);
}

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);
$states->draw($img);

$visibility = $map->getlayerbyname("visibility");
$visibility->set("status", MS_ON);
$visibility->draw($img);

$roads = $map->getlayerbyname("roads");
$roads->set("status", MS_ON);
$dbvalid = date('Y-m-d H:i', $ts);
$dbvalid2 = date('Y-m-d H:i', $ts - 14 * 86400);
if (isset($_GET['valid'])) {
    $roads->set("data", "geom from (with data as (" .
        "select b.type as rtype, b.int1, b.segid, c.cond_code, " .
        "row_number() OVER (PARTITION by b.segid ORDER by c.valid DESC) " .
        "from roads_base b, roads_log c WHERE b.segid = c.segid " .
        "and b.type > 1 and c.valid < '$dbvalid' and " .
        "c.valid > '$dbvalid2'), " .
        "agg as (select * from data where row_number = 1) " .
        "select b.type as rtype, b.int1, random() as boid, b.geom, " .
        "coalesce(d.cond_code, 0) as cond_code from " .
        "roads_base b LEFT JOIN agg d on (b.segid = d.segid) " .
        "WHERE b.type > 1 and " .
        "b.archive_end > '$dbvalid' and b.archive_begin < '$dbvalid')" .
        "as foo using UNIQUE boid using SRID=26915");
}
$roads->draw($img);

$roads_int = $map->getlayerbyname("roads-inter");
$roads_int->set("status", MS_ON);
if (isset($_GET['valid'])) {
    $roads_int->set("data", "geom from (with data as (" .
        "select b.type as rtype, b.int1, b.segid, c.cond_code, " .
        "row_number() OVER (PARTITION by b.segid ORDER by c.valid DESC) " .
        "from roads_base b, roads_log c WHERE b.segid = c.segid " .
        "and b.type > 1 and c.valid < '$dbvalid' and " .
        "c.valid > '$dbvalid2'), " .
        "agg as (select * from data where row_number = 1) " .
        "select b.type as rtype, b.int1, random() as boid, b.geom, " .
        "coalesce(d.cond_code, 0) as cond_code from " .
        "roads_base b LEFT JOIN agg d on (b.segid = d.segid) " .
        "WHERE b.type = 1 and " .
        "b.archive_end > '$dbvalid' and b.archive_begin < '$dbvalid')" .
        "as foo using UNIQUE boid using SRID=26915");
}
$roads_int->draw($img);

if (isset($_GET["trucks"])) {
    // 10 minute window for trucks
    $w1 = date('Y-m-d H:i', $ts - 300);
    $w2 = date('Y-m-d H:i', $ts + 300);
    $trucks = $map->getlayerbyname("trucks");
    $trucks->set("status", MS_ON);
    $trucks->set("data", "geom from (select geom, random() as boid from " .
        "idot_snowplow_archive WHERE valid > '{$w1}' and valid < '{$w2}') as foo " .
        "using UNIQUE boid using SRID=4326");
    $trucks->draw($img);
}

//$roads_lbl = $map->getlayerbyname("roads_label");
//$roads_lbl->draw($img);
//$roads_lbl->set("connection", $_DATABASE);

if ($thumbnail) {
    $logokey2 = $map->getlayerbyname("colorkey-small");
} else {
    $logokey2 = $map->getlayerbyname("colorkey");
}
$logokey2->set("status", MS_ON);
$c1 = $logokey2->getClass(0);
$s1 = $c1->getStyle(0);
if ($thumbnail) {
    $s1->set("size", 30);
} else if ($eightbit) {
    $s1->set("symbolname", "logokey-8bit");
    $s1->set("size", 60);
} else {
    $s1->set("size", 50);
}


$logokey = ms_newLayerObj($map);
$logokey->set("type", MS_SHP_POINT);
$logokey->set("transform", MS_FALSE);
$logokey->set("status", MS_ON);
$logokey->set("labelcache", MS_ON);
$logokey->set("status", MS_ON);


$logokey_c3 = ms_newClassObj($logokey);
$logokey_c3s0 = ms_newStyleObj($logokey_c3);
$l = $logokey_c3->addLabel(new labelObj());
$logokey_c3->getLabel(0)->set("buffer", 10);
$logokey_c3->getLabel(0)->set("size", MS_MEDIUM);
$logokey_c3->getLabel(0)->color->setRGB(0, 0, 0);
$bpt = ms_newpointobj();
$bpt->setXY(300, 300);
$bpt->draw($map, $logokey, $img, 0, "      ");

$map->drawLabelCache($img);

$logokey2->draw($img);

$layer = $map->getLayerByName("credits");
$c = $layer->getClass(0);
$point = ms_newpointobj();
if ($thumbnail) {
    $point->setXY(85, 230);
    $c->label->set("size", MS_LARGE);
} else {
    $point->setXY(300, 10);
}
$point->draw($map, $layer, $img, 0, date('Y-m-d h:i A', $ts));


//$point = ms_newpointobj();
//$point->setXY(500, 22);
//$point->draw($map, $layer, $img, 1, "Limited Visibility");

$map->drawLabelCache($img);

header("Content-type: image/png");
$img->saveImage('');
