<?php 
/* 
 * Helper functions for now for mapping of data
 */
function saveWebImage($img){
    $tempfn = sprintf("%s.png", tempnam("/var/webtmp", "ms"));
    $img->save($tempfn);
    return sprintf("/tmp/%s", basename($tempfn));
}

function iemmap_title($map, $img, $title=null, $subtitle=null){
    $iem_headerbar = $map->getLayerByName("iem_headerbar");
    $iem_headerbar->__set("status", MS_ON);

    $iem_headerbar_logo = $map->getLayerByName("iem_headerbar_logo");
    $iem_headerbar_logo->__set("status", MS_ON);
    
    $iem_headerbar->draw($map, $img);
    $iem_headerbar_logo->draw($map, $img);

    $iem_headerbar_title = $map->getLayerByName("iem_headerbar_title");
    $iem_headerbar_title->__set("status", MS_ON);
        
    if ($title != null){
        $point = new pointObj();
        $point->setXY(80, 28);
        $point->draw($map, $iem_headerbar_title, $img, 0, $title);
    }
    if ($subtitle != null){
        $point = new pointObj();
        $point->setXY(82, 50);
        $point->draw($map, $iem_headerbar_title, $img, 1, $subtitle);
    }
}
