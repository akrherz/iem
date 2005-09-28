#!/usr/bin/perl

read(STDIN, $request, $ENV{'CONTENT_LENGTH'});

$filepath = "/mesonet/www/html/climodat/data/";

%files = ( "112 41.0333 92.8000 ALBIA", "al0112fr.dat",
	"133 43.0667 94.3000 ALGONA", "al0133fr.dat",
	"157 42.7500 92.7833 ALLISON", "al0157fr.dat",
	"200 42.0333 93.8000 AMES-8-WSW", "am0200fr.dat",
	"213 42.1167 91.3000 ANAMOSA-1-WNW", "an0213fr.dat",
	"241 41.6833 93.6000 ANKENY-3-S", "an0241fr.dat",
	"364 41.4167 95.0000 ATLANTIC-1-NE", "at0364fr.dat",
	"385 41.7167 94.9333 AUDUBON", "au0385fr.dat",
	"576 40.6833 94.7167 BEDFORD-1-NNW", "be0576fr.dat",
	"600 41.8833 92.2667 BELLE-PLAINE", "be0600fr.dat",
	"608 42.2667 90.4167 BELLEVUE-L-AND-D-12", "be0608fr.dat",
	"753 40.7500 92.4333 BLOOMFIELD", "bl0753fr.dat",
	"923 43.0667 93.8000 BRITT", "br0923fr.dat",
	"1233 42.0667 94.8500 CARROLL-2-SSW", "ca1233fr.dat",
	"1257 42.3000 91.0167 CASCADE", "ca1257fr.dat",
	"1277 42.0667 95.8167 CASTANA-EXP-FARM", "ca1277fr.dat",
	"1319 42.0333 91.5833 CEDAR-RAPIDS-1", "ce1319fr.dat",
	"1354 40.7333 92.8667 CENTERVILLE", "ce1354fr.dat",
	"1394 41.0000 93.3167 CHARITON", "ch1394fr.dat",
	"1402 43.0500 92.6667 CHARLES-CITY", "ch1402fr.dat",
	"1442 42.7500 95.5333 CHEROKEE", "ch1442fr.dat",
	"1533 40.7333 95.0333 CLARINDA", "cl1533fr.dat",
	"1541 42.7333 93.7500 CLARION", "cl1541fr.dat",
	"1635 41.8000 90.2667 CLINTON-1", "cl1635fr.dat",
	"1731 41.2500 91.3667 COLUMBUS-JCT-2-SSW", "co1731fr.dat",
	"1833 41.0000 94.7500 CORNING", "co1833fr.dat",
	"1848 40.7667 93.3000 CORYDON", "co1848fr.dat",
	"1954 43.3833 92.1000 CRESCO-1-NE", "cr1954fr.dat",
	"2110 43.3167 91.7833 DECORAH-2-N", "de2110fr.dat",
	"2171 42.0333 95.3333 DENISON", "de2171fr.dat",
	"2364 42.5333 90.6500 DUBUQUE-LOCK-AND-DAM", "du2364fr.dat",
	"2689 43.1000 94.6833 EMMETSBURG", "em2689fr.dat",
	"2724 43.4167 94.8333 ESTHERVILLE-2-N", "es2724fr.dat",
	"2789 41.0333 91.9500 FAIRFIELD", "fa2789fr.dat",
	"2864 42.8333 91.8000 FAYETTE", "fa2864fr.dat",
	"2977 43.2833 93.6333 FOREST-CITY", "fo2977fr.dat",
	"3007 40.6167 91.3333 FORT-MADISON", "fo3007fr.dat",
	"2999 42.5000 94.2000 FORT-DODGE", "fo2999fr.dat",
	"3290 41.0000 95.7667 GLENWOOD", "gl3290fr.dat",
	"3438 41.3000 94.4667 GREENFIELD", "gr3438fr.dat",
	"3473 41.7167 92.7333 GRINNELL-3-SW", "gr3473fr.dat",
	"3487 42.3667 92.7833 GRUNDY-CENTER", "gr3487fr.dat",
	"3509 41.6833 94.5000 GUTHRIE-CENTER", "gu3509fr.dat",
	"3517 42.7833 91.1000 GUTTENBERG-L-AND-D-10", "gu3517fr.dat",
	"3584 42.7500 93.2000 HAMPTON-2-NW", "ha3584fr.dat",
	"3632 41.6500 95.3167 HARLAN", "ha3632fr.dat",
	"3718 43.0000 96.4833 HAWARDEN", "ha3718fr.dat",
	"3985 42.6833 94.2000 HUMBOLDT-2", "hu3985fr.dat",
	"4038 42.3500 95.4833 IDA-GROVE", "id4038fr.dat",
	"4052 42.4833 91.8167 INDEPENDENCE-2-W", "in4052fr.dat",
	"4063 41.3667 93.5500 INDIANOLA-2-SSW", "in4063fr.dat",
	"4101 41.6500 91.5333 IOWA-CITY", "io4101fr.dat",
	"4142 42.5333 93.2667 IOWA-FALLS", "io4142fr.dat",
	"4228 42.0167 94.3833 JEFFERSON", "je4228fr.dat",
	"4389 40.7333 91.9667 KEOSAUQUA", "ke4389fr.dat",
	"4502 41.3167 93.1333 KNOXVILLE", "kn4502fr.dat",
	"4735 42.8000 96.1667 LEMARS", "le4735fr.dat",
	"4894 41.6333 95.8000 LOGAN", "lo4894fr.dat",
	"5086 42.4667 91.4500 MANCHESTER-2", "ma5086fr.dat",
	"5131 42.0667 90.7000 MAQUOKETA-2-W", "ma5131fr.dat",
	"5198 42.0667 92.9333 MARSHALLTOWN", "ma5198fr.dat",
	"5230 43.1500 93.2000 MASON-CITY", "ma5230fr.dat",
	"5493 43.3833 95.1833 MILFORD-4-NW", "mi5493fr.dat",
	"5769 40.7000 94.2500 MOUNT-AYR", "mt5769fr.dat",
	"5796 40.9500 91.5500 MOUNT-PLEASANT", "mo5796fr.dat",
	"5837 41.4000 91.0667 MUSCATINE", "mu5837fr.dat",
	"5952 43.0500 92.3167 NEW-HAMPTON", "ne5952fr.dat",
	"5992 41.7000 93.0500 NEWTON", "ne5992fr.dat",
	"6103 43.4500 93.2167 NORTHWOOD", "no6103fr.dat",
	"6151 41.3167 95.3833 OAKLAND-2-E", "oa6151fr.dat",
	"6200 42.6500 91.9167 OELWEIN-2-S", "oe6200fr.dat",
	"6243 42.0167 96.1000 ONAWA", "on6243fr.dat",
	"6305 43.2833 92.8000 OSAGE", "os6305fr.dat",
	"6316 41.1500 93.8167 OSCEOLA-3-WSW", "os6316fr.dat",
	"6327 41.3167 92.6500 OSKALOOSA", "os6327fr.dat",
	"6566 41.8333 94.1167 PERRY", "pe6566fr.dat",
	"6719 42.7000 94.6667 POCAHONTAS", "po6719fr.dat",
	"6800 43.0833 95.6333 PRIMGHAR", "pr6800fr.dat",
	"6940 41.0000 95.2333 RED-OAK", "re6940fr.dat",
	"7147 43.4333 96.1667 ROCK-RAPIDS", "ro7147fr.dat",
	"7161 42.4000 94.6167 ROCKWELL-CITY", "ro7161fr.dat",
	"7312 42.4333 95.0000 SAC-CITY", "sa7312fr.dat",
	"7613 40.7833 95.3500 SHENANDOAH-1-NE", "sh7613fr.dat",
	"7664 43.4500 95.7167 SIBLEY-5-NNE", "si7664fr.dat",
	"7669 40.7500 95.6500 SIDNEY", "si7669fr.dat",
	"7678 41.3333 92.2000 SIGOURNEY", "si7678fr.dat",
	"7708 42.4000 96.3833 SIOUX-CITY-WSO-AP", "si7708fr.dat",
	"7726 42.8833 95.1500 SIOUX-RAPIDS", "si7726fr.dat",
	"7979 42.6333 95.1833 STORM-LAKE-2-E", "st7979fr.dat",
	"8266 41.7833 91.1167 TIPTON", "ti8266fr.dat",
	"8296 41.9833 92.5833 TOLEDO", "to8296fr.dat",
	"8339 42.8167 92.2500 TRIPOLI-4-N", "tr8339fr.dat",
	"8568 42.1667 92.0000 VINTON", "vi8568fr.dat",
	"8688 41.2833 91.6833 WASHINGTON", "wa8688fr.dat",
	"8704 42.5500 92.4000 WATERLOO WSO", "wa8704fr.dat",
	"8755 43.2667 91.4833 WAUKON", "wa8755fr.dat",
	"8806 42.4667 93.8000 WEBSTER-CITY", "we8806fr.dat",
	"9067 41.6667 92.0167 WILLIAMSBURG", "wi9067fr.dat",
	"9132 41.3333 94.0000 WINTERSET", "wi9132fr.dat");

