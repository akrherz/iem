#!/usr/bin/perl

#------------------------------------------------------------
# Mapserver Service Information

#
# Script debug level
#
my $debug = 5;

#
# Service default image type
#
my $imagetype = "png"; # png | jpg | gif

#
# Service list 
# (name, epsg projection id, mapfile)
#
my @files = (
             "OrthoTest,26915,/mesonet/www/html/GIS/apps/ortho/test.map"
            );


#------------------------------------------------------------
# Parse the service list into associative arrays

my %map_file = ();
my %map_epsg = ();
foreach my $f ( @files ) {
  my @l = split(/,/,$f);
  $map_file{$l[0]} = $l[2];
  $map_epsg{$l[0]} = $l[1];
}


#------------------------------------------------------------
# Declare module usage and set up some objects.

$| = 1;

use POSIX qw(strftime);
use XML::Writer;
use XML::Parser;
use mapscript;

my $xml_out = new XML::Writer;
my $xml_parser = new XML::Parser(Style => 'Tree');


#------------------------------------------------------------
# Image types and extensions.

$imginfo = { "gif" => { "ms" => $mapscript::MS_GIF, "ims" => "gif", "ext" => "gif" },
             "png" => { "ms" => $mapscript::MS_PNG, "ims" => "png8", "ext" => "png" },
             "jpg" => { "ms" => $mapscript::MS_JPEG, "ims" => "jpg", "ext" => "jpg" }};


#------------------------------------------------------------
# Mapping arrays indexed on MS_* constants.

my @inchesPerUnit = (1, 12, 63360.0, 39.3701, 39370.1, 4374754);
my @visibleByStatus = ("false","true","true","false");
my @unitsByUnit = ("INCHES","FEET","MILES","METERS","KILOMETERS","DECIMAL_DEGREES");


#------------------------------------------------------------
# Read the inputs from the query URL.
# Parse the URL into an associative array.
 
my @url = split(/&/,$ENV{QUERY_STRING});
my %url_in = ();
foreach (@url) {
  s/\+/ /g;
  my ($name, $value) = split(/=/,$_);
  $name =~ s/%(..)/pack("c",hex($1))/ge;
  $value =~ s/%(..)/pack("c",hex($1))/ge;
  $name =~ tr/A-Z/a-z/;
  $url_in{$name} = $value;
}


#------------------------------------------------------------
# Return fake version and exit if client is asking for 
# version information.
 
if( $url_in{"cmd"} =~ /^getversion$/i ) {
  print "Content-type: text/plain\n\n";
  print "Build Number:235.1249\n";
  print "Version:3.0\n";
  exit;
}


#------------------------------------------------------------
# Return ping response if the client is asking for it.
 
if( $url_in{"cmd"} =~ /^ping$/i ) {
  print "Content-type: text/plain\n\n";
  print "IMS v3.0\n";
  exit;
}


#------------------------------------------------------------
# Read in the XML input file from the POST data.
# Parse the result.

my $xml_in = join("",<>);
my $xml_tree = $xml_parser->parse($xml_in);


#------------------------------------------------------------
# Check the service name
 
my $servicename = $url_in{"servicename"};


#------------------------------------------------------------
# Log the query inputs.
 
&log(1,"\n----------------------------------------");
&log(1,"Query: $ENV{QUERY_STRING}");
&log(1,"Service: $map_file{$servicename}");
&log(1,"XML: $xml_in");
&log(1,"Doc: $xml_tree");


#------------------------------------------------------------
# Response headers.
 
print "Content-type: text/plain\n\n";
print qq{<?xml version="1.0"?>};
$xml_out->startTag('ARCXML','version' => '1.0.1');

#------------------------------------------------------------
# Servicename of catalog means return ArcXML response document 
# of services, one for each map file served.

