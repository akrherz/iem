<?php 
/* 
 * Helper functions for now for mapping of data
 */
function iemmap_title($map, $img, $title=null, $subtitle=null){
	$iem_headerbar = $map->getLayerByName("iem_headerbar");
	$iem_headerbar->set("status", MS_ON);

	$iem_headerbar_logo = $map->getLayerByName("iem_headerbar_logo");
	$iem_headerbar_logo->set("status", MS_ON);
	
	$iem_headerbar->draw($img);
	$iem_headerbar_logo->draw($img);

	$iem_headerbar_title = $map->getLayerByName("iem_headerbar_title");
	$iem_headerbar_title->set("status", MS_ON);
		
	if ($title != null){
		$point = ms_newpointobj();
		$point->setXY(80, 28);
		$point->draw($map, $iem_headerbar_title, $img, 0, $title);
	}
	if ($subtitle != null){
		$point = ms_newpointobj();
		$point->setXY(82, 50);
		$point->draw($map, $iem_headerbar_title, $img, 1, $subtitle);
	}
}