%start_string =( "Number of Precipitation Events", "# OF PRECIPITATION EVENTS",
	"Twelve Significant Rainfall Events", "TWELVE SIGNIFICANT RAINFALL EVENTS",
	"Growing Degree Days", "GROWING DEGREE DAYS",
	"Daily Record Highs and Lows", "DAILY RECORD HIGHS AND LOWS OCCURRING",
	"Daily Maximum Precipitation", "DAILY MAXIMUM PRECIPITATION",
	"Daily Record Hi and Low Ranges", "RECORD LARGEST AND SMALLEST",
	"Daily Mean Highs and Lows", "DAILY  MEAN  HIGHS AND LOWS",
	"Number of Days Each Year Min >= 32", "# OF DAYS EACH YEAR WHERE MIN >=32",
	"Last Spring/First Fall/Length of Season Base=32", "BASE TEMP=32",
	"Last Spring/First Fall/Length of Season Base=30", "BASE TEMP=30",
	"Last Spring/First Fall/Length of Season Base=28", "BASE TEMP=28",
	"Last Spring/First Fall/Length of Season Base=26", "BASE TEMP=26",
	"Last Spring/First Fall/Length of Season Base=24", "BASE TEMP=24",
	"Monthly Average Maximum Temperatures", "MONTHLY AVG. MAX TEMPS",
	"Monthly Average Minimum Temperatures", "MONTHLY AVG. MIN TEMPS",
	"Monthly Average Mean Temperatures", "MONTHLY AVG. MEAN TEMPS",
	"Monthly Average Precipitation Totals", "MONTHLY PRECIP TOTALS AND",
	"Monthly Heating Degree Days", "MONTHLY HEATING DEGREE DAYS",
	"Monthly Cooling Degree Days", "MONTHLY COOLING DEGREE DAYS",
	"Heat Stress Variables", "HEAT STRESS VARIABLES");

