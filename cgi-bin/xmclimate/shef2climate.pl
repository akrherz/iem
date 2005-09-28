#!/usr/local/bin/perl
##########################################################
#
# shef2climate.pl - perl script that updates decodes shef 
#                   and updates and xmclimate data file
# Author:	Carl Dierking 
######################### Main ############################
################ Decode Shef Message ######################
#
$climDataDir = "/data/climdata";
$climUtlDir  = "/apps/xmclimate/bin";
#
# assign an associated array with values that set the proper bits
$WX{smoke} = 1;      # bit 1
$WX{haze} = 1;       # bit 1
$WX{fog} = 2;        # bit 2
$WX{drizzle} = 8;    # bit 4
$WX{ice} = 16;       # bit 5
$WX{glaze} = 32;     # bit 6
$WX{thunder} = 64;   # bit 7
$WX{hail} = 128;     # bit 8
$WX{dust} = 256;     # bit 9
$WX{sand} = 256;     # bit 9
$WX{blowsnow} = 512; # bit 10
$WX{wind} = 1024;    # bit 11
$WX{tornado} = 2048; # bit 12
$WX{rain} = 4096;    # bit 13
$WX{snow} = 8192;    # bit 14
#
# open a file if a pathname was given at the command line
if ( $#ARGV < 0) {
   print "No filename! exiting...\n";
   exit 1;
}
open(INFILE, "< $ARGV[0]")
   or die "Unable to open file: $ARGV[0] ... $!\n";

$distribData = 1;   #  If not distributing data via LDM set this to 0
$newData = 0;       #  If new data has been detected this will be set to 1


