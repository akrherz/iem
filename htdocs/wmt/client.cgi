#!/usr/bin/perl
# Copyright (c) 1997 Massachusetts Institute of Technology.
# All rights reserved.
#
# Perl script for browsing Digital Orthophotos.
# Major Revision History:
# April 1996:      Initial csh version up, using pre-tiled images. (John Evans)
# Aug/Sep 1996:    "Seamless" views, using a new pnmcut; image downloads. (John Evans)
# Feb/Apr 1997:    GeoTIFF support (Andrew Wheeler) and CGI library.
# April 1998:      Image lookups in a database (Dan Martin and John Evans)
# Summer 1998:     Facelift and <table>-based seamless viewport (Pam Mukerji)
# July, 1998:      Dynamic overviews and "you are here" (Nii Lartey Dodoo)
# October, 1998:   Truly seamless views w/ multi_tiffcut and then tiffmosaic.c

##### User-selectable options ##################################
# Check these two settings - else the client might not work
$WMTVER = '0.9';   # Default WMT interface version number
                   # (Set to nothing for "classic" MITortho interface)
@ZOOMLEVELS = (0.5, 1, 2, 5, 10, 20, 50, 100, 200); # Valid zoom levels
%LAYERS = ('DMX' => 'Des Moines Base Reflectivity');
%SERVER = ('iem'     => 'http://mesonet.agron.iastate.edu/wmt/server.cgi');

# Make sure the Web page displays the right coordinate system
$COORD_SYS = "Mass. State Plane meters, Mainland Zone, NAD83";

# Specify the client's default image request
$DEF_X0=241500;        # Center of default view: easting...
$DEF_Y0=908500;        # ... and northing
$DEF_ZOOMLEVEL = 200;  # Default zoom level (screen:image pixels);
$DEF_PWIDTH=400;       # Default viewport: width & height
$DEF_PHEIGHT=300;      # in pixels, and in meters on the ground

# This setting can be safely ignored
$OVERLAP = 5;          # Percent overlap when going N, S, E, W

##### End user-selectable options ############################

# Initialize a CGI structure
use CGI;
use File::Basename;
$query = new CGI;
$form_preamble = $query->startform(-method=>GET, -action=>"$SCRIPT");
$SCRIPT=basename($0); # Stash this script's name for self-reference later
                      # (Dir. path is relative to the Web-root)


# Initialize form variables.
# Check for debug flag (verbose output) first:
if ($debug = $query->param('debug')) {
    $|=1;                          # Make sure diagnostics go out in sync
    print $query->header;          # Send out HTTP header early
# Make this setting stick through the remainder of the session
    $debugvar = "<input name=debug type=hidden value=1>";
} else {$debugvar='';}

# Set a session-id which persists through successive queries.
# (Not used at present)
# $sessionid = $query->param('uid') || $$;

# Set WMT-inteface version number:
$wmtver = $query->param('wmtver') || $WMTVER;

# Get the requested data layer (Wasn't used previously)
$layer = $query->param('layer') ||  'mainland';

# Zoom level (screen:image pixels); sensible default
$zoom = $query->param('zoom') || $DEF_ZOOMLEVEL;

# Find closest image-pyramid level ($zl) if in-between:
$zl = $#ZOOMLEVELS; $prevzoom = $ZOOMLEVELS[$zl];
for ($z = $#ZOOMLEVELS; $z >= 0; $z--) {
    $midpoint = sqrt ($ZOOMLEVELS[$z]*$prevzoom);
    if ($zoom <= $midpoint) {$zl = $z;} else {last;}
    $prevzoom = $ZOOMLEVELS[$z];
}
$debug && print "Zoom: $zoom m/pixel; nearest level is $zl -> $ZOOMLEVELS[$zl] m/pixel.<br>\n";
# But don't "snap" the actual zoom level to that one

# Desired action:
$action = $query->param('action') || "nop";	# default is "Nop"

# Viewport width & height in pixels on screen:
$pwidth  = $query->param('pwidth')  || $DEF_PWIDTH;
$pheight = $query->param('pheight') || $DEF_PHEIGHT;

# Center of current view (in geographic coordinates):
$x0 = $query->param('x0') || $DEF_X0;
$y0 = $query->param('y0') || $DEF_Y0;