%stop_string =("Number of Precipitation Events", "TWELVE SIGNIFICANT RAINFALL EVENTS",
	"Twelve Significant Rainfall Events", "GROWING DEGREE DAYS",
	"Growing Degree Days",  "DAILY RECORD HIGHS AND LOWS OCCURRING",
	"Daily Record Highs and Lows", "DAILY MAXIMUM PRECIPITATION",
	"Daily Maximum Precipitation",  "RECORD LARGEST AND SMALLEST",
	"Daily Record Hi and Low Ranges", "DAILY  MEAN  HIGHS AND LOWS",
	"Daily Mean Highs and Lows", "# OF DAYS EACH YEAR WHERE MIN >=32",
	"Number of Days Each Year Min >= 32", "BASE TEMP=32",
	"Last Spring/First Fall/Length of Season Base=32", "BASE TEMP=30",
	"Last Spring/First Fall/Length of Season Base=30", "BASE TEMP=28",
	"Last Spring/First Fall/Length of Season Base=28", "BASE TEMP=26",
	"Last Spring/First Fall/Length of Season Base=26", "BASE TEMP=24",
	"Last Spring/First Fall/Length of Season Base=24", "MONTHLY AVG. MAX TEMPS",
	"Monthly Average Maximum Temperatures", "MONTHLY AVG. MIN TEMPS",
	"Monthly Average Minimum Temperatures", "MONTHLY AVG. MEAN TEMPS",
	"Monthly Average Mean Temperatures", "MONTHLY PRECIP TOTALS AND",
	"Monthly Average Precipitation Totals", "MONTHLY HEATING DEGREE DAYS",
	"Monthly Heating Degree Days", "MONTHLY COOLING DEGREE DAYS",
	"Monthly Cooling Degree Days", "HEAT STRESS VARIABLES",
	"Heat Stress Variables", "EOF");

print "Content-type: text/plain\n\n";
#&print_header("Here it is!");

@req=split(/&/, $request);
foreach (@req) {
        tr/+/ /;
	s/%(..)/pack("c",hex($1))/ge;
}
	
#print ("$req[0]!\n-----------------------------\n");
#print ("$req[1]!\n-----------------------------\n");


@station=split(/=/, $req[0]);

#print ("\nstation is $station[1]!\n");

$filename = $files{"$station[1]"};

#print ("\n!$filepath$filename!\n");

@searcher=split(/=/, $req[1]);

if (@searcher>2)
{
    $searcher[1]="$searcher[1]=$searcher[2]";
}

#print ("\ndata is $searcher[1]\n");

$start_search_string = $start_string{"$searcher[1]"};

#print ("\nstart search string = $start_search_string\n");

$stop_search_string = $stop_string{"$searcher[1]"};

#print ("\nstop search string = $stop_search_string\n");

if (open (INFILE, "$filepath$filename")) {
#			print ("\nFile opened successfully!\n");
}
else
{
	print ("\nFile not opened!\n");
	print ("$filepath$filename");
}


$inline=<INFILE>;
while (($inline !~ /$stop_search_string/)&&(!eof(INFILE)))
{
     if ($inline =~ /$start_search_string/)
      {
         $printem=1;
      }
     if ($printem)
      {
         print ("$inline");
      }
     $inline=<INFILE>;
}

if ($stop_search_string =~ /EOF/)
{
    print ("$inline");
}

close(INFILE);

#&print_footer;

sub print_header {
    local ($title) = @_;

	print ("Content-type: text/html\n\n");
	print ("<HTML><HEAD>\n");
	print ("<TITLE>$title</TITLE>");
	print ("$title\n\n");
	print ("</HEAD>\n<BODY>\n");
}

sub print_footer {
     print ("</BODY>\n</HTML>\n");
}



         