if ( $servicename eq "catalog" ) {

  $xml_out->startTag('RESPONSE');
  $xml_out->startTag('SERVICES');

  foreach my $map_name (keys %map_file) {
    $xml_out->startTag('SERVICE',
                       'NAME' => $map_name, 
                       'SERVICEGROUP' => $map_name, 
                       'ACCESS' => 'PUBLIC', 
                       'TYPE' => 'ImageServer', 
                       'DESC' => $map_name, 
                       'GROUP' => '*',
                       'STATUS' => 'ENABLED');
    $xml_out->emptyTag('XAP',
                       'NAME' => '');
    $xml_out->emptyTag('IMAGE', 
                       'URL' => '',
                       'PATH' => $map_file{$map_name},
                       'TYPE' => "JPG");
    $xml_out->endTag('SERVICE');
  }
  $xml_out->endTag('SERVICES');
  $xml_out->endTag('RESPONSE');

#------------------------------------------------------------
# This is a request to a valid service, so find out what
# kind of request and respond appropriately.

} elsif ( $map_file{$servicename} ) {
  if( getArcXMLType($xml_tree) eq "REQUEST" ) {
    my $map = new mapObj($map_file{$servicename});
    $map->{imagetype} = $imginfo->{$imagetype}->{ms};
    $map->{transparent} = $mapscript::MS_ON;
    if( getRequestType($xml_tree) eq "GET_SERVICE_INFO" ) {

      $xml_out->startTag('RESPONSE');
      $xml_out->startTag('SERVICEINFO');
      $xml_out->startTag('PROPERTIES');

      my $extent = $map->{extent};
      $extent->project($map->{projection},new projectionObj("init=epsg:" . $map_epsg{$servicename}));
      $xml_out->emptyTag('ENVELOPE', minx => $extent->{minx}, miny => $extent->{miny},
                                     maxx => $extent->{maxx}, maxy => $extent->{maxy},
                                     name => 'Initial_Extent');
      $xml_out->emptyTag('FEATURECOORDSYS', id => $map_epsg{$servicename});
      $xml_out->emptyTag('FILTERCOORDSYS', id => $map_epsg{$servicename});
      $xml_out->emptyTag('BACKGROUND', color => clrObj2Str($map->{imagecolor}));
      $xml_out->endTag('PROPERTIES');

      for( my $i = 0; $i < $map->{numlayers} ; $i++ ) {

        my $lyr = $map->getLayer($i);

        # Do not display default layers in legend
        next if $lyr->{status} == $mapscript::MS_DEFAULT;

        my @minscale = ();
        if( $lyr->{minscale} >= 0 ) {
          $minscale[0] = "minscale";
          $minscale[1] = $lyr->{minscale}/$map->{resolution}/$inchesPerUnit[$map->{units}];
        }

        @maxscale = ();
        if( $lyr->{maxscale} >= 0 ) {
          $maxscale[0] = "maxscale";
          $maxscale[1] = $lyr->{maxscale}/$map->{resolution}/$inchesPerUnit[$map->{units}];
        }

        $xml_out->startTag('LAYERINFO',
                           type => 'image',
                           name => $lyr->{name},
                           visible => $visibleByStatus[$lyr->{status}],
                           id => $i,
                           @minscale,
                           @maxscale);

        $xml_out->emptyTag('ENVELOPE',
                           minx => $extent->{minx},
                           miny => $extent->{miny},
                           maxx => $extent->{maxx},
                           maxy => $extent->{maxy});
        $xml_out->endTag('LAYERINFO');
      }
      $xml_out->endTag('SERVICEINFO');
      $xml_out->endTag('RESPONSE');
    }
    elsif( getRequestType($xml_tree) eq "GET_IMAGE" ) {
      my $properties_tree;
      getSubTree($xml_tree,\$properties_tree,"PROPERTIES");
      my $props = getChildren($properties_tree);
      my $envelope = new rectObj();
      my $featcs_id,$featcs_wkt;
      my $filtcs_id,$filtcs_wkt;
      foreach my $prop ( @{$props} ) {
        &log(1,"[" . getTag($prop). "]");
        if ( getTag($prop) eq "FEATURECOORDSYS" ) {
          $featcs_id = getAttr($prop,"id");
          $featcs_wkt = getAttr($prop,"string");
          $featcs_wkt =~ s/\"Albers\"/\"Albers_Conic_Equal_Area\"/;
        }
        elsif ( getTag($prop) eq "FILTERCOORDSYS" ) {
          $filtcs_id = getAttr($prop,"id");
          $filtcs_wkt = getAttr($prop,"string");
          $filtcs_wkt =~ s/\"Albers\"/\"Albers_Conic_Equal_Area\"/;
        }
        elsif ( getTag($prop) eq "ENVELOPE" ) {
          &log(1,"In envelope reader");
          &log(3,getAttr($prop,"minx"));
          &log(3,getAttr($prop,"miny"));
          &log(3,getAttr($prop,"maxx"));
          &log(3,getAttr($prop,"maxy"));
          $envelope->{minx} = getAttr($prop,"minx");
          $envelope->{miny} = getAttr($prop,"miny");
          $envelope->{maxx} = getAttr($prop,"maxx");
          $envelope->{maxy} = getAttr($prop,"maxy");
        }
        elsif ( getTag($prop) eq "BACKGROUND" ) {
          $map->{imagecolor} = str2ClrObj(getAttr($prop,"color"),$map->{imagecolor});
        }
        elsif ( getTag($prop) eq "IMAGESIZE" ) {
          $map->{height} = getAttr($prop,"height");
          $map->{width} = getAttr($prop,"width");
        }
        elsif ( getTag($prop) eq "OUTPUT" ) {}
        elsif ( getTag($prop) eq "LAYERLIST" ) {
          my $ldefs = getChildren($prop);
          my %lon = ();
          foreach my $ldef ( @{$ldefs} ) {
            my $id = getAttr($ldef,"id");
            &log(2,"[" . getAttr($ldef,"name") . ":" . $id . "]");
            $lon{$id} = 1;
          }
          for( my $i = 0; $i < $map->{numlayers}; $i++) {
            my $lyr = $map->getLayer($i);
            if ($lon{$i}) 
              { $lyr->{status} = $mapscript::MS_ON; }
            elsif($lyr->{status} != $mapscript::MS_DEFAULT) 
              { $lyr->{status} = $mapscript::MS_OFF; }
          }
        }
      }

      #------------------------------------------------------------
      # If there is a FEATURECOORDSYS then set the map projection
      # before drawing the map. If there is not one, set the map
      # back to the default coordinate system.
      #
      if( $featcs_id eq "0" ) {
        &log(2,"GET_IMAGE -> FEATURECOORDSYS -> ID 0");
        $map->setProjection("init=epsg:4267");
      } 
      elsif( $featcs_id ) {
        &log(2,"GET_IMAGE -> FEATURECOORDSYS -> $featcs_id");
        $map->setProjection("init=epsg:" . $featcs_id);
      }
      elsif( $featcs_wkt ) {
        &log(2,"GET_IMAGE -> FEATURECOORDSYS -> $featcs_wkt");
        $map->setWKTProjection($featcs_wkt);
      }
      else {
        &log(2,"GET_IMAGE -> FEATURECOORDSYS -> DEFAULT");
        $map->setProjection("init=epsg:" . $map_epsg{$servicename});
      }
 
      #------------------------------------------------------------
      # If there is a FILTERCOORDSYS then project the map extent
      # to the FEATURECOORDSYS before setting the map extent.  
      #
      log_envelope(2,$envelope);
      if( $filtcs_id eq "0" ) {
        # Hypothesis : id == 0 implies use the feature coordinate system
        # so we do nothing here
        &log(2,"GET_IMAGE -> FILTERCOORDSYS -> ID 0");
      } 
      elsif( $filtcs_id ) {
        &log(2,"GET_IMAGE -> FILTERCOORDSYS -> $filtcs_id");
        $envelope->project(new projectionObj("init=epsg:" . $filtcs_id),$map->{projection});
      }
      elsif( $filtcs_wkt ) {
        &log(2,"GET_IMAGE -> FILTERCOORDSYS -> $filtcs_wkt");
        my $l = new layerObj($map);
        $l->setWKTProjection($filtcs_wkt);
        $envelope->project($l->{projection},$map->{projection});
      }
      else {
        &log(2,"GET_IMAGE -> FILTERCOORDSYS -> DEFAULT");
        $envelope->project(new projectionObj("init=epsg:" . $map_epsg{$servicename}),$map->{projection});
      }
      log_envelope(2,$envelope);

      #------------------------------------------------------------
      # Once the FEATURECOORDSYS is set and the extent projected
      # to the FEATURECOORDSYS we can set the map extent.
      #
      if( $envelope ) {
        $map->{extent} = $envelope;
      } 
      else {
        &log(1,"CRITICAL FAILURE : No Envelope");
      }

      my $img = $map->draw();
      my $filename = $map->{name} . "-" . $$ . "." . $imginfo->{$imagetype}->{ext};
      my $svstatus = mapscript::msSaveImage($img,$map->{web}->{imagepath} . $filename,$map->{imagetype},$map->{transparent},$map->{interlace},$map->{imagequality});
 
      $xml_out->startTag('RESPONSE');
      $xml_out->startTag('IMAGE');
      $xml_out->emptyTag('ENVELOPE',
                         minx => $map->{extent}->{minx},
                         miny => $map->{extent}->{miny},
                         maxx => $map->{extent}->{maxx},
                         maxy => $map->{extent}->{maxy});
      $xml_out->emptyTag('OUTPUT',
                         file => $map->{web}->{imagepath} . $filename,
                         type => $imginfo->{$imagetype}->{ims},
                         url => $map->{web}->{imageurl} . $filename);
      $xml_out->endTag('IMAGE');
      $xml_out->endTag('RESPONSE');
    }
  } 

#------------------------------------------------------------
# This request is for a servicename we do not serve. Return
# an error here.

} else {

  # TO BE DONE

}

