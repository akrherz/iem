<?php
//=======================================================================
// File:        JPGRAPH_COLORMAP.INC.PHP
// Description: Class to handle the usage of colormaps. This is used to
//              map a number to the specified range [min,max] and translate
//              this to a color in the chosen color map
//
// Created:     2009-07-10
// Ver:         $Id: jpgraph_colormap.inc.php 1587 2009-07-14 00:29:27Z ljp $
//
// Copyright (c) Aditus Consulting. All rights reserved.
//
// Some colormaps inspired from "ColorBrewer" research page.
// See: http://www.personal.psu.edu/cab38/ColorBrewer/ColorBrewer.html */
//
//========================================================================

class ColorMap {
    const EPSILON = 1.0e-8;
    private $rgb = null;
    private $imap = 0;
    private $irange = array(0,0), $irange_dist = 0 ;
    private $inumcolors = 64;
    private $inullcolor = 'gray';
    private $isinit = false;
    private $icolor_buckets = array();
    private $ipredefmaps = array(

    	/* Standard colors */

        /* HEAT */
        0 => array('black','darkred','orange','yellow','white'),

        /* BW */
        1 => array('black','gray','white'),

        /* RAINBOW */
        2 => array('darkred','red','orange','yellow','green','blue','darkblue','indigo','violet'),

        /* BLUERED1 */
        3 => array('navy','blue','black','red','darkred'),

        /* BLUERED2 */
        4 => array('navy','blue','yellow','red','darkred'),

        /* GREENRED1 */
        5 => array('darkgreen','green','black','red','darkred'),

        /* GREENRED2 */
        6 => array('darkgreen','green','yellow','red','darkred'),

        /* GREENBLUE1 */
        7 => array('darkblue','blue','black','green','darkgreen'),

        /* GREENBLUE2 */
        8 => array('darkblue','blue','yellow', 'green','darkgreen'),

	    /* BLUEGREENRED */
        9 => array('blue','darkgreen','green','red','darkred'),


        /* Colormaps inspired from "ColorBrewer" research page. */
        /* See: http://www.personal.psu.edu/cab38/ColorBrewer/ColorBrewer.html */

        /* Center white colors */
        10 => array('#b35806','#e08214','#fdb863','#fee0b6','#f7f7f7','#d8daeb','#b2abd2','#8073ac','#542788'),

        11 => array('#8c510a','#bf812d','#dfc27d','#f6e8c3','#f5f5f5','#c7eae5','#80cdc1','#35978f','#01665e'),

        12 => array('#b2182b','#d6604d','#f4a582','#fddbc7','#f7f7f7','#d1e5f0','#92c5de','#4393c3','#2166ac'),

        13 => array('#b2182b','#d6604d','#f4a582','#fddbc7','#ffffff','#e0e0e0','#bababa','#878787','#4d4d4d'),

		14 => array('#d73027','#f46d43','#fdae61','#fee08b','#ffffdf','#d9ef8b','#a6d96a','#66bd63','#1a9850'),

		/* Sequential */
		15 => array('#fff7fb','#ece7f2','#d0d1e6','#a6bddb','#74a9cf','#3690c0','#0570b0','#045a8d','#023858'),

		16 => array('#f7fcfd','#e5f5f9','#ccece6','#99d8c9','#66c2a4','#41ae76','#238b45','#006d2c','#00441b'),

		17 => array('#ffffd9','#edf8b0','#c7e9b4','#7fcdbb','#41b6c3','#1d91c0','#225ea8','#253494','#081d58'),

		18 => array('#fff7ec','#fee8c8','#fdd49e','#fdbb84','#fc8d59','#ef6548','#d7301f','#b30000','#7f0000'),

		19 => array('#ffffcc','#ffeda0','#fed976','#feb24c','#fd8d3c','#fc4e2a','#e31a1c','#bd0026','#b00026'),

		20 => array('#ffffe5','#fff7bc','#fee391','#fec44f','#fe9929','#ec7014','#cc4c02','#993404','#662506'),

		21 => array('#f7fcfd','#e0ecf4','#bfd3e6','#9ebcda','#8c96c6','#8c6bb1','#88419d','#810f7c','#4d004b')

    );

    private $icurrmap = array(), $icurrmap_num = -1;

    public function __construct() {
        $this->SetMap(0);
        $this->SetNumColors(64);
    }

    public function InitRGB($aRGB) {
        $this->rgb = $aRGB;        
    }
    
    public function SetMap($aMap,$aInvert=false) {
        
        if( is_array($aMap) ) {
            // Assume it is a manually specified color map
            if( $aInvert ) {
                $this->icurrmap = array_reverse($aMap);
            }
            else {
                $this->icurrmap = $aMap;
                $this->imap = -1; // Mark that this is a custom map
            }            
        }
        else {
            $this->imap = $aMap;
            $n = count($this->ipredefmaps)-1;
            if( $aMap > $n ) {
        	    JpGraphError::RaiseL(29205,$n);
        	    // 'Colormap specification out of range. Must be an integer in range [0,%d]'
            }
            if( $aInvert ) {
        	    $this->icurrmap = array_reverse($this->ipredefmaps[$this->imap]);
            }
            else {
        	    $this->icurrmap = $this->ipredefmaps[$this->imap];
            }
        }
        $this->icurrmap_num = count($this->icurrmap);
        $this->isinit = false;
    }
    
