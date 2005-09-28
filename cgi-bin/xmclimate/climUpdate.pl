#!/usr/bin/perl
###########################################################################
#a########################climUpdate.pl####################################
##Program written by Carl Dierking at WSFO Juneau
##Use: Script for loading an ascii file contain one month of climate
##     climate data into xmclimate netCDF files 
###########################################################################
$updateDir = "/data/climIn";
$dataDir = "/data/climdata";
$binDir = "/apps/xmclimate/bin";

opendir(DIR, $updateDir) or die "Unable to opendir $updateDir: $!";
@climfiles = grep { /XMCLI/ } readdir (DIR);
closedir(DIR);
#
for ($i = 0; $i <= $#climfiles; $i++) {
$climfiles[$i] = $updateDir . '/' . $climfiles[$i];
$datestr = `date +"%T %D"`;
chomp($datestr);
print "$datestr  Found: $climfiles[$i]\n";

#print "/usr/local/bin/climWrite -ddir $dataDir -f $climfiles[$i]\n";
$resultString = `$binDir/climWrite -ddir $dataDir -f $climfiles[$i]`;
print $resultString;
}
if ($#climfiles >= 0) {
   unlink (@climfiles) or warn "Unable to unlink all files in $updateDir: $!";
}
###########################################################################
############################End of Program#################################


