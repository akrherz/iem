#!/usr/bin/perl -w

# Load all settings and default values from config file
my %DEF;                                 # Hash table to hold settings
($CONFIG_FILE = $0) =~ s/\.cgi/.cfg/;    # Location of config file
&get_configs (\%DEF, $CONFIG_FILE) or die "Can\'t get settings from $CONFIG_FILE";

use CGI;                                 # Invoke needed library modules
use File::Basename;

$pid = $$;                               # Unique ID for suggested filenames
($ENV{'PATH'} = '/bin:/usr/bin:/usr/local/bin')
	 =~ s/\s*,\s*/:/g;   # Limit command path

# MIME-types and pixel converters for pixel ouput:
%MIME = ( jpg => 'jpeg', jpeg => 'jpeg',
      geotiff => 'tiff', gtif => 'tiff',
          tif => 'tiff', tiff => 'tiff',
          gif => 'gif',  png => 'png',
		  pnm => 'pnm', ppm => 'ppm',
		  pgm => 'pnm');
$tif_convert = "| pnmtotiff -nocolormap -packbits -rowsperstrip 1 "
     . "> /tmp/$pid && cat /tmp/$pid; rm -f /tmp/$pid";
$gtif_convert = "| pnmtotiff -nocolormap -packbits -rowsperstrip 1 > /tmp/$pid; "
     . "geotifcp -c packbits -r 1 -g /tmp/$pid.meta /tmp/$pid /tmp/$pid.tif "
     . "&& cat /tmp/$pid.tif; rm -f /tmp/$pid /tmp/$pid.meta /tmp/$pid.tif";
# Set preferred GIF converter depending on preferences
$gif_convert = ($DEF{gif_convert} =~ /quant/ ?
			  "| ppmquant -fs 256 2>/dev/null      | ppmtogif -sort "
			: "| ppmdither -red 6 -green 7 -blue 6 | ppmtogif -sort ");

%CONVERT = ('jpg'  => "| cjpeg -progressive", 'jpeg' => "| cjpeg -progressive",
			'png'  => "| pnmtopng",
			'gif'  => $gif_convert,
			'tif'  => $tif_convert, 'tiff' => $tif_convert,
			'gtif' => $gtif_convert, 'geotiff' => $gtif_convert,
			'pnm'  => '', 'ppm' => '', 'pgm' => '');

# Retrieve parameters from (lower-cased) GET/POST query string
$ENV{'QUERY_STRING'} =~ tr/A-Z/a-z/ if defined $ENV{QUERY_STRING};
$query = new CGI;

#### WMT queries ####
# OpenGIS WMT interface kicks in if a "wmtver" variable is defined.