&init_hash;
while (<INFILE>) {
   chomp($_);
   @dataline = split(/\//, $_);
   foreach $segment ( @dataline ) {
      @codes = split(/ /, $segment);
      if ($codes[0] =~ /\.A1/) {
         if (defined($SHEFOB{$codes[1]})) {
	     if ($codes[1] =~ /XW/) {
		$SHEFOB{WXCODE} |= convertWxCodes($codes[2]);
	     }
	     $SHEFOB{$codes[1]} = $codes[2];
         }
      } elsif ($codes[0] =~ /\.A/) {
         &init_hash;
         $SHEFOB{STN} = $codes[1];
  	 $SHEFOB{MONTH} = int($codes[2] / 100);
  	 $SHEFOB{DAY} = int($codes[2] - ($SHEFOB{MONTH} * 100));
	 if ( $codes[3] eq "L") {
	   printf "Local time: $codes[4]\n";
	 } else {
	   printf "GMT time: $codes[3]\n";
	 }
      } else {
         if (defined($SHEFOB{$codes[0]})) {
	     if ($codes[0] =~ /XW/) {
		$SHEFOB{WXCODE} |= convertWxCodes($codes[1]);
	     }
	     $SHEFOB{$codes[0]} = $codes[1];
         }
      }
   }
   if ($_ =~ /\.A/) {
	&write_data;
   }
}

exit;

##############  subroutines   ############################

sub init_hash {

# read all the given variables and assign them to an associated list
$SHEFOB{STN} = "M";
$SHEFOB{MONTH} = "M";
$SHEFOB{DAY} = "M";
$SHEFOB{YEAR} = "M";
$SHEFOB{PPD} = "M";
$SHEFOB{PPP} = "M";
$SHEFOB{PP} = "M";
$SHEFOB{TX} = "M";
$SHEFOB{TA} = "M";
$SHEFOB{TN} = "M";
$SHEFOB{SF} = "0";
$SHEFOB{SD} = "0";
$SHEFOB{UR} = "M";
$SHEFOB{UP} = "M";
$SHEFOB{XW} = "M";
$SHEFOB{XWD} = "M";
$SHEFOB{WXCODE} = "0";
#
}


sub write_data {
############# QC data and write to the netCDF file ###############
#
$TEMPLOW = -100;
$TEMPHI  = 150;
$PCPNHI  = 25;
$SNOWHI  = 50;
$SNWDHI  = 500;
$WINDHI  = 200;

#  Check for a valid station ID and build path to data file
if ($SHEFOB{STN} ne "M") {
   $blank = "_____";
   $offset = length($SHEFOB{STN});
   $SHEFOB{STN} =  $SHEFOB{STN} . substr($blank, $offset);
   $climFile = "O0CL" . $SHEFOB{STN} . "00000";
#   $climFile = "O0CL" . substr($blank, $offset) . $SHEFOB{STN} . "00000";
#   print "File path: $climDataDir/$climFile\n";
} else {
   print "Error: No station ID!\n";
   exit 1;
}
#
#  Make sure the date is valid
if ($SHEFOB{MONTH} ne "M" && $SHEFOB{DAY} ne "M") {
   if ($SHEFOB{MONTH} < 1 || $SHEFOB{MONTH} > 12 ) {
      print "Error: Month = $SHEFOB{MONTH}\n";
      exit 1;
   }
   if ($SHEFOB{DAY} < 1 || $SHEFOB{DAY} > 31 ) {
      print "Error: Day = $SHEFOB{DAY}\n";
      exit 1;
   }
   $curmonth = `date +%m`;
   $curday = `date +%d`;
   $SHEFOB{YEAR} = `date +%Y`;
   chomp($SHEFOB{YEAR});
   if ($SHEFOB{MONTH} > $curmonth) {
      --$SHEFOB{YEAR};
   } elsif ($SHEFOB{MONTH} == $curmonth && $SHEFOB{DAY} > $curday) {
      --$SHEFOB{YEAR};
   }
} else {
  print "No date in message!\n";
  exit 1;
}
# 
# Got station ID and date information, so check each data value, 
# and if it passes, enter it individually 
# 
# Check Maximum Temperature and write it to the file
if ($SHEFOB{TX} =~ /[0-9.-]+/) {
  if ($SHEFOB{TX} < $TEMPLOW || $SHEFOB{TX} > $TEMPHI) {
     print "Error: Max Temperature out of range!\n";
     $SHEFOB{TX} = "M";
  } else {
     print "$climUtlDir/climWrite -stn $SHEFOB{STN} -ddir $climDataDir";
     print " -y $SHEFOB{YEAR} -m $SHEFOB{MONTH} -a $SHEFOB{DAY}";
     print " -v maxt -d $SHEFOB{TX}\n";
     $resultStr = `$climUtlDir/climWrite -stn $SHEFOB{STN} -ddir $climDataDir -y $SHEFOB{YEAR} -m $SHEFOB{MONTH} -a $SHEFOB{DAY} -v maxt -d $SHEFOB{TX}`;
     print "$resultStr\n";
     $newData = 1;
  }
} else {
  $SHEFOB{TX} = "M";
}
#
# Check Minimum Temperature and write it to the file
if ($SHEFOB{TN} =~ /[0-9.-]+/) {
  if ($SHEFOB{TN} < $TEMPLOW || $SHEFOB{TN} > $TEMPHI) {
     print "Error: Min Temperature out of range!\n";
     $SHEFOB{TN} = "M";
  } else {
     print "$climUtlDir/climWrite -stn $SHEFOB{STN} -ddir $climDataDir";
     print " -y $SHEFOB{YEAR} -m $SHEFOB{MONTH} -a $SHEFOB{DAY}";
     print " -v mint -d $SHEFOB{TN}\n";
     $resultStr = `$climUtlDir/climWrite -stn $SHEFOB{STN} -ddir $climDataDir -y $SHEFOB{YEAR} -m $SHEFOB{MONTH} -a $SHEFOB{DAY} -v mint -d $SHEFOB{TN}`;
     print "$resultStr\n"; 
     $newData = 1;
  }
} else {
  $SHEFOB{TN} = "M";
}
################## Load Precip #####################
if ($SHEFOB{PP} eq "M" && $SHEFOB{PPD} ne "M") {
   $SHEFOB{PP} = $SHEFOB{PPD};
}
if ($SHEFOB{PP} eq "M" && $SHEFOB{PPP} ne "M") {
   $SHEFOB{PP} = $SHEFOB{PPP};
}
if ($SHEFOB{PP} =~ /[0-9.-T]+/) {
  if ($SHEFOB{PP} ne "T" && $SHEFOB{PP} < 0) {
     print "Error: negative pcpn value!\n";
     $SHEFOB{PP} = "M";
  } elsif ($SHEFOB{PP} ne "T" && $SHEFOB{PP} > $PCPNHI) {
     print "Error: Precip of range!\n";
     $SHEFOB{PP} = "M";
  } else {
     print "$climUtlDir/climWrite -stn $SHEFOB{STN} -ddir $climDataDir";
     print " -y $SHEFOB{YEAR} -m $SHEFOB{MONTH} -a $SHEFOB{DAY}";
     print " -v pcpn -d $SHEFOB{PP}\n";
     $resultStr = `$climUtlDir/climWrite -stn $SHEFOB{STN} -ddir $climDataDir -y $SHEFOB{YEAR} -m $SHEFOB{MONTH} -a $SHEFOB{DAY} -v pcpn -d $SHEFOB{PP}`;
     print "$resultStr\n"; 
     $newData = 1;
     if ($SHEFOB{PP} > 0 && $SHEFOB{TX} ne "M" && $SHEFOB{TX} > 31) {
	$SHEFOB{WXCODE} |= $WX{rain};
     }
  }
} else {
  $SHEFOB{PP} = "M";
}
################## Load Snowfall #####################
if ($SHEFOB{SF} =~ /[0-9.-T]+/) {
  if ($SHEFOB{SF} ne "T" && $SHEFOB{SF} < 0) {
     print "Error: negative snowfall!\n";
     $SHEFOB{SF} = "M";
  } elsif ($SHEFOB{SF} ne "T" && $SHEFOB{SF} > $SNOWHI) {
     print "Error: snowfall out of range!\n";
     $SHEFOB{SF} = "M";
  } else {
     print "$climUtlDir/climWrite -stn $SHEFOB{STN} -ddir $climDataDir";
     print " -y $SHEFOB{YEAR} -m $SHEFOB{MONTH} -a $SHEFOB{DAY}";
     print " -v snow -d $SHEFOB{SF}\n";
     $resultStr = `$climUtlDir/climWrite -stn $SHEFOB{STN} -ddir $climDataDir -y $SHEFOB{YEAR} -m $SHEFOB{MONTH} -a $SHEFOB{DAY} -v snow -d $SHEFOB{SF}`;
     print "$resultStr\n"; 
     $newData = 1;
     if ($SHEFOB{SF} > 0) {
	$SHEFOB{WXCODE} |= $WX{snow};
     }
  }
} else {
  $SHEFOB{SF} = "M";
}
################ Load Snow Depth ######################
if ($SHEFOB{SD} =~ /[0-9.-T]+/) {
  if ($SHEFOB{SD} ne "T" && $SHEFOB{SD} < 0) {
     print "Error: Snow on ground of range!\n";
     $SHEFOB{SD} = "M";
  } elsif ($SHEFOB{SD} ne "T" && $SHEFOB{SD} > $SNWDHI) {
     print "Error: Snow on ground of range!\n";
     $SHEFOB{SD} = "M";
  } else {
     print "$climUtlDir/climWrite -stn $SHEFOB{STN} -ddir $climDataDir";
     print " -y $SHEFOB{YEAR} -m $SHEFOB{MONTH} -a $SHEFOB{DAY}";
     print " -v snwg -d $SHEFOB{SD}\n";
     $resultStr = `$climUtlDir/climWrite -stn $SHEFOB{STN} -ddir $climDataDir -y $SHEFOB{YEAR} -m $SHEFOB{MONTH} -a $SHEFOB{DAY} -v snwg -d $SHEFOB{SD}`;
     print "$resultStr\n"; 
     $newData = 1;
  }
} else {
  $SHEFOB{SD} = "M";
}
############### Peak Wind Speed ######################
if ($SHEFOB{UP} =~ /[0-9.-]+/) {
  if ($SHEFOB{UP} < 0 || $SHEFOB{UP} > $WINDHI) {
     print "Error: Peak wind out of range!\n";
     $SHEFOB{UP} = "M";
  } else {
     print "$climUtlDir/climWrite -stn $SHEFOB{STN} -ddir $climDataDir";
     print " -y $SHEFOB{YEAR} -m $SHEFOB{MONTH} -a $SHEFOB{DAY}";
     print " -v pkwndspd -d $SHEFOB{UP}\n";
     $resultStr = `$climUtlDir/climWrite -stn $SHEFOB{STN} -ddir $climDataDir -y $SHEFOB{YEAR} -m $SHEFOB{MONTH} -a $SHEFOB{DAY} -v pkwndspd -d $SHEFOB{UP}`;
     print "$resultStr\n"; 
     $newData = 1;
     if ($SHEFOB{UP} > 58) {
	$SHEFOB{WXCODE} |= $WX{wind};
     }
  }
} else {
  $SHEFOB{UP} = "M";
}
############### Peak Wind Direction ##################
if ($SHEFOB{UR} =~ /[0-9.-]+/) {
  if ($SHEFOB{UR} < 0 || $SHEFOB{UR} > 360) {
     print "Error: Peak wind out of range!\n";
     $SHEFOB{UR} = "M";
  } else {
     if (($SHEFOB{UR} * 10) <= 360) {
        $SHEFOB{UR} *= 10;
     }
     print "$climUtlDir/climWrite -stn $SHEFOB{STN} -ddir $climDataDir";
     print " -y $SHEFOB{YEAR} -m $SHEFOB{MONTH} -a $SHEFOB{DAY}";
     print " -v pkwnddir -d $SHEFOB{UR}\n";
     $resultStr = `$climUtlDir/climWrite -stn $SHEFOB{STN} -ddir $climDataDir -y $SHEFOB{YEAR} -m $SHEFOB{MONTH} -a $SHEFOB{DAY} -v pkwnddir -d $SHEFOB{UR}`;
     print "$resultStr\n"; 
     $newData = 1;
  }
} else {
  $SHEFOB{UR} = "M";
}
##################### Weather Codes ####################
if ($SHEFOB{WXCODE} > 0 && $SHEFOB{WXCODE} < 16384) {
     print "$climUtlDir/climWrite -stn $SHEFOB{STN} -ddir $climDataDir";
     print " -y $SHEFOB{YEAR} -m $SHEFOB{MONTH} -a $SHEFOB{DAY}";
     print " -v wxcode -d $SHEFOB{WXCODE}\n";
     $resultStr = `$climUtlDir/climWrite -stn $SHEFOB{STN} -ddir $climDataDir -y $SHEFOB{YEAR} -m $SHEFOB{MONTH} -a $SHEFOB{DAY} -v wxcode -d $SHEFOB{WXCODE}`;
     print "$resultStr\n"; 
} elsif ($SHEFOB{WXCODE} >= 16384) {
     print "Error: Weather code out of range! [$SHEFOB{WXCODE}]\n";
     $SHEFOB{WXCODE} = "M";
}
#
  # check if data needs to be distributed to AWIPS via LDM
  if ($distribData == 1 && $newData == 1) {
     print "Distributing update to AWIPS: $climDataDir/$climFile\n";
     $resultStr = `remsh bering "/apps/xmclimate/bin/climDistrib.pl $climDataDir/$climFile $SHEFOB{MONTH} $SHEFOB{YEAR} OBS EXTERN"`;
     print "$resultStr\n"; 
     $newData = 1;
  }
}

##########################################################
# Daily occurrence weather table codes (DYSW) used by 
# NCDC are different from the WMO type wx codes contained 
# in SHEF data. Xmclimate uses the DYSW code 
# list with an assigned bit position in a short integer
#     COOP              WMO
#  1  smoke or haze     4 - 5
#  2  fog               10 - 12; 40 - 49
#  3  unassigned        
#  4  drizzle           50 - 59
#  5  ice pellets       79
#  6  glaze             66 - 69
#  7  thunder           17; 29; 91 - 99
#  8  hail              96 
#  9  dust or sand      6 - 9, 30 - 35
# 10  blowing snow	36 = 39
# 11  high wind
# 12  tornado           19
# 13  rain		60 - 65
# 14  snow		70 - 78
#####################################################
sub convertWxCodes {
print "searching wx codes for $_[0] \n";

  if ($_[0] == 4) {
     return $WX{smoke};
  } elsif ($_[0] == 5) {
     return $WX{haze};
  } elsif ($_[0] >= 6 && $_[0] <= 9) {
     return $WX{dust};
  } elsif ($_[0] >= 10 && $_[0] <= 12) {
     return  $WX{fog};
  } elsif ($_[0] == 17 || $_[0] == 29) {
     return $WX{thunder};
  } elsif ($_[0] == 19) {
     return $WX{tornado};
  } elsif ($_[0] == 20) {
     return $WX{drizzle};
  } elsif ($_[0] == 21) {
     return $WX{rain};
  } elsif ($_[0] == 22) {
     return $WX{snow};
  } elsif ($_[0] == 24) {
     return $WX{glaze};
  } elsif ($_[0] == 25) {
     return $WX{rain};
  } elsif ($_[0] == 23 || $_[0] == 26 || $_[0] == 68 || $_[0] == 69) {
     return ($WX{rain} + $WX{snow});
  } elsif ($_[0] == 27 ||$_[0] == 88) {
     return $WX{hail};
  } elsif ($_[0] == 28) {
     return $WX{fog};
  } elsif ($_[0] >= 30 && $_[0] <= 35) {
     return $WX{sand};
  } elsif ($_[0] >= 36 && $_[0] <= 39) {
     return $WX{blowsnow};
  } elsif ($_[0] >= 40 && $_[0] <= 49) {
     return $WX{fog};
  } elsif ($_[0] >= 50 && $_[0] <= 59) {
     return $WX{drizzle};
  } elsif ($_[0] >= 60 && $_[0] <= 65) {
     return $WX{rain};
  } elsif ($_[0] == 66 || $_[0] == 67) {
     return ($WX{rain} + $WX{glaze});
  } elsif ($_[0] >= 70 && $_[0] <= 78) {
     return $WX{snow};
  } elsif ($_[0] == 79) {
     return $WX{ice};
  } elsif ($_[0] >= 80 && $_[0] <= 82) {
     return $WX{rain};
  } elsif ($_[0] == 83 || $_[0] == 84) {
     return ($WX{rain} + $WX{snow});
  } elsif ($_[0] == 85 || $_[0] == 86) {
     return $WX{snow};
  } elsif ($_[0] == 87 || $_[0] == 88) {
     return $WX{ice};
  } elsif ($_[0] == 89 || $_[0] == 90) {
     return $WX{hail};
  } elsif ($_[0] == 91 || $_[0] == 92 || $_[0] == 95 || $_[0] == 97) {
     return ($WX{thunder} + $WX{rain});
  } elsif ($_[0] == 93 || $_[0] == 94) {
     return ($WX{thunder} + $WX{snow});
  } elsif ($_[0] == 98) {
     return ($WX{thunder} + $WX{dust});
  } elsif ($_[0] == 96 || $_[0] == 99) {
     return ($WX{thunder} + $WX{rain} + $WX{hail});
  } else {
     return 0;
  }
}