$xml_out->endTag('ARCXML');
$xml_out->end();

#------------------------------------------------------------
# SUBROUTINES

#------------------------------------------------------------
# Log an info message

sub log {
  my $loglevel = shift;
  my $logmessage = shift;
  my $logtime = strftime "%H:%M:%S",localtime;
  print STDERR " " x $loglevel,"\[$logtime\] $logmessage\n" if $loglevel <= $debug;
}

sub log_envelope {
  my $loglevel = shift;
  my $logenv = shift;
  my $logtime = strftime "%H:%M:%S",localtime;
  print STDERR "\[$logtime\] ((" . $logenv->{minx} . "," . $logenv->{miny} .
               "),(" . $logenv->{maxx} . "," . $logenv->{maxy} . "))\n" if $loglevel <= $debug;
}

#------------------------------------------------------------
# Search a tree at level one for a particular tag

sub findTag {
  my $tree = shift;
  my $tag = shift;
  my $rt;
  for( my $i = 1; $i < @{$tree->[1]}; $i += 2 ) {
    if( $tree->[1]->[$i] =~ /^$tag$/i ) {
      $rt = [$tree->[1]->[$i],$tree->[1]->[$i+1]];
      last;
    }
  }
  $rt;
}

#------------------------------------------------------------
# Return the attribute value of root level tag