if (defined ($wmtver = $query->param('wmtver'))) { # WMT queries
	
# Pixel size of the returned image (or in-image error message).
   	$pwidth  = $query->param('width')  || $DEF{$layer}{pwidth}
   	     || $DEF{pwidth} || 600;
   	$pheight = $query->param('height') || $DEF{$layer}{pheight}
   	     || $DEF{pheight} || 400;

# Get request type and handle "capabilities" requests right off:
	$request = $query->param('request') || 'map';

# Handle capabilities requests right away
	if ($request =~ /cap\w*s/i) {
		my @versions = sort keys %{$DEF{capabilities}};
		my $version = $versions[0];
		foreach $v (@versions) {
			last if $v gt $wmtver;
			$version = $v;
		}
		$xml_file = $DEF{capabilities}->{$version};
   		print "Content-type: text/xml\n";
   		print "Content-disposition: inline; filename=\"",
   			basename ($xml_file), "\"\n\n";
   		if (open (FILE, $xml_file)) {
   			print <FILE>;
   		}
   		else {
			print "<!-- Internal error: ",
				  "Could not open v.$version Capabilities XML file ",
   		          basename ($xml_file), ". -->\n";
		}
   		exit;
	}

# Retrieve first requested layer (ignoring all others :-)
# This is done first so as to catch any layer-specific settings

   	($layer, $ignored) = split /,/, $query->param('layers')
   		|| $DEF{def_layer} || $DEF{layers}->[0];

# Retrieve image format; sensible default
   	$format = $query->param('format') || $DEF{$layer}{'format'}
   		 || $DEF{'format'} || 'jpg';

# Retrieve exception format; sensible default
   	$except_fmt = $query->param('exception') || $DEF{$layer}{exception}
   	     || $DEF{exception} || 'inimage';

# Compute view center and size from the bounding box:
    if (defined ($bbox = $query->param('bbox'))) {
    	($gxmin, $gymin, $gxmax, $gymax) = split /,/, $bbox;
		$gwidth  = $gxmax - $gxmin;
		$gheight = $gymax - $gymin;
	} else {
    	exception ("No bounding box (bbox) specified!")
    		unless $format =~ /g(eo)*tif/i; # (GeoTIFF requires a bbox)
    }
# Infer requested zoom from bbox, width, height.
# (Pick a zoom, any zoom. This choice is less crucial now that we resample.)
   	$zoom = MAX ($gwidth/$pwidth, $gheight/$pheight);

} else {     #### Pre-WMT queries ####

   	$layer   = $query->param('layer') || $DEF{def_layer} || $DEF{layers}->[0];
   	$ctr_x   = $query->param('x0');       # View ctr. -- Might be zero
   	$ctr_x   = $DEF{$layer}{x0} unless defined $ctr_x; # Might be zero
   	$ctr_x   = $DEF{x0} unless defined $ctr_x;
   	$ctr_y   = $query->param('y0');                    # Might be zero
   	$ctr_y   = $DEF{$layer}{y0} unless defined $ctr_y; # Might be zero
   	$ctr_y   = $DEF{y0} unless defined $ctr_y;
  	$pwidth  = $query->param('pwidth')  || $DEF{$layer}{pwidth}  || $DEF{pwidth}
  		|| 600;  # Width and height in pixels
  	$pheight = $query->param('pheight') || $DEF{$layer}{pheight} || $DEF{pheight}
  		|| 400;
   	$gwidth  = $query->param('gwidth');  # Width and height in ground units
   	$gheight = $query->param('gheight'); 
   	$zoom = $query->param('zoom') || MAX($gwidth/$pwidth,$gheight/$pheight)
   		|| $DEF{$layer}{def_zoom} || $DEF{def_zoom}; # requested resolution
   	$format = $query->param('format') || $DEF{$layer}{'format'}
   		|| $DEF{'format'} || 'jpg';

# If needed, compute viewport size on the ground based on pixel size
$gwidth  = $pwidth  * $zoom unless defined $gwidth;
$gheight = $pheight * $zoom unless defined $gheight;

# Make up a bounding-box from the viewport center and size
# (WMT queries provide this up-front)
	$gxmin = $ctr_x - $gwidth  / 2;
	$gymin = $ctr_y - $gheight / 2;	
	$gxmax = $ctr_x + $gwidth  / 2; 
	$gymax = $ctr_y + $gheight / 2;
	
} # if ($wmtver)

# Optional outgoing image-processing filters to be applied:
$FIX_IMAGE = $DEF{$layer}{fix_image};
$FIX_IMAGE = $DEF{fix_image} unless defined $FIX_IMAGE;
$FIX_IMAGE = "" unless defined $FIX_IMAGE;

# Compute pixel width/height for GeoTIFF and (later) image-stretching
$xzoom = $gwidth /$pwidth;
$yzoom = $gheight/$pheight;

# If needed, build the GeoTIFF header file to be embedded
if ($format =~ /g(eo)*tif/i) {
	$COORDSYS = $DEF{$layer}{geotiff_srs} || $DEF{geotiff_srs};
	$UNITS = $DEF{$layer}{geotiff_units} || $DEF{geotiff_units} || 'Linear_Meter';
	$west_geox =  $gxmin + $xzoom/2;
	$north_geoy = $gymax - $yzoom/2;
	open(META,">/tmp/$pid.meta");
	print META <<META_END;
Geotiff_Information:
   Version: 1
   Key_Revision: 1.0
   Tagged_Information:
      ModelTiepointTag (2,3):
         0                0                0                
         $west_geox       $north_geoy      0                
      ModelPixelScaleTag (1,3):
         $xzoom           $yzoom           0                
      End_Of_Tags.
   Keyed_Information:
      GTModelTypeGeoKey (Short,1): ModelTypeProjected
      GTRasterTypeGeoKey (Short,1): RasterPixelIsArea
      ProjectedCSTypeGeoKey (Short,1): $COORDSYS
      GeogLinearUnitsGeoKey (Short,1): $UNITS
      End_Of_Keys.
   End_Of_Geotiff.
META_END
	close META;
}

# Background color
$bgcolor = $query->param('bgcolor')    || $DEF{$layer}{bgcolor}
   		|| $DEF{bgcolor} || '0xffffff'; # white by default
