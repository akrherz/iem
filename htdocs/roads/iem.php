<?php
require_once "/usr/lib64/php/modules/mapscript.php";

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
    $ts = new DateTime(substr($row["valid"], 0, 16), new DateTimeZone("America/Chicago"));
} else {
    $ts = new DateTime($_GET["valid"], new DateTimeZone("America/Chicago"));
}

$map = new MapObj("roads.map");
if ($eightbit) {
    $map->selectOutputFormat("png");
} else {
    $map->selectOutputFormat("png24");
}
$map->imagecolor->setRGB(140, 144, 90);
$map->outputformat->__set('imagemode', MS_IMAGEMODE_RGB);
$map->outputformat->__set('transparent', MS_OFF);

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
$map->__set("width", $width);
$map->__set("height", $height);

$img = $map->prepareImage();

if (isset($_GET["nexrad"])) {
    $gmtts = clone $ts;
    $gmtts->setTimezone(new DateTimeZone("UTC"));
    $radarfn = sprintf("/mesonet/ARCHIVE/data/%s/GIS/uscomp/n0q_%s.png", $gmtts->format("Y/m/d"), $gmtts->format("YmdHi"));
    $radar = $map->getLayerByName("nexrad_n0q");
    $radar->__set("status", MS_ON);
    $radar->__set("data", $radarfn);
    $radar->draw($map, $img);
}

$counties = $map->getLayerByName("counties");
if ($metroview) {
    $counties->__set("status", MS_ON);
    $counties->draw($map, $img);
}

$states = $map->getLayerByName("states");
$states->__set("status", MS_ON);
$states->draw($map, $img);

$visibility = $map->getLayerByName("visibility");
$visibility->__set("status", MS_ON);
$visibility->draw($map, $img);

$roads = $map->getLayerByName("roads");
$roads->__set("status", MS_ON);
$dbvalid = $ts->format('Y-m-d H:i');
# yuck
$dbvalid2 = clone $ts;
$dbvalid2->sub(new DateInterval("P90D"));
$dbvalid2 = $dbvalid2->format('Y-m-d H:i');
if (isset($_GET['valid'])) {
    $sql = <<< EOM
    geom from (
        with data as (
            select b.segid, c.cond_code,
            row_number() OVER (PARTITION by b.segid ORDER by c.valid DESC)
            from roads_base b, roads_log c WHERE b.segid = c.segid 
            and c.valid < '$dbvalid' and c.valid > '$dbvalid2'),
        agg as (
            select * from data where row_number = 1)

        select b.type as rtype, b.int1, random() as boid, b.geom,
        d.cond_code from roads_base b JOIN agg d on (b.segid = d.segid)
        WHERE b.type > 1)
    as foo using UNIQUE boid using SRID=26915
EOM;
    $roads->__set("data", $sql);
}
$roads->draw($map, $img);

$roads_int = $map->getLayerByName("roads-inter");
$roads_int->__set("status", MS_ON);
if (isset($_GET['valid'])) {
    $roads_int->__set("data", str_replace("b.type > 1", "b.type = 1", $sql));
}
$roads_int->draw($map, $img);

if (isset($_GET["trucks"])) {
    // 10 minute window for trucks
    $w1 = clone $ts;
    $w1->sub(new DateInterval("PT5M"));
    $w1 = $w1->format('Y-m-d H:i');
    $w2 = clone $ts;
    $w2->add(new DateInterval("PT5M"));
    $w2 = $w2->format('Y-m-d H:i');
    $trucks = $map->getLayerByName("trucks");
    $trucks->__set("status", MS_ON);
    $trucks->__set("data", "geom from (select geom, random() as boid from " .
        "idot_snowplow_archive WHERE valid > '{$w1}' and valid < '{$w2}') as foo " .
        "using UNIQUE boid using SRID=4326");
    $trucks->draw($map, $img);
}

if ($thumbnail) {
    $logokey2 = $map->getLayerByName("colorkey-small");
} else {
    $logokey2 = $map->getLayerByName("colorkey");
}
$logokey2->__set("status", MS_ON);
$c1 = $logokey2->getClass(0);
$s1 = $c1->getStyle(0);
if ($thumbnail) {
    $s1->__set("size", 30);
} else if ($eightbit) {
    $s1->__set("symbolname", "logokey-8bit");
    $s1->__set("size", 60);
} else {
    $s1->__set("size", 50);
}

$logokey = new layerObj($map);
$logokey->__set("type", MS_SHP_POINTZ);
$logokey->__set("transform", MS_FALSE);
$logokey->__set("status", MS_ON);
$logokey->__set("labelcache", MS_ON);
$logokey->__set("status", MS_ON);

$logokey_c3 = new classObj($logokey);
$logokey_c3s0 = new styleObj($logokey_c3);
$l = $logokey_c3->addLabel(new labelObj());
$logokey_c3->getLabel(0)->__set("buffer", 10);
$logokey_c3->getLabel(0)->__set("size", MS_MEDIUM);
$logokey_c3->getLabel(0)->color->setRGB(0, 0, 0);
$bpt = new pointObj();
$bpt->setXY(300, 300);
$bpt->draw($map, $logokey, $img, 0, "      ");

$map->drawLabelCache($img);

$logokey2->draw($map, $img);

$layer = $map->getLayerByName("credits");
$c = $layer->getClass(0);
$point = new pointObj();
if ($thumbnail) {
    $point->setXY(85, 230);
    $c->label->__set("size", MS_LARGE);
} else {
    $point->setXY(300, 10);
}
$point->draw($map, $layer, $img, 0, $ts->format('Y-m-d h:i A'));

$map->drawLabelCache($img);

header("Content-type: image/png");
echo $img->getBytes();
