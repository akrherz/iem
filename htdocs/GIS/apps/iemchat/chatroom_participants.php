<?php
/* Create a map of chatroom participants */
include("../../../../config/settings.inc.php");

require_once "$rootpath/include/Zend/XmlRpc/Client.php";
require_once "$rootpath/include/database.inc.php";
$mesosite = iemdb("postgis");

$client = new Zend_XmlRpc_Client('https://iemchat.com/iembot-xmlrpc');

$ar = $client->call('getAllRoomCount');
$cats = Array("2","6","11","16","21","200");
$regex = Array("2"=>Array(),"6"=>Array(),"11"=>Array(),"16"=>Array(),
               "21"=>Array(), "200" => Array() );
$d = gmdate("Y-m-d H:i:00+00" ,  time());
while( list($idx, $tar) = each($ar))
{
  $room = $tar[0];
  $cnt = $tar[1];
  if (isset($_GET["logit"]))
  {
    $sql = "INSERT into iemchat_room_participation(room, valid, users) 
            VALUES ('$room', '$d', '$cnt')";
    pg_exec($mesosite, $sql);
  }
  if (strlen($room) != 7 or substr($room,3,4) != "chat"){ continue; }
  $wfo = strtoupper(substr($room,0,3));
  reset($cats);
  while( list($key,$ceil) = each($cats) ){
    if ($cnt < $ceil){ $regex[$ceil][] = $wfo; break ;}
  }
}
while( list($key,$ar) = each($regex) ){
  $regex[$key] = implode("|", $ar);
}




$map = ms_newMapObj("$rootpath/data/gis/base2163.map");
$map->setExtent(-2110437, -2253038.125, 2548326, 1241034.125);
$map->setSize(480,640);

$namer = $map->getlayerbyname("namerica");
$namer->set("status", MS_ON);

$lakes = $map->getlayerbyname("lakes");
$lakes->set("status", MS_ON);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

//$bars = $map->getlayerbyname("bars");
//$bars->set("status", MS_ON);

$cwa = ms_newLayerObj($map);
$cwa->set("name", "cwa2");
$cwa->set("data", "/mesonet/data/gis/static/shape/4326/nws/cwas.shp");
$cwa->set("type", MS_SHAPE_POLYGON);
$cwa->set("status", MS_ON);
$cwa->setProjection("init=epsg:4326");
$cwa->set("classitem", "WFO");

$cwac0 = ms_newClassObj($cwa);
$cwac0->set("name", "None");
$cwac0->setExpression("/".$regex["2"]."/");
$cwac0s0 = ms_newStyleObj($cwac0);
$cwac0s0->color->setRGB(135,135,135);

$cwac0 = ms_newClassObj($cwa);
$cwac0->set("name", "1-5");
$cwac0->setExpression("/".$regex["6"]."/");
$cwac0s0 = ms_newStyleObj($cwac0);
$cwac0s0->color->setRGB(99,99,255);

$cwac0 = ms_newClassObj($cwa);
$cwac0->set("name", "6-10");
$cwac0->setExpression("/".$regex["11"]."/");
$cwac0s0 = ms_newStyleObj($cwac0);
$cwac0s0->color->setRGB(9,255,209);

$cwac0 = ms_newClassObj($cwa);
$cwac0->set("name", "11-15");
$cwac0->setExpression("/".$regex["16"]."/");
$cwac0s0 = ms_newStyleObj($cwac0);
$cwac0s0->color->setRGB(9,255,9);

$cwac0 = ms_newClassObj($cwa);
$cwac0->set("name", "16-20");
$cwac0->setExpression("/".$regex["21"]."/");
$cwac0s0 = ms_newStyleObj($cwac0);
$cwac0s0->color->setRGB(190,255,9);

$cwac0 = ms_newClassObj($cwa);
$cwac0->set("name", "21+");
$cwac0->setExpression("/".$regex["200"]."/");
$cwac0s0 = ms_newStyleObj($cwac0);
$cwac0s0->color->setRGB(255,255,9);


$img = $map->prepareImage();
$namer->draw($img);
$lakes->draw($img);
$cwa->draw($img);
$states->draw($img);
$map->embedlegend($img);

$watches = $map->getlayerbyname("watches");
$watches->set("connection", $_DATABASES["postgis"] );
$watches->set("status", 1);
$watches->set("data", "geom from (select type as wtype, geom, oid from watches where expired > now() and issued <= now() ) as foo using unique oid using srid=4326");
$watches->draw($img);


$bar640t = $map->getLayerByName("bar640t");
$bar640t->set("status", 1);
$bar640t->draw($img);

$tlayer = $map->getLayerByName("bar640t-title");
$point = ms_newpointobj();
$point->setXY(80, 12);
$point->draw($map, $tlayer, $img, 0,"IEMCHAT Users In Chatroom");
$point->free();

$point = ms_newpointobj();
$point->setXY(80, 29);
$d = strftime("%d %B %Y %-2I:%M %p %Z" ,  time());
$point->draw($map, $tlayer, $img, 1,"$d");
$point->free();

$map->drawLabelCache($img);

$layer = $map->getLayerByName("logo");
$point = ms_newpointobj();
$point->setXY(40, 26);
$point->draw($map, $layer, $img, "logo", "");
$point->free();



header("Content-type: image/png");
$img->saveImage('');
?>
