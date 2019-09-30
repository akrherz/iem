<?php 
include("../../config/settings.inc.php");
include("../../include/myview.php");
$t = new MyView();
$t->title = "LDM Request HOWTO";

$t->content = <<<EOF
<ol class="breadcrumb">
  <li><a href="/info.php">IEM Information</a></li>
  <li class="active">Real-time IEM data feeds with LDM HOWTO</li>
</ol>

<p>This page will show you all the steps necessary
to set up a LDM data feed from the Iowa Environmental Mesonet [IEM].  Currently,
we are offering the SchoolNet (KCCI-TV8) dataset and Roadway Weather Information System (RWIS) dataset via LDM.</p>

<p><b>STEP 1: Send an Email</b><br>
Send us an email requesting a LDM feed.  You can send this email to me, Daryl
Herzmann (akrherz@iastate.edu) . You should include contact information
and the DNS/IP of the host that you will be using to connect to the IEM LDM. 
We would like to keep track of who is requesting data and what they are using 
the data for, so please include that as well.</p>

<p><b>STEP 2: Download GEMPAK surface tables</b><br>
Here are the GEMPAK surface tables needed to point dcmetr at. You should download
these files and place them somewhere accessible by your decoders.<br>
<a href="IA.snet.stn">SchoolNet</a>  and <a href="IA.rwis.stn">RWIS</a>
</p>

<p><b>STEP 3.1: Configure LDM (ldmd.conf)</b><br>
For the purposes of this HOWTO, I am assuming that you have administrative 
knowledge of LDM.  You will want to edit your ldmd.conf file to request the
data feeds from the IEM.  Remember the tabs!
<pre style="background: #EEEEEE">
 # Request Iowa Mesonet RWIS data, filename IA.rwisDDHHMM.sao
request	EXP	"^IA\.rwis......\.sao"	mesonet.agron.iastate.edu
 # Request Iowa Mesonet SchoolNet data, filename IA.snetDDHHMM.sao
request	EXP	"^IA\.snet......\.sao"	mesonet.agron.iastate.edu
</pre>

<p><b>STEP 3.2: Configure LDM (pqact.conf)</b><br>
Since you have went through all this effort to request the data, you should
at least process it somehow!  The datafiles are in METAR collectives with a 
fake WMO header.  (KISU is used, referring to Iowa State).  Here are samples 
of what you can do with your pqact.conf file.  Remember the tabs!
<pre style="background: #EEEEEE">
  # Process Iowa Mesonet SchoolNet data
  # Product name: IA.snetDDHHMM.sao, where DD is day HH is hour, MM is minute
  # Data is inserted at :17, :37 and :57 after the hour.
#EXP	^IA\.snet......\.sao
#	PIPE	dcmetr -b 3 -m 72 -s /path/to/surf/file/IA.snet.stn
#		-t 1200 -d data/gempak/logs/dcmetr_IAsnet.log -a 0
#		data/gempak/surface/exp/YYYYMMDD_IAsnet.gem
  # Process Iowa Mesonet RWIS data
  # Product name: IA.rwisDDHHMM.sao, where DD is day HH is hour, MM is minute
  # Data is inserted every 10 minutes starting at :06 after
#EXP	^IA\.rwis......\.sao
#	PIPE	dcmetr -b 3 -m 72 -s /path/to/surf/file/IA.rwis.stn
#		-t 1200 -d data/gempak/logs/dcmetr_IArwis.log -a 0
#		data/gempak/surface/exp/YYYYMMDD_IArwis.gem
  # Do something fancy, and combine them in one file!
EXP	^IA\.(rwis|snet)......\.sao
	PIPE	dcmetr	-b 3 -m 72 -s /path/to/combined/file
		-t 1200 -d data/gempak/logs/dcmetr_IEM.log -a 0
		data/gempak/surface/YYYYMMDD_IEM.gem
</pre>

<br>SchoolNet data files are generated every 20 minutes.  RWIS files are generated
every 10 minutes.  You may want to be a bit more creative with the LDM request
and pqact.conf configuration to limit the number of products decoded.  The products
are marked with a timestamp (DayDayHourHourMinuteMinute) .
<br>
<br>Now, hopefully by this time, I has responded to your email and set
up the IEM LDM to accept your data connection.  You may want to try a simple
LDM command to see if your connection is allowed.
<pre style="background: #EEEEEE">
$ notifyme -v -l - -h mesonet.agron.iastate.edu -f EXP
</pre>
It may take 5-10 minutes before a new data product hits the IEM data queue.
If this command worked, you are probably all set!  Restart LDM and see what
breaks!</p>

<p><b>STEP 4: Sign up for IEM bulletin (optional)</b>
<br>You don't have to complete this step, but you can keep up-to-date with
IEM news and events with the IEM Daily Bulletin.  You can sign up for it
<a 
href="https://mailman.iastate.edu/mailman/listinfo/iem-dailyb">here</a>.
 If this service generates enough interest, I will set up a dedicated 
email
list for it.

<p><b>CAVEATS!!!</b>
<ul>
 <li>These networks are not reporting in METAR format. The format is generated
from the raw ASCII data.  If you ever notice formatting issues, please let us
know.  Many of the scripts have been in use for a year now, so they are somewhat
robust.  Having sub-zero temperatures makes the METAR format fun!</li>
 <li><b>Important!</b>  It is not recommended that you integrate this dataset 
with the normal ASOS/AWOS sites you get via the IDD or from the dish.  Some
of these instruments are in ditches or on top of school roofs.  They are not
thoroughly QC'd either, the IEM is working on QC routines and will implement 
them in the future.</li>
</ul>

<p><b>Current Data Users:</b>
<br><a href="http://www.rap.ucar.edu/weather/surface/">NCAR-RAP Surface Data</a>, Boulder, CO
<br><a href="http://www.spc.noaa.gov">Storm Prediction Center</a>, Norman, 
OK
<br><a href="http://www.crh.noaa.gov/dmx/">NWS WFO Des Moines, IA</a>
<br><a href="http://www.crh.noaa.gov/unr/">NWS WFO Rapid City, SD</a>
<br><a href="http://www.crh.noaa.gov/fsd/">NWS WFO Sioux Falls, SD</a>
<br><a href="http://www.atmos.albany.edu">University of Albany, NY</a>
<br><a href="http://weather.cod.edu">College of DuPage, IL</a>
<br /><a href="http://www.mesonet.ttu.edu/">West Texas Mesonet, TX</a>
<br>

<p align="right">
Daryl Herzmann 
<br> (akrherz@iastate.edu)
<br> Rev: 26 Dec 2002

EOF;
$t->render('single.phtml');
?>
