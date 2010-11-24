<?php
/* Something to generate the plots! */

include_once("../../../../config/settings.inc.php");


if (isset($argv))
   for ($i=1;$i<count($argv);$i++)
   {
       $it = split("=",$argv[$i]);
       $_GET[$it[0]] = $it[1];
   }
//print_r($_GET);
//die();

/* stuff that we need to $_GET[] */
$dstr = isset($_GET["dstr"]) ? $_GET["dstr"] : date("Y-m-d", time() - 86400);
$tokens = explode("-", $dstr);
$year = $tokens[0];
$month = $tokens[1];
$day = $tokens[2];

$extents = isset($_GET['extents']) ? $_GET['extents'] : 
		"-104.2, 36, -80, 50";
$layers = isset($_GET['layers']) ? $_GET['layers'] : 
		Array("data", "states", "counties");
$var = isset($_GET['var']) ? $_GET['var'] : "rainfall_in";
$map_height = isset($_GET['height']) ? $_GET['height'] : 480;
$map_width = isset($_GET['width']) ? $_GET['width'] : 640;
$advanced = isset($_GET["advanced"]) ? 1 : 0;

/* Time related stuff */
$ts = mktime(0,0,0, $month, $day, $year);

/* Color table, blue to brown */
$c = Array();
$c[0] = Array('r'=>255,'g'=>102,'b'=>   0); // 
$c[1] = Array('r'=>255,'g'=>153,'b'=>   0); // 
$c[2] = Array('r'=>255,'g'=> 204,'b'=>   0); // 
$c[3] = Array('r'=>255,'g'=> 232,'b'=>   0); // 
$c[4] = Array('r'=>255,'g'=> 255,'b'=>   0); // 
$c[5] = Array('r'=>204,'g'=> 255,'b'=>   0); // 
$c[6] = Array('r'=> 51,'g'=> 255,'b'=>   0); // 
$c[7] = Array('r'=>102,'g'=> 255,'b'=> 153); // 
$c[8] = Array('r'=> 24,'g'=> 255,'b'=> 255); // 
$c[9] = Array('r'=>  0,'g'=> 212,'b'=> 255); // 
$c[10] = Array('r'=>  0,'g'=> 102,'b'=> 255); // 
$c[11] = Array('r'=>  0,'g'=>   0,'b'=> 255); // 

$cr = array_reverse($c);

$ramps = Array(
	0 =>  Array(0.05, 0.1, 0.25, 0.5, 0.75, 1, 1.5, 2,3,5,7), // Rainfall (inch)
	1 => Array(-10, 0, 10, 20, 30, 40, 50, 60,70,80,90),
	2 => Array(0, 10, 20, 30, 40, 50, 60,70,80,90,100),
	3 =>  Array(0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6,0.7,0.8,0.9), // Rainfall (inch)
	4 =>  Array(0.1, 0.5, 1, 2.5, 5, 7.5, 10, 15,20,30,40), // Rainfall (inch)
);