# "Scrub" for safer shell execution later on:
$bgcolor =~ s|[^\w#:,/.]||g; # anything that's not alphanumeric or [#:,/.])

# Fix color nomenclature as needed for ppmtogif and pnmtopng:
# Turn 0xrrggbb notation into #rrggbb (old X11-style)
	$bgcolor =~ s/^0x/\\#/ if ($bgcolor =~ /^0x.[0-9a-f]+/i);
# For pnmtopng: strip out "rgbi:" prefix and turn '/' into ',':
	if ($format eq 'png') {
		$bgcolor =~ s/^rgbi://i;
		$bgcolor =~ s|/|,|g;
	}

# Transparent GIF/PNG (same syntax for ppmtogif and pnmtopng)
$transp = $query->param('transparent') || $DEF{$layer}{transparent}
   		|| $DEF{transparent} || 'false'; # opaque by default

$CONVERT{$format} .= " -transparent $bgcolor"
	 if ($transp =~ /TRUE/i and $format =~ /gif|png/);

# Now that GeoTIFFs and transparency are possible, handle exceptions:
# Unsupported format
unless (already ([keys %CONVERT], $format)) {
	$badformat = $format;    # Fix format for inimage exception:
	$format = $DEF{$layer}{'format'} || $DEF{'format'} || 'gif';
	exception ("Unsupported format $badformat. Try",
			   uc $format, "instead.");
}

# Layer name unknown
already ($DEF{layers}, $layer) or exception ("No layer named $layer.",
	"Known layernames are:", @{$DEF{layers}});

# Requested image too large
$max_pwidth  = $DEF{$layer}{max_pwidth}  || $DEF{max_pwidth}  || 4000;
$max_pheight = $DEF{$layer}{max_pheight} || $DEF{max_pheight} || 6000;
($pwidth <= $max_pwidth) or exception ("$pwidth pixels is too wide!",
	"Try viewport widths of $max_pwidth or less.");
($pheight <= $max_pheight) or exception ("$pheight pixels is too tall!",
	"Try viewport heights of $max_pheight or less.");

# (WMT only) Retrieve style and SRS; check SRS against supported list
if (defined $wmtver) {
# Styles
   	($style, $ignored) = split /,/, $query->param('styles') || "none";
   	$FIX_IMAGE .= " | ppmtopgm" if ($style =~ /gr[ae]y/i);
# SRS
   	@srs_list = split /[^0-9]+/, ($DEF{$layer}{srs} || $DEF{srs});  # Supported SRSs
   	$srs = $query->param('srs') || $srs_list[0]; # Choose first by default
   	$srs =~ s/^EPSG://i; # Strip off EPSG: prefix if present
	already (\@srs_list, $srs) or exception ("Invalid SRS $srs.",
	    		   "Try using SRS $srs_list[0] for layer $layer.");
}

# Get pointers to "zooms" array from config file, and sort it numerically:
@zoomlist = split /[^0-9.]+/, ($DEF{$layer}{zooms} || $DEF{zooms});
@zoomlist = sort {$a <=> $b; } @zoomlist;

# Set min and max zoom levels from config file, or sensible defaults
$min_zoom = $DEF{$layer}{min_zoom};                  # Might be zero
$min_zoom = $DEF{min_zoom} unless defined $min_zoom; # Might be zero
$min_zoom = (MIN(@zoomlist) / 100) || 1 unless defined $min_zoom;
$max_zoom = $DEF{$layer}{max_zoom} || $DEF{max_zoom} || (MAX(@zoomlist) * 4);

# Check that zoom levels are reasonable:
$units = $DEF{$layer}{units} || $DEF{units};
($zoom <= $max_zoom) or 
	exception ("$zoom $units/pixel is too zoomed out for layer $layer.",
		   "Try zooming in to $max_zoom $units/pixel or less.");
($zoom >= $min_zoom) or
	exception ("$zoom $units/pixel is too zoomed in for layer $layer.",
		   "Try zooming out to $min_zoom $units/pixel or more.");

# Find the closest zoom level by iterating DOWN through the list
$zl = $#zoomlist;
$prevzoom = $zoomlist[$zl];
for ($z = $#zoomlist; $z >= 0; $z--) {
    $midpoint = sqrt ($zoomlist[$z]*$prevzoom);
    if ($zoom <= $midpoint) {$zl = $z;} else {last;}
    $prevzoom = $zoomlist[$z];
}

# Prepare to resample things between requested and available zoom levels
$build_pwidth  = MAX(int($gwidth /$zoomlist[$zl]), 1);
$build_pheight = MAX(int($gheight/$zoomlist[$zl]), 1);
$xstretch = $pwidth /$build_pwidth;
$ystretch = $pheight/$build_pheight;
$FIX_IMAGE .= "| pnmscale -xscale $xstretch -yscale $ystretch"
	if ($xstretch != 1 or $ystretch != 1);
$pwidth  = $build_pwidth;
$pheight = $build_pheight;

# OK, *now* use that zoom level to pick images etc.
$zoom = $zoomlist[$zl];

# Pick an image suffix, mosaicker, and subdirectory based on this zoom
@suffixes = split /\s*[,\s:|;]\s*/, ($DEF{$layer}{suffix} || $DEF{suffix});
$suffix   = $suffixes[MIN($zl,$#suffixes)];
$suffix = '.tif' if not defined $suffix;

@mosaickers =  split /\s*[,\s:|;]\s*/, ($DEF{$layer}{mosaicker} || $DEF{mosaicker});
$mosaicker  = $mosaickers[MIN($zl,$#mosaickers)] || 'drgtiffmosaic';

@subdirs = split /\s*[,\s:|;]\s*/, ($DEF{$layer}{subdirs} || $DEF{subdirs});
$subdir = $subdirs[MIN($zl,$#subdirs)] || "${zoom}mtif";

# Open index file for search:
$orthodb = $DEF{$layer}{'index'} || $DEF{'index'};
open (INDEX, $orthodb) or die "Can\'t open image index $orthodb !\n";

# Open a channel to the mosaicker
open (DOIT, "| $mosaicker $pwidth $pheight $bgcolor"
		  . " $FIX_IMAGE $CONVERT{$format}");

# Look for images that overlap the current viewport
$orthodir = $DEF{$layer}{orthodir} || $DEF{orthodir};

IMG: while (<INDEX>) {                    # Loop thru image records
    next if /^#/;                    # Skip lines that begin with '#'
    @rec = split /,/;                # Parse the input line 
    $topmatte    = $rec[5]; 
    $bottommatte = $rec[6]; 
    $leftmatte   = $rec[7]; 
    $rightmatte  = $rec[8];
    $res         = $rec[9];
    $im_xmin     = $rec[1] + $res * $leftmatte;
    $im_ymin     = $rec[2] + $res * $bottommatte;
    $im_xmax     = $rec[3] - $res * $rightmatte;
    $im_ymax     = $rec[4] - $res * $topmatte;

# Skip images whose footprint doesn't overlap the viewport rectangle
    next IMG unless ($im_xmin <= $gxmax and $im_xmax >= $gxmin
        and $im_ymin <= $gymax and $im_ymax >= $gymin);
	
# Get image name
	$image = $rec[0];

# Figure out the cell's geographic extent:
	$cell_xmin = MAX($gxmin, $im_xmin);
	$cell_xmax = MIN($gxmax, $im_xmax);
	$cell_ymin = MAX($gymin, $im_ymin);
	$cell_ymax = MIN($gymax, $im_ymax);
	
# Then compute the pixel-cutting parameters for this cell:
	$px = int(($cell_xmin -   $im_xmin + $res * $leftmatte) / $zoom);
	$py = int(($im_ymax   - $cell_ymax + $res * $topmatte ) / $zoom);
# (To show sub-pixels try using $pw = MAX(...,1) to force a non-zero width)
	$pw = int(($cell_xmax - $cell_xmin) / $zoom);
	$ph = int(($cell_ymax - $cell_ymin) / $zoom);
    
    next unless ($pw > 0 and $ph > 0); # Skip if zero size
    
# Compute the offsets of this cell within the viewport; complain if fishy
	$ul_x = int (($cell_xmin - $gxmin) / $zoom);
    $ul_y = int (($gymax - $cell_ymax) / $zoom);
	($xoverflow = $ul_x + $pw - $pwidth) <= 0
		or warn "Oops! $image excerpt too wide by $xoverflow pixels!\n";
	($yoverflow = $ul_y + $ph - $pheight) <= 0
		or warn "Oops! $image excerpt too tall by $yoverflow pixels!\n";

# Send a tile specification to the mosaicker
	print DOIT "$orthodir/$subdir/$image$suffix ",
				"$ul_x $ul_y $px $py $pw $ph\n";

}  # while (<INDEX>)

close (INDEX);                       # Done reading index

$|=1; 		    # Make sure MIME header arrives first
print "Content-type: image/$MIME{$format}\n\n";  # MIME header
close (DOIT); 	# Send the mosaicker off to work

exit;

#-------------------

# GET_CONFIGS -- reads user settings from config file
# Two arguments:  - a ref. to a hash table to contain settings;
#                 - the name of a config file to parse

sub get_configs {
	my ($DEF, $CONFIG_FILE) = @_;
	open (CFG, "$CONFIG_FILE") or die "No config file $CONFIG_FILE";
CFG: while (<CFG>) {
		s/^\s*//;				# Skip leading whitespace
		s/\s*\#.*$//;			# Skip everything after '#' and preceding whitespace
		next CFG if not /=/;	# Read param = value lines only
		chomp;					# Strip end-of-line if present
		my ($key, $value) = split /\s*=\s*/;  # Split on first '='
	    if ($key !~ /:/) {  # Settings that apply to *all* layers
	    	$key = lc $key;   # (Force lower-case)
			$$DEF{$key} = $value;
			if ($key =~ /^layers$/) { # Add layer names to list if needed
				foreach $l (split /\s*[,\s:|;]\s*/, $value) {
					push @{$$DEF{layers}}, $l unless already ($$DEF{layers}, $l);
				}
			}
		} else { # Layer-specific overrides
	        my @array = split /\s*:\s*/, $key;
			my $subkey = lc (pop @array); # Force lower-case
			$key =~ s/\s*:\s*$subkey$//;
			# Store each layer's params. as a sub hash table
			$$DEF{$key}{$subkey} = $value;
			# Add to layers array if necessary
	        push @{$$DEF{layers}}, $key
	        	unless (already ($$DEF{layers}, $key) or $key =~ /capabilities/);
        } # if ($key =~ /:/)
   	} # while (<CFG>)
   	1;
}

#-----------------
# EXCEPTION -- reports errors in a graphic of requested size
# Arguments are strings to be reported in the message
# Writes error message into a GIF and sends it out.
# (Later versions will write XML/HTML error output.)
sub exception {
	my ($string, $font, $pref1, $pref2);
	my @strings = @_;
	use GD;# Load up GD graphics library
    use Text::Wrap;					# Load up Text-wrap module		
	$pref1 = $pref2 = " ";      # Prefixes for wrapped text
	($except_fmt =~ /image/) or
	    push @_, "(Sorry, I only know how to do INIMAGE error messages)"
	   if $wmtver;
	
# Try gdTinyFont if gdSmallFont won't fit the URL
	$font = ($pwidth/gdSmallFont->width > (1 + length $query->url) ?
		gdSmallFont : gdTinyFont);

# Set # of columns for text-wrapping
    $Text::Wrap::columns = int($pwidth/($font->width)) - 1;

# Set starting position for text-ouput
	my ($text_x0, $text_y0) = ($font->width, 0);

# Create a new GIF array, allocate color names, and set transparency
	$im = new GD::Image($pwidth, $pheight) or die ("Failed to create error GIF");
	$white = $im->colorAllocate(255,255,255);
	$black = $im->colorAllocate(1,1,1);
	$im->transparent($white) if ($transp =~ /TRUE/i and $format =~ /gif/);

# Write URL into output image and adjust text position for next line
    $im->string($font,$text_x0, $text_y0, $query->url . ":", $black);
    $text_y += $font->height;

# Build error report from input strings
	$report = shift @strings;
	foreach $string (@strings) {$report .= " $string";}

# Split wrapped text by record-separator
	@lines = split $/, wrap ($pref1, $pref2, $report);
    
# Write each line of wrapped text into the output image
    foreach $line (@lines) {
		$im->string($font, $text_x0, $text_y, $line, $black);
	    $text_y += $font->height;  # Move one line down
    }

# Done building the output image; format it as needed
# and send it out
	binmode STDOUT; $| = 1;
	if ($format =~ /gif/i) {
	    print "Content-Type: image/gif\n\n";
		print $im->gif;
	} else {
		open (ERROR, "| /usr/local/bin/giftoppm $CONVERT{$format}");
		binmode ERROR;
		print "Content-Type: image/$MIME{$format}\n\n";
		print ERROR $im->gif;
	}
	exit;    # Exit, don't return to caller!?! Hmm...
}

# Basic utilities
#--------------------------
# ALREADY -- checks whether value already appears in a list
# Two arguments:
# - a ref. to an array to be searched
# - the scalar value to search on
sub already {
	my ($array, $entry) = @_;    # $array is a reference to an array
	my ($i, $found) = ("", 0);
	foreach $i (@$array) {
		if ($entry eq $i) { $found = 1; last;}
	}
	$found;
}

sub MIN {
  local($min) = pop;
  foreach $arg (@_) { $min = $arg if $min > $arg; }
  $min;
}
    
sub MAX {
  local($max) = pop;
  foreach $arg (@_) { $max = $arg if $max < $arg; }
  $max;
}