$debug && print "zoom=$zoom, view center (x=$x0, y=$y0),",
#		"layer=$layer,"
		"width=$pwidth, height=$pheight, action=$action<br>";

#------------------------------------------------------------------
# Based on the action specified, determine the next image's
# geographic coordinates:
#------------------------------------------------------------------

# First, treat actions that use a mouseclick
if ($action eq "pan" or $action =~ /^zoom/) {
# Recenter view on mouseclick (x,y) (default is middle of viewport):
   $xclick = $query->param('x') || $pwidth/2;
   $yclick = $query->param('y') || $pheight/2;
   $debug && print "<br>zoom=$zoom, (nearest level is $ZOOMLEVELS[$zl]). ",
   	"You clicked on $xclick, $yclick to recenter at ";
   $x0 = int ($x0 - $zoom * ($pwidth/2  - $xclick));
   $y0 = int ($y0 + $zoom * ($pheight/2 - $yclick));
      $debug && print "($x0, $y0) in geographic coordinates; ";
}

if ($action =~ /^zoom/) {
   ($whereto = $action) =~ s/^zoom//;   # parse out "zoom" prefix
   $debug && print "whereto=$whereto; ";
   if ($whereto eq "in") {
      $debug && print "Zooming IN  from zoom level $zl -> $zoom m pixels ";
      if ($zoom > $ZOOMLEVELS[0]) {
      	$zl-- if $zoom <= $ZOOMLEVELS[$zl];
      	$zoom = $ZOOMLEVELS[$zl];
      }
      if ($zoom > $ZOOMLEVELS[0]) { $zichecked = "CHECKED"; } 
      else { $rcchecked = "CHECKED"; }
   }
   elsif ($whereto eq "out") {
      $debug && print "Zooming OUT from zoom level $zl -> $zoom  m pixels ";
      if ($zoom <= $ZOOMLEVELS[$#ZOOMLEVELS]) {
        $zl++ if ($zoom >= $ZOOMLEVELS[$zl]);
      	$zoom = $ZOOMLEVELS[$zl];
      }
      if ($zoom <= $ZOOMLEVELS[$#ZOOMLEVELS]) { $zochecked = "CHECKED"; }
      else { $rcchecked = "CHECKED"; }
   }
   else {                             # "zoom50", "zoom20", etc.   
      $debug && print "whereto=$whereto; ";
      $debug && print "Zooming directly from zoom level $zl -> $zoom  m pixels ";
      $zl = 0;
      for ($z = $#ZOOMLEVELS; $z >= 0; $z--) {
      	$zl = $z if $whereto <= $ZOOMLEVELS[$z];
      }
      $zoom = $ZOOMLEVELS[$zl];
      $rcchecked = "CHECKED";
   }   # Done with zoom actions
   $debug && print "to zoom level $zl -> $zoom m pixels.<br>\n";
} else {
   $rcchecked = "CHECKED";     # Recenter is default next action
}

# Switching layers: parse out "layer" prefix
if ($action =~ /^layer/) {
	($layer = $action) =~ s/^layer//;
}

# This if() clause covers lateral movements w/o a mouseclick:
if  ($action =~ /^north/ or $action =~ /^south/
  or $action =~ /east$/ or $action =~ /west$/ ) {
   $lateral = 1; $debug && print "Going ";
}

if ($action =~ /^north/ ) {                   # N, NE, NW
  $deltay = 1;  $debug && print "North";     
}
elsif ($action =~ /^south/ ) {                # S, SW, SW
  $deltay = -1; $debug && print "South";
}
if ($action =~ /east$/ ) {                    # E, NE, SE
  $deltax = 1;  $debug && print "East";
}
elsif ($action =~ /west$/ ) {                 # W, NW, SW
  $deltax = -1; $debug && print "West";
}
if  ($lateral) {
   $debug && print ": resetting (x0, y0) to ";
   $x0 = $x0 + $deltax * (1 - $OVERLAP/100)*$pwidth*$zoom;
   $y0 = $y0 + $deltay * (1 - $OVERLAP/100)*$pheight*$zoom;
   $debug && print "{$x0, $y0).<br>\n";
}

# Viewport width and height, in geographic units (e.g. meters):
$gwidth  = $pwidth  * $zoom;
$gheight = $pheight * $zoom;

###### Store state string (no $action); it gets used a lot here.
$state = "zoom=${zoom}&x0=${x0}&y0=${y0}&gwidth=${gwidth}&gheight=${gheight}"
  . "&pwidth=${pwidth}&pheight=${pheight}&layer=$layer";
$state .= "&debug=${debug}" if $debug;

# Set Query-String for map server
# OGC-WMT 0.0.1 server interface kicks in on non-blank 'wmtver'
if ($wmtver) { 
	@bbox = ($x0-$gwidth/2, $y0-$gheight/2,
	           $x0+$gwidth/2, $y0+$gheight/2);
	$imgrequest = "wmtver=$wmtver&request=map"
	            . "&bbox=$bbox[0],$bbox[1],$bbox[2],$bbox[3]"
	            . "&width=$pwidth&height=$pheight&layers=$layer";
	$state .= "&wmtver=$wmtver"; # Carry version ID along
} else { # "Classic" interface x0,y0,width,height,zoom
    $imgrequest = $state;
}

@directions = ("north", "south", "east", "west",
               "northeast", "northwest", "southeast", "southwest");

foreach $dir (@directions) {
   $link{$dir} = "<a href=\"${SCRIPT}?action=$dir&$state\">";
   $get{$dir} = $link{$dir}
          . "<img src=\"${dir}_hand.gif\" Alt=\"$dir\" border=\"0\"></a>";
}

# Put an asterisk next to current zoom level and layer name
${'zoom'.$zoom.'_selected'}   = "<FONT color=\"red\"><B>*</B></FONT>";
${'layer'.$layer.'_selected'} = "<FONT color=\"green\"><B>*</B></FONT>";

# "Zoom in" radio button (if not zoomed in all the way):
$zoomin  = "<input type=radio name=\"action\" value=\"zoomin\" $zichecked>"
   . " Zoom IN <br>" if ($zoom > $ZOOMLEVELS[0]);

# "Zoom out" radio button (if not zoomed out all the way):
$zoomout = "<input type=radio name=\"action\" value=zoomout $zochecked>"
   . " Zoom OUT <br>" if ($zoom < $ZOOMLEVELS[$#ZOOMLEVELS]);

$debug && print "New zoom=$zoom, xclick=$xclick, yclick=$yclick,",
  "x0=$x0, y0=$y0, pwidth=$pwidth, pheight=$pheight, gwidth=$gwidth,",
  "gheight=$gheight<br>\n";

# OK, now dump the form to stdout for the browser.
#------------------------------------------------------------------
print $query->header unless $debug;    # If debug, we already did this around line 50
print <<EndForm1;
<HTML><HEAD>
<TITLE>MIT/NRCS DOQ Server: $zoom m/pixel, center (x,y)=($x0,$y0)</TITLE>
</HEAD>
<BODY BGCOLOR=#ffffff>
<font size="+2">MIT/NRCS DOQ server: $zoom m/pixel, center (x,y) = ($x0,$y0)</font>
$form_preamble
<input name=zoom    value=$zoom    type=hidden>
<input name=x0 value=$x0 type=hidden  size=5>
<input name=y0 value=$y0 type=hidden size=5>			
<input name=layer value=$layer type=hidden>
$debugvar
<!--
<table align=CENTER><tr>
<td><a href="index.html">Project homepage</a></td>

<td><a href="metadata.cgi?$state">FGDC metadata</a></td>

<td><a href="download.cgi?$imgrequest">Download options</a></td>
</tr></table>
-->
<table><tr valign=top><td>
<TABLE border=1 CELLSPACING=0 width=60 height=40 BGCOLOR=#eeeeee>
  <tr align=center>
    <td><FONT FACE="Helvetica"
         SIZE="-2">$link{'northwest'}<b>NW</b></a></font></td>
    <td><FONT FACE="Helvetica"
         SIZE="-2">$link{'north'}<b>N</b></a></font></td>
    <td><FONT FACE="Helvetica"
         SIZE="-2">$link{'northeast'}<b>NE</b></a></font></td>
  </tr><tr align=center>
    <td><FONT FACE="Helvetica"
         SIZE="-2">$link{'west'}<b>W</b></a></font></td>
    <td><FONT FACE="Helvetica"
         SIZE="-2">&nbsp;</font></td>
    <td><FONT FACE="Helvetica"
         SIZE="-2">$link{'east'}<b>E</b></a></font></td>
  </tr><tr align=center>
    <td><FONT FACE="Helvetica"
         SIZE="-2">$link{'southwest'}<b>SW</b></a></font></td>
    <td><FONT FACE="Helvetica"
         SIZE="-2">$link{'south'}<b>S</b></a></font></td>
    <td><FONT FACE="Helvetica"
         SIZE="-2">$link{'southeast'}<b>SE</b></a></font></td>
  </tr>
</TABLE>
<hr>
<b><FONT SIZE="-1">
Click on the image to<br></font></b>
<FONT FACE="Helvetica" SIZE="-2">
<input type="radio" name="action" value="pan" $rcchecked>Recenter image<br>   
$zoomin
$zoomout</font>
<FONT SIZE="-1"><b>
or to set a scale of<br></b></font>
<FONT FACE="Helvetica" SIZE="-2">
EndForm1

############## Radio buttons for zoom levels
foreach $z (reverse @ZOOMLEVELS) {
	print "<INPUT TYPE=\"radio\" NAME=\"action\" VALUE=zoom$z>"
	 . " ${z}m pixels "
	 . " ${'zoom'.${z}.'_selected'}<br>\n";
}
print '(<FONT color="red"><B>*</B></FONT> Current zoom level)<hr>';
# ... and for layer names
foreach $l (keys %LAYERS) {
	print '<INPUT TYPE="radio" NAME="action"' . " VALUE=layer$l>"
	 . " $LAYERS{$l} ${'layer'.${l}.'_selected'}<br>\n";
}

############## ... and back to the here-document
print <<EndForm2;
(<FONT color=\"green\"><B>*</B></FONT> Current layer)<br>
</font>
<hr>
<table><tr align=right valign=bottom>
  <td><b><FONT FACE="Helvetica" SIZE="-2">View Width:<br>
     <input name=pwidth value=$pwidth size=5></font><br>
      <FONT FACE="Helvetica" SIZE="-3">pixels</font></b></td>
  <td><b><FONT FACE="Helvetica" SIZE="-2">Height:<br>
     <input name=pheight value=$pheight size=5><br>
       <FONT FACE="Helvetica" SIZE="-3">pixels</font></font></b></td>
</tr></table>
<FONT FACE="Helvetica" SIZE="-2">
<INPUT TYPE="submit" VALUE="Submit Changes"><br>
</font>
</td><td><TABLE BORDER=0 CELLSPACING=0>
   <tr>
     <TD>$get{'northwest'}</TD>
     <TD align=center>$get{'north'}<br></td>
     <TD>$get{'northeast'}</TD>
   </tr><tr>
     <td align="left" valign="center">$get{'west'}</td>
     <td align=center><input type=image src="$SERVER{$layer}/$$.jpg?$imgrequest"
            width="$pwidth" height="$pheight" align="middle"></td>
     <td align="right" valign="center">$get{'east'}<br></td>
   </tr><tr>
     <TD>$get{'southwest'}</TD>
     <TD align=center>$get{'south'}<br></TD>
     <TD>$get{'southeast'}</TD>
    </tr><tr>
     <td COLSPAN=3 align="right"><img src="scalebar$ZOOMLEVELS[$zl].gif"></td></tr>
  </TABLE>
</TD></TR></TABLE>
</form>
<HR>
The viewport above measures width=$gwidth and height=$gheight meters on
the ground. Each pixel you see measures <strong>${zoom}x${zoom}</strong>
meters. The viewport is centered on X=<strong>$x0</strong>,
Y=<strong>$y0</strong> ($COORD_SYS).
<HR SIZE=2>
Copyright &copy; 1999 Massachusetts Institute of Technology.<br>
</CENTER></body></html>
EndForm2

# MAX and MIN don't exist in perl; here they are as subroutines:
sub MAX {  local($max) = pop(@_);
  foreach $element (@_) { $max = $element if $max < $element; }
  $max; }
sub MIN {  local($min) = pop(@_);
  foreach $element (@_) { $min = $element if $min > $element; }
  $min; }