$params = Array(
"rainfall_in" => Array('dbstr' => 'bogus',
  'units' => 'in', 'cramp' => $cr,
  'title' => "Daily Rainfall: ",
  'table' => "bogus", 'myramp' => 0,
  'maplayer' => 'data', 
  'dbdate' => strftime("%Y-%m-%d", $ts),
  'sql' => "the_geom from (select d.fips,
    d.precip / 25.4 as da,
    the_geom from weather d, counties c
    WHERE d.valid = '". strftime("%Y-%m-%d", $ts) ."' and d.fips = c.fips) as foo
    using unique fips using srid=4326"),

"rh" => Array('dbstr' => 'bogus',
  'units' => '%', 'cramp' => $cr,
  'title' => "Relative Humidity for: ",
  'table' => "bogus", 'myramp' => 2,
  'maplayer' => 'data', 
  'dbdate' => strftime("%Y-%m-%d", $ts),
  'sql' => "the_geom from (select d.fips,
    rh as da,
    the_geom from weather d, counties c
    WHERE d.valid = '". strftime("%Y-%m-%d", $ts) ."' and d.fips = c.fips) as foo
    using unique fips using srid=4326"),


"dailylow" => Array('dbstr' => 'bogus',
  'units' => 'Fahrenhit', 'cramp' => $cr,
  'title' => "Low Temperature for: ",
  'table' => "bogus", 'myramp' => 1,
  'maplayer' => 'data', 
  'dbdate' => strftime("%Y-%m-%d", $ts),
  'sql' => "the_geom from (select d.fips,
    round(((1.8 * d.low::real) + 32.0)::numeric, 0) as da,
    the_geom from weather d, counties c
    WHERE d.valid = '". strftime("%Y-%m-%d", $ts) ."' and d.fips = c.fips) as foo
    using unique fips using srid=4326"),


"dailyhigh" => Array('dbstr' => 'bogus',
  'units' => 'Fahrenhit', 'cramp' => $cr,
  'title' => "High Temperature for: ",
  'table' => "bogus", 'myramp' => 1,
  'maplayer' => 'data', 
  'dbdate' => strftime("%Y-%m-%d", $ts),
  'sql' => "the_geom from (select d.fips,
    round(((1.8 * d.high::real) + 32.0)::numeric, 0) as da,
    the_geom from weather d, counties c
    WHERE d.valid = '". strftime("%Y-%m-%d", $ts) ."' and d.fips = c.fips) as foo
    using unique fips using srid=4326"),



"evap" => Array('dbstr' => 'bogus',
  'units' => 'inches', 'cramp' => $cr,
  'title' => "Evaporation for: ",
  'table' => "bogus", 'myramp' => 3,
  'maplayer' => 'data', 
  'dbdate' => strftime("%Y-%m-%d", $ts),
  'sql' => "the_geom from (select d.fips,
    evaporation / 25.4 as da,
    the_geom from weather d, counties c
    WHERE d.valid = '". strftime("%Y-%m-%d", $ts) ."' and d.fips = c.fips) as foo
    using unique fips using srid=4326"),

"solar" => Array('dbstr' => 'bogus',
  'units' => 'MJ', 'cramp' => $cr,
  'title' => "Solar Radiation for: ",
  'table' => "bogus", 'myramp' => 4,
  'maplayer' => 'data', 
  'dbdate' => strftime("%Y-%m-%d", $ts),
  'sql' => "the_geom from (select d.fips,
    solar as da,
    the_geom from weather d, counties c
    WHERE d.valid = '". strftime("%Y-%m-%d", $ts) ."' and d.fips = c.fips) as foo
    using unique fips using srid=4326"),


);
$param = $params[$var];
$param['ramp'] = $ramps[ $param['myramp'] ];
$param["title"] .= strftime("%d %b %Y", $ts);



/* Start Mapping */
$map = ms_newMapObj("base.map");
$map->setSize($map_width, $map_height);

/* Set Extents */
$arExtents = explode(",", $extents);
$map->setextent($arExtents[0], $arExtents[1], $arExtents[2], $arExtents[3]);


/* Prepare the Image */
$img = $map->prepareImage();

function add_and_draw($name)
{
	global $layers, $map, $img;
	if (in_array($name, $layers) )
	{
		$lyr = $map->getlayerbyname($name);
		$lyr->set("status", MS_ON );
		$lyr->draw($img);
	}
}


$colors = $param["cramp"];
$rainfall = $map->getlayerbyname("highs");
$rainfall->set("status", MS_ON);
$rainfall->set("data", $param["sql"]);

$bins = $param["ramp"];

if ($var == "rainfall_in")
{
  $cz = ms_newClassObj($rainfall);
  $cz->setexpression("([da] == 0)");
}

$c0 = ms_newClassObj($rainfall);
$c0->setexpression("([da] < ". $bins[0] .")");
$c0s = ms_newStyleObj($c0);
$c0s->color->setRGB($colors[0]['r'], $colors[0]['g'], $colors[0]['b']);

$c1 = ms_newClassObj($rainfall);
$c1->setexpression("([da] < ". $bins[1] .")");
$c1s = ms_newStyleObj($c1);
$c1s->color->setRGB($colors[1]['r'], $colors[1]['g'], $colors[1]['b']);

$c2 = ms_newClassObj($rainfall);
$c2->setexpression("([da] < ". $bins[2] .")");
$c2s = ms_newStyleObj($c2);
$c2s->color->setRGB($colors[2]['r'], $colors[2]['g'], $colors[2]['b']);

$c3 = ms_newClassObj($rainfall);
$c3->setexpression("([da] < ". $bins[3] .")");
$c3s = ms_newStyleObj($c3);
$c3s->color->setRGB($colors[3]['r'], $colors[3]['g'], $colors[3]['b']);