sub getAttr {
  my $tree = shift;
  my $tag = shift;
  $tree->[1]->[0]->{$tag};
}

sub getAttrs {
  my $tree = shift;
  $tree->[1]->[0];
}

#------------------------------------------------------------
# Get the tag name of a tree

sub getTag {
  my $tree = shift;
  $tree->[0];
}

#------------------------------------------------------------
# Search a tree at level one for all tags with same name

sub getChildren {
  my $tree = shift;
  my $rt = [];
  for( my $i = 1; $i < @{$tree->[1]}; $i += 2 ) {
    push(@{$rt},[$tree->[1]->[$i],$tree->[1]->[$i+1]]);
  }
  $rt;
}

#------------------------------------------------------------
# Extract an arbitrary subtree with a particular tag header

sub getSubTree {
  my $tree = shift;  # Input tree to walk through
  my $ref = shift;   # Scalar reference of var to store result
  my $tag = shift;   # Tag to search for
  my $rt;
  if ($tree->[0] =~ /^$tag$/i ) {
    ${$ref} = $tree;
    $rt = $tree;
  } else {
    for( my $i = 1; $i < @{$tree->[1]}; $i += 2 ) {
      last if getSubTree([$tree->[1]->[$i],$tree->[1]->[$i+1]],$ref,$tag);
    }
  }
  $rt;
}

#------------------------------------------------------------
# What kind of packet is this? REQUEST/RESPONSE/CONFIG

sub getArcXMLType {
  my $tree = shift;
  uc($tree->[1]->[1]);
} 
  
#------------------------------------------------------------
# What kind of REQUEST is this? GET_SERVICE_INFO/GET_IMAGE

sub getRequestType {
  my $tree = shift;
  uc($tree->[1]->[2]->[1]);
} 

sub getRequestInfo {
  my $tree = shift;
  uc($tree->[1]->[2]->[1]);
} 

#------------------------------------------------------------
# What kind of REQUEST is this? GET_SERVICE_INFO/GET_IMAGE

sub clrObj2Str {
  my $clrObj = shift;
  return $clrObj->{red} . "," . $clrObj->{green} . "," . $clrObj->{blue};
}

sub str2ClrObj {
  my $str = shift;
  my $clrObj = shift;
  my ($r,$g,$b) = split(/,/,$str);
  $clrObj->{red} = $r;
  $clrObj->{green} = $g;
  $clrObj->{blue} = $b;
  return $clrObj;
}

