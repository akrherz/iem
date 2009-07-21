<?php
/*=======================================================================
 // File:  		 JPGRAPH_PLOTLINE.PHP
 // Description: PlotLine extension for JpGraph
 // Created:  	 2009-03-24
 // Ver:  		 $Id: jpgraph_plotline.php 1148 2009-03-24 21:55:44Z ljp $
 //
 // CLASS PlotLine
 // Data container class to hold properties for a static
 // line that is drawn directly in the plot area.
 // Useful to add static borders inside a plot to show for example set-values
 //
 // Copyright (c) Aditus Consulting. All rights reserved.
 //========================================================================
 */

class PlotLine {
    public $scaleposition, $direction=-1;
    protected $weight=1;
    protected $color = 'black';
    private $legend='',$hidelegend=false, $legendcsimtarget='', $legendcsimalt='',$legendcsimwintarget='';
    private $iLineStyle='solid';

    function __construct($aDir=HORIZONTAL,$aPos=0,$aColor='black',$aWeight=1) {
        $this->direction = $aDir;
        $this->color=$aColor;
        $this->weight=$aWeight;
        $this->scaleposition=$aPos;
    }

    function SetLegend($aLegend,$aCSIM='',$aCSIMAlt='',$aCSIMWinTarget='') {
        $this->legend = $aLegend;
        $this->legendcsimtarget = $aCSIM;
        $this->legendcsimwintarget = $aCSIMWinTarget;
        $this->legendcsimalt = $aCSIMAlt;
    }

    function HideLegend($f=true) {
        $this->hidelegend = $f;
    }

    function SetPosition($aScalePosition) {
        $this->scaleposition=$aScalePosition;
    }

    function SetDirection($aDir) {
        $this->direction = $aDir;
    }

    function SetColor($aColor) {
        $this->color=$aColor;
    }

    function SetWeight($aWeight) {
        $this->weight=$aWeight;
    }

    function SetLineStyle($aStyle) {
        $this->iLineStyle = $aStyle;
    }

    //---------------
    // PRIVATE METHODS

    function DoLegend(&$graph) {
        if( !$this->hidelegend ) $this->Legend($graph);
    }

    // Framework function the chance for each plot class to set a legend
    function Legend(&$aGraph) {
        if( $this->legend != '' ) {
            $dummyPlotMark = new PlotMark();
            $lineStyle = 1;
            $aGraph->legend->Add($this->legend,$this->color,$dummyPlotMark,$lineStyle,
            $this->legendcsimtarget,$this->legendcsimalt,$this->legendcsimwintarget);
        }
    }

    function PreStrokeAdjust($aGraph) {
        // Nothing to do
    }

    function Stroke($aImg,$aXScale,$aYScale) {
        $aImg->SetColor($this->color);
        $aImg->SetLineWeight($this->weight);
        $oldStyle = $aImg->SetLineStyle($this->iLineStyle);
        if( $this->direction == VERTICAL ) {
            $ymin_abs=$aYScale->Translate($aYScale->GetMinVal());
            $ymax_abs=$aYScale->Translate($aYScale->GetMaxVal());
            $xpos_abs=$aXScale->Translate($this->scaleposition);
            $aImg->StyleLine($xpos_abs, $ymin_abs, $xpos_abs, $ymax_abs);
        }
        elseif( $this->direction == HORIZONTAL ) {
            $xmin_abs=$aXScale->Translate($aXScale->GetMinVal());
            $xmax_abs=$aXScale->Translate($aXScale->GetMaxVal());
            $ypos_abs=$aYScale->Translate($this->scaleposition);
            $aImg->StyleLine($xmin_abs, $ypos_abs, $xmax_abs, $ypos_abs);
        }
        else {
            JpGraphError::RaiseL(25125);//(" Illegal direction for static line");
        }
        $aImg->SetLineStyle($oldStyle);
    }
}


?>