    public function GetCurrMap() {
    	return array($this->imap, $this->icurrmap);
    }
    
    public function SetRange($aMin,$aMax) {
        if( $aMin > $aMax ) {
            JpGraphError::RaiseL(29201);
            // 'Min range value must be less or equal to max range value for colormaps'
        }
        $this->irange[0] = $aMin;
        $this->irange[1] = $aMax;
        $this->irange_dist = $aMax - $aMin;
        if( $this->irange_dist <= ColorMap::EPSILON ) {
            JpGraphError::RaiseL(29202);
            // 'The distance between min and max value is too small for numerical precision'
        }
    }
    
    public function GetRange() {
        return $this->irange;
    }
    
    public function SetNumColors($aNum,$aAdjust=true) {
        $p = $this->icurrmap_num;
        if( $aAdjust ) {
        	$aNum = round( ($aNum-$p)/($p-1) )*($p-1) + $p;
        }
        $this->inumcolors = $aNum;
        $this->isinit = false;
        return $aNum;
    }
    
    public function SetNullColor($aNullColor) {
        $this->inullcolor = $aNullColor;
    }
    
    private function chk() {
        if( !$this->isinit ) 
            $this->InitBuckets();
    }
    
    public function getColor($aVal) {
        $this->chk();
    	if( is_nan($aVal) || is_null($aVal) ) {
    		return $this->inullcolor;
    	}
        if( $aVal <= $this->irange[0] ) {
            return $this->icolor_buckets[0];
        }
        if( $aVal >= $this->irange[1] ) {
            return $this->icolor_buckets[$this->inumcolors-1];
        }
        // Scale value
        $x = ($aVal - $this->irange[0]) / $this->irange_dist ;

        $bucket = floor( $x * ($this->inumcolors-1) );
        return $this->icolor_buckets[$bucket];
    }
    
    public function GetBuckets() {
		$this->chk();
        return $this->icolor_buckets;
    }
    
    private function lip($aStart,$aEnd,$aVal) {
       // Linear interpolation helper method
       if( $aStart ==  $aEnd )
            return $aStart;
        else {
            //$x = ($aVal - $aStart) / ($aEnd - $aStart);
            return $aStart + $aVal*(($aEnd - $aStart));
        }
    }
    private function InitBuckets() {
    	// First do some sanity checks since the number of buckets
    	// is to some degree controlled by the number of platoes in
    	// the color map. For example. If the map as three platoe colors
    	// the the possible number of buckets are: 3,5,7, 9, ...
    	// If the number of platoes colors are 4 the n the possible
    	// number of buckets are: 4, 7, 10, 13, ..
    	// In short the number of buckets are p + k*(n-1), k = 0, 1, 2, ,..

    	if( $this->inumcolors < $this->icurrmap_num ) {
			JpGraphError::RaiseL(29203,$this->icurrmap_num);
			// 'Number of color quantification level must be at least ',$this->icurrmap_num
    	}

    	if(  ($this->inumcolors-$this->icurrmap_num) % ($this->icurrmap_num-1) !== 0 ) {
    		JpGraphError::RaiseL(29204,$this->inumcolors, $this->icurrmap_num, $this->icurrmap_num-1);
    		// 'Number of colors (%d) is invalid for this colormap. Itm must be a number that can be written as: %d + k*%d'
    	}
        
        // Remember that the map is initialized
        $this->isinit = true;
        
        // First find out how many value we need to create between
        // the given color platou values
        $n = ($this->inumcolors - $this->icurrmap_num) / ($this->icurrmap_num - 1) + 1;

        // Now loop through all given colors and create
        // buckets by interpolating the value between two
        // consecutive colors in the map
        // The index i refers to the lower color
        $k = 0;
        $step = 1/$n;

        for( $i=0; $i < $this->icurrmap_num-1; ++$i ) {
            $rgb1 = $this->rgb->Color($this->icurrmap[$i]);
            $rgb2 = $this->rgb->Color($this->icurrmap[$i+1]);
            $v = 0 ;
            for($j=0; $j < $n; ++$j){
                $r = round($this->lip($rgb1[0],$rgb2[0],$v));
                $g = round($this->lip($rgb1[1],$rgb2[1],$v));
                $b = round($this->lip($rgb1[2],$rgb2[2],$v));
                $this->icolor_buckets[$k++] = array($r,$g,$b);
                $v += $step;
            }
        }
        // Set the last bucket to the last platoen color        
        $this->icolor_buckets[$k] = $rgb2;
    }
}


?>