$c4 = ms_newClassObj($rainfall);
$c4->setexpression("([da] < ". $bins[4] .")");
$c4s = ms_newStyleObj($c4);
$c4s->color->setRGB($colors[4]['r'], $colors[4]['g'], $colors[4]['b']);

$c5 = ms_newClassObj($rainfall);
$c5->setexpression("([da] < ". $bins[5] .")");
$c5s = ms_newStyleObj($c5);
$c5s->color->setRGB($colors[5]['r'], $colors[5]['g'], $colors[5]['b']);

$c6 = ms_newClassObj($rainfall);
$c6->setexpression("([da] < ". $bins[6] .")");
$c6s = ms_newStyleObj($c6);
$c6s->color->setRGB($colors[6]['r'], $colors[6]['g'], $colors[6]['b']);

$c7 = ms_newClassObj($rainfall);
$c7->setexpression("([da] < ". $bins[7] .")");
$c7s = ms_newStyleObj($c7);
$c7s->color->setRGB($colors[7]['r'], $colors[7]['g'], $colors[7]['b']);

$c8 = ms_newClassObj($rainfall);
$c8->setexpression("([da] < ". $bins[8] .")");
$c8s = ms_newStyleObj($c8);
$c8s->color->setRGB($colors[8]['r'], $colors[8]['g'], $colors[8]['b']);

$c9 = ms_newClassObj($rainfall);
$c9->setexpression("([da] < ". $bins[9] .")");
$c9s = ms_newStyleObj($c9);
$c9s->color->setRGB($colors[9]['r'], $colors[9]['g'], $colors[9]['b']);

$c10 = ms_newClassObj($rainfall);
$c10->setexpression("([da] < ". $bins[10] .")");
$c10s = ms_newStyleObj($c10);
$c10s->color->setRGB($colors[10]['r'], $colors[10]['g'], $colors[10]['b']);

$c11 = ms_newClassObj($rainfall);
$c11->setexpression("([da] >= ". $bins[10] .")");
$c11s = ms_newStyleObj($c11);
$c11s->color->setRGB($colors[11]['r'], $colors[11]['g'], $colors[11]['b']);

$rainfall->draw($img);

add_and_draw("counties");
add_and_draw("states");

/* Need something to draw bars! */
$bar = $map->getlayerbyname("bar");

$layer = $map->getLayerByName("credits");
$rt = ms_newRectObj();
$rt->setextent(0, 30, $map_width, 5);
$rt->draw($map, $bar, $img, 0, "");
$rt->free();
$point = ms_newpointobj();
$point->setXY(50, 20);
$point->draw($map, $layer, $img, 0, $param["title"]);


$rt = ms_newRectObj();
$rt->setextent(0, $map_height, $map_width, $map_height - 20);
$rt->draw($map, $bar, $img, 0, "");
$rt->free();

$rt = ms_newRectObj();
$rt->setextent(0, $map_height, 60, $map_height - 210);
$rt->draw($map, $bar, $img, 0, "");
$rt->free();

$point = ms_newpointobj();
$point->setXY(5, $map_height - 10);
$point->draw($map, $layer, $img, 1, "Map Units: ". $param["units"] ."  NC1018 EXPERIMENTAL PLOT         Map Generated on  ". date("Y/m/d"));

$layer = $map->getLayerByName("singlebox");
$x = 1;
$y = $map_height - 200;
$height = 14;
$width = 10;
for ($k=11;$k>=0;$k--){
 $p = ms_newRectObj();
 $p->setextent($x, $y + $height, $x + $width, $y);
 $cl = ms_newClassObj($layer);
 $st = ms_newStyleObj($cl);
 $st->color->setRGB($colors[$k]['r'], $colors[$k]['g'], $colors[$k]['b']);
 $st->outlinecolor->setRGB(255, 255, 255);
 $cl->label->color->setRGB(255, 255, 255);
 $cl->label->set("type", MS_BITMAP);
 $cl->label->set("size", MS_MEDIUM);
 $cl->label->set("position", MS_UR);
 $cl->label->set("offsetx", $width * 1.25);
 $cl->label->set("offsety", 0);
 $p->draw($map, $layer, $img, 11- $k, @$param["ramp"][$k]);
 $p->free();
 $y = $y + $height;
}


header("Content-type: image/png");
$img->saveImage('');
//$map->save('/tmp/t.map');
?>
