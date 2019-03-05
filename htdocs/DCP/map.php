<?php 
/**
 * Produce a map of SHEF values
 */
require_once "../../config/settings.inc.php";
define("IEM_APPID", 119);
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "SHEF Physical Code Map";
$t->thispage = "networks-dcp";
$OL = '4.6.4';
$t->headextra = <<<EOF
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link rel="stylesheet" href="/vendor/jquery-ui/1.11.4/jquery-ui.min.css" />
<link type="text/css" href="/vendor/openlayers/{$OL}/ol3-layerswitcher.css" rel="stylesheet" />
<style>
.map {
	height: 75%;
	width: 100%;
	background-color: #D2B48C;
}
.popover {
		width: 300px;
		}
</style>
EOF;
$t->jsextra = <<<EOF
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src="/vendor/jquery-ui/1.11.4/jquery-ui.js"></script>
<script src='/vendor/openlayers/{$OL}/ol3-layerswitcher.js'></script>
<script src='map.js?v=2'></script>
EOF;

$t->content = <<<EOF

<div id="popover-content" style="display: none">
  <!-- Hidden div with the popover content -->
  <p>This is the popover content</p>
</div>

<div class="breadcrumb">
		<li><a href="/DCP/">DCP/HADS Mainpage</a></li>
		<li class="active">Map of SHEF Reports</li>
		</div>
		
<div class="row">
<div class="col-md-12">
		
<div class="pull-right">
<i class="fa fa-text-size"></i>
<button id="fminus" class="btn btn-default"><i class="fa fa-minus"></i></button>
<button id="fplus" class="btn btn-default"><i class="fa fa-plus"></i></button>
</div>

<p>The IEM processes the raw SHEF encoded data into its raw components which
include the physical code and time duration.  This tool presents a simple map
of the last parsed value for a given physical code and duration.  The within days
limits the map to only show stations that have reported the value within the
given number of days.  This is a work-in-progress here and <a href="/info/contacts.php">your feedback</a> would
be wonderful.</p>

		<form name='bah'><p><strong>Select Physical Code:</strong> 
<select onChange="javascript: updateMap();" id="pe">
<option value="AD">[AD] Reserved</option>
<option value="AF">[AF] Surface frost intensity (coded, see Table 20)</option>
<option value="AG">[AG] Percent of green vegetation (%)</option>
<option value="AM">[AM] Surface dew intensity (coded, see Table 21)</option>
<option value="AT">[AT] Time below critical temperature, 25 DF or -3.9 DC (HRS and MIN)</option>
<option value="AU">[AU] Time below critical temperature, 32 DF or 0 DC (HRS and MIN)</option>
<option value="AW">[AW] Leaf wetness (HRS and MIN)</option>
<option value="BA">[BA] Solid portion of water equivalent (in, mm)</option>
<option value="BB">[BB] Heat deficit (in, mm)</option>
<option value="BC">[BC] Liquid water storage (in, mm)</option>
<option value="BD">[BD] Temperature index (DF, DC)</option>
<option value="BE">[BE] Maximum water equivalent since snow began to accumulate (in, mm)</option>
<option value="BF">[BF] Areal water equivalent just prior to the new snowfall (in, mm)</option>
<option value="BG">[BG] Areal extent of snow cover from the areal depletion curve just prior to the new snowfall (%)</option>
<option value="BH">[BH] Amount of water equivalent above which 100 % areal snow cover temporarily exists (in, mm)</option>
<option value="BI">[BI] Excess liquid water in storage (in, mm)</option>
<option value="BJ">[BJ] Areal extent of snow cover adjustment (in, mm)</option>
<option value="BK">[BK] Lagged excess liquid water for interval 1 (in, mm)</option>
<option value="BL">[BL] Lagged excess liquid water for interval 2 (in, mm)</option>
<option value="BM">[BM] Lagged excess liquid water for interval 3 (in, mm)</option>
<option value="BN">[BN] Lagged excess liquid water for interval 4 (in, mm)</option>
<option value="BO">[BO] Lagged excess liquid water for interval 5 (in, mm)</option>
<option value="BP">[BP] Lagged excess liquid water for interval 6 (in, mm)</option>
<option value="BQ">[BQ] Lagged excess liquid water for interval 7 (in, mm)</option>
<option value="CA">[CA] Upper zone tension water contents (in, mm)</option>
<option value="CB">[CB] Upper zone free water contents (in, mm)</option>
<option value="CC">[CC] Lower zone tension water contents (in, mm)</option>
<option value="CD">[CD] Lower zone free water supplementary storage contents (in, mm)</option>
<option value="CE">[CE] Lower zone free water primary storage contents (in, mm)</option>
<option value="CF">[CF] Additional impervious area contents (in, mm)</option>
<option value="CG">[CG] Antecedent precipitation index (in, mm)</option>
<option value="CH">[CH] Soil moisture index deficit (in, mm)</option>
<option value="CI">[CI] Base flow storage contents (in, mm)</option>
<option value="CJ">[CJ] Base flow index (in, mm)</option>
<option value="CK">[CK] First quadrant index Antecedent Evaporation Index (AEI) (in, mm)</option>
<option value="CL">[CL] First quadrant index Antecedent Temperature Index (ATI) (DF, DC)</option>
<option value="CM">[CM] Frost index (DF, DC)</option>
<option value="CN">[CN] Frost efficiency index (%)</option>
<option value="CO">[CO] Indicator of first quadrant index (AEI or ATI)</option>
<option value="CP">[CP] Storm total rainfall (in, mm)</option>
<option value="CQ">[CQ] Storm total runoff (in, mm)</option>
<option value="CR">[CR] Storm antecedent index (in, mm)</option>
<option value="CS">[CS] Current antecedent index (in, mm)</option>
<option value="CT">[CT] Storm period counter (integer)</option>
<option value="CU">[CU] Average air temperature (DF, DC)</option>
<option value="CV">[CV] Current corrected synthetic temperature (DF, DC)</option>
<option value="CW">[CW] Storm antecedent evaporation index, AEI (in, mm)</option>
<option value="CX">[CX] Current AEI (in, mm)</option>
<option value="CY">[CY] Current API (in, mm)</option>
<option value="CZ">[CZ] Climate Index</option>
<option value="EA">[EA] Evapotranspiration potential amount (IN, MM)</option>
<option value="ED">[ED] Evaporation, pan depth (IN, MM)</option>
<option value="EM">[EM] Evapotranspiration amount (IN, MM)</option>
<option value="EP">[EP] Evaporation, pan increment (IN, MM)</option>
<option value="ER">[ER] Evaporation rate (IN/day, MM/day)</option>
<option value="ET">[ET] Evapotranspiration total (IN, MM)</option>
<option value="EV">[EV] Evaporation, lake computed (IN, MM)</option>
<option value="FA">[FA] Fish - shad</option>
<option value="FB">[FB] Fish - sockeye</option>
<option value="FC">[FC] Fish - chinook</option>
<option value="FE">[FE] Fish - chum</option>
<option value="FK">[FK] Fish - coho</option>
<option value="FL">[FL] Fish - ladder (1=left, 2=right, 3=total)</option>
<option value="FP">[FP] Fish - pink</option>
<option value="FS">[FS] Fish – steelhead</option>
<option value="FT">[FT] Fish type - type (1=adult, 2=jacks, 3=fingerlings)</option>
<option value="FZ">[FZ] Fish - count of all types combined</option>
<option value="GC">[GC] Condition, road surface (coded, see Table 1)</option>
<option value="GD">[GD] Frost depth, depth of frost penetration, non permafrost (IN, CM)</option>
<option value="GL">[GL] Salt content on a surface (e.g., road) (%)</option>
<option value="GP">[GP] Frost, depth of pavement surface (IN, CM)</option>
<option value="GR">[GR] Frost report, structure (coded, see Table 16)</option>
<option value="GS">[GS] Ground state (coded, see Table 18)</option>
<option value="GT">[GT] Frost, depth of surface frost thawed (IN, CM)</option>
<option value="GW">[GW] Frost, depth of pavement surface frost thawed (IN, CM)</option>
<option value="HA">[HA] Height of reading, altitude above surface (FT, M)</option>
<option value="HB">[HB] Depth of reading below surface, or to water table or groundwater (FT, M)</option>
<option value="HC">[HC] Height, ceiling (FT, M)</option>
<option value="HD">[HD] Height, head (FT, M)</option>
<option value="HE">[HE] Height, regulating gate (FT, M)</option>
<option value="HF">[HF] Elevation, project powerhouse forebay (FT, M)</option>
<option value="HG">[HG] Height, river stage (FT, M)</option>
<option value="HH">[HH] Height of reading, elevation in MSL (FT, M)</option>
<option value="HI">[HI] Stage trend indicator (coded, see Table 19)</option>
<option value="HJ">[HJ] Height, spillway gate (FT, M)</option>
<option value="HK">[HK] Height, lake above a specified datum (FT, M)</option>
<option value="HL">[HL] Elevation, natural lake (FT, M)</option>
<option value="HM">[HM] Height of tide, MLLW (FT, M)</option>
<option value="HN">[HN] (S) Height, river stage, daily minimum, translates to HGIRZNZ (FT, M)</option>
<option value="HO">[HO] Height, flood stage (FT, M)</option>
<option value="HP">[HP] Elevation, pool (FT, M)</option>
<option value="HQ">[HQ] Distance from a ground reference point to the river's edge used to estimate stage (coded, see Chapter 7.4.6)</option>
<option value="HR">[HR] Elevation, lake or reservoir rule curve (FT, M)</option>
<option value="HS">[HS] Elevation, spillway forebay (FT, M)</option>
<option value="HT">[HT] Elevation, project tail water stage (FT, M)</option>
<option value="HU">[HU] Height, cautionary stage (FT, M)</option>
<option value="HV">[HV] Depth of water on a surface (e.g., road) (IN, MM)</option>
<option value="HW">[HW] Height, spillway tail water (FT, M)</option>
<option value="HX">[HX] (S) Height, river stage, daily maximum, translates to HGIRZXZ (FT, M)</option>
<option value="HY">[HY] (S) Height, river stage at 7 a.m. local just prior to date-time stamp, translates to HGIRZZZ at 7 a.m. local time (FT, M)</option>
<option value="HZ">[HZ] Elevation, freezing level (KFT, KM)</option>
<option value="IC">[IC] Ice cover, river (%)</option>
<option value="IE">[IE] Extent of ice from reporting area, upstream “+,” downstream - (MI, KM)</option>
<option value="IO">[IO] Extent of open water from reporting area, downstream “+,” upstream - (FT, M)</option>
<option value="IR">[IR] Ice report type, structure, and cover (coded, see Table 14)</option>
<option value="IT">[IT] Ice thickness (IN, CM)</option>
<option value="LA">[LA] Lake surface area (KAC,KM2)</option>
<option value="LC">[LC] Lake storage volume change (KAF,MCM)</option>
<option value="LS">[LS] Lake storage volume (KAF,MCM)</option>
<option value="MD">[MD] Dielectric Constant at depth, paired value vector (coded, see Chapter 7.4.6 for format)</option>
<option value="MI">[MI] Moisture, soil index or API (IN, CM)</option>
<option value="ML">[ML] Moisture, lower zone storage (IN, CM)</option>
<option value="MM">[MM] Fuel moisture, wood (%)</option>
<option value="MN">[MN] Soil Salinity at depth, paired value vector (coded, see Chapter 7.4.6 for format)</option>
<option value="MS">[MS] Soil Moisture amount at depth (coded, see Chapter 7.4.6)</option>
<option value="MT">[MT] Fuel temperature, wood probe (DF, DC)</option>
<option value="MU">[MU] Moisture, upper zone storage (IN, CM)</option>
<option value="MV">[MV] Water Volume at Depth, paired value vector (coded, see Chapter 7.4.6 for format)</option>
<option value="MW">[MW] Moisture, soil, percent by weight (%)</option>
<option value="NC">[NC] River control switch (0=manual river control, 1=open river uncontrolled)</option>
<option value="NG">[NG] Total of gate openings (FT, M)</option>
<option value="NL">[NL] Number of large flash boards down (whole number)</option>
<option value="NN">[NN] Number of the spillway gate reported (used with HP, QS)</option>
<option value="NO">[NO] Gate opening for a specific gate (coded, see Chapter 7.4.6)</option>
<option value="NS">[NS] Number of small flash boards down (whole number)</option>
<option value="PA">[PA] Pressure, atmospheric (IN-HG, KPA)</option>
<option value="PC">[PC] Precipitation, accumulator (IN, MM)</option>
<option value="PD">[PD] Pressure, atmospheric net change during past 3 hours (IN-HG, KPA)</option>
<option value="PE">[PE] Pressure, characteristic, NWS Handbook #7, table 10.7</option>
<option value="PF">[PF] (S) Precipitation, flash flood guidance, precipitation to initiate flooding, translates to PPTCF for 3-hour intervals (IN, MM)</option>
<option value="PJ">[PJ] Precipitation, departure from normal (IN, MM)</option>
<option value="PL">[PL] Pressure, sea level (IN-HG, KPA)</option>
<option value="PM">[PM] Probability of measurable precipitation (dimensionless) (coded, see Table 22)</option>
<option value="PN">[PN] Precipitation normal (IN, MM)</option>
<option value="PP">[PP] Precipitation (includes liquid amount of new snowfall), actual increment (IN, MM)</option>
<option value="PR">[PR] Precipitation rate (IN/day, MM/day)</option>
<option value="PT">[PT] Precipitation, type (coded, see Table 17)</option>
<option value="PY">[PY] (S) Precipitation, increment ending at 7 a.m. local just prior to date-time stamp, translates to PPDRZZZ at 7 a.m. local time (IN, MM)</option>
<option value="QA">[QA] Discharge, adjusted for storage at project only (KCFS, CMS)</option>
<option value="QB">[QB] Runoff depth (IN, MM)</option>
<option value="QC">[QC] Runoff volume (KAF, MCM)</option>
<option value="QD">[QD] Discharge, canal diversion (KCFS, CMS)</option>
<option value="QE">[QE] Discharge, percent of flow diverted from channel (%)</option>
<option value="QF">[QF] Discharge velocity (MPH, KPH)</option>
<option value="QG">[QG] Discharge from power generation (KCFS, CMS)</option>
<option value="QI">[QI] Discharge, inflow (KCFS, CMS)</option>
<option value="QL">[QL] Discharge, rule curve (KCFS, CMS)</option>
<option value="QM">[QM] Discharge, preproject conditions in basin (KCFS, CMS)</option>
<option value="QN">[QN] (S) Discharge, minimum flow, translates to QRIRZNZ (KCFS, CMS)</option>
<option value="QP">[QP] Discharge, pumping (KCFS, CMS)</option>
<option value="QR">[QR] Discharge, river (KCFS, CMS)</option>
<option value="QS">[QS] Discharge, spillway (KCFS, CMS)</option>
<option value="QT">[QT] Discharge, computed total project outflow (KCFS, CMS)</option>
<option value="QU">[QU] Discharge, controlled by regulating outlet (KCFS, CMS)</option>
<option value="QV">[QV] Cumulative volume increment (KAF, MCM)</option>
<option value="QX">[QX] (S) Discharge, maximum flow, translates to QRIRZXZ (KCFS, CMS)</option>
<option value="QY">[QY] (S) Discharge, river at 7 a.m. local just prior to date-time stamp translates to QRIRZZZ at 7 a.m. local time (KCFS, CMS)</option>
<option value="QZ">[QZ] Reserved</option>
<option value="RA">[RA] Radiation, albedo (%)</option>
<option value="RI">[RI] Radiation, accumulated incoming solar over specified duration in langleys (LY)</option>
<option value="RN">[RN] Radiation, net radiometers (watts/meter squared)</option>
<option value="RP">[RP] Radiation, sunshine percent of possible (%)</option>
<option value="RT">[RT] Radiation, sunshine hours (HRS)</option>
<option value="RW">[RW] Radiation, total incoming solar radiation (watts/meter squared)</option>
<option value="SA">[SA] Snow, areal extent of basin snow cover (%)</option>
<option value="SB">[SB] Snow, Blowing Snow Sublimation (IN)</option>
<option value="SD">[SD] Snow, depth (IN, CM)</option>
<option value="SE">[SE] Snow, Average Snowpack Temperature (DF)</option>
<option value="SF">[SF] Snow, depth, new snowfall (IN, CM)</option>
<option value="SI">[SI] Snow, depth on top of river or lake ice (IN, CM)</option>
<option value="SL">[SL] Snow, elevation of snow line (KFT, M)</option>
<option value="SM">[SM] Snow, Melt (IN)</option>
<option value="SP">[SP] Snowmelt plus rain (IN)</option>
<option value="SR">[SR] Snow report, structure, type, surface, and bottom (coded, see Table 15)</option>
<option value="SS">[SS] Snow density (IN SWE/IN snow, CM SWE/CM snow)</option>
<option value="ST">[ST] Snow temperature at depth measured from ground (See Chapter 7.4.6 for format)</option>
<option value="SU">[SU] Snow, Surface Sublimation (IN)</option>
<option value="SW">[SW] Snow, water equivalent (IN, MM)</option>
<option value="TA">[TA] Temperature, air, dry bulb (DF,DC)</option>
<option value="TB">[TB] Temperature in bare soil at depth (coded, see Chapter 7.4.6 for format)</option>
<option value="TC">[TC] Temperature, degree days of cooling, above 65 DF or 18.3 DC (DF,DC)</option>
<option value="TD">[TD] Temperature, dew point (DF,DC)</option>
<option value="TE">[TE] Temperature, air temperature at elevation above MSL (See Chapter 7.4.6 for format)</option>
<option value="TF">[TF] Temperature, degree days of freezing, below 32 DF or 0 DC (DF,DC)</option>
<option value="TH">[TH] Temperature, degree days of heating, below 65 DF or 18.3 DC (DF,DC)</option>
<option value="TJ">[TJ] Temperature, departure from normal (DF, DC)</option>
<option value="TM">[TM] Temperature, air, wet bulb (DF,DC)</option>
<option value="TN">[TN] (S) Temperature, air minimum, translates to TAIRZNZ (DF,DC)</option>
<option value="TP">[TP] Temperature, pan water (DF,DC)</option>
<option value="TR">[TR] Temperature, road surface (DF,DC)</option>
<option value="TS">[TS] Temperature, bare soil at the surface (DF,DC)</option>
<option value="TV">[TV] Temperature in vegetated soil at depth (coded, see Chapter 7.4.6 for format)</option>
<option value="TW">[TW] Temperature, water (DF,DC)</option>
<option value="TX">[TX] (S) Temperature, air maximum, translates to TAIRZXZ (DF,DC)</option>
<option value="TZ">[TZ] Temperature, Freezing, road surface (DF,DC)</option>
<option value="UC">[UC] Wind, accumulated wind travel (MI,KM)</option>
<option value="UD">[UD] Wind, direction (whole degrees)</option>
<option value="UE">[UE] Wind, standard deviation (Degrees)</option>
<option value="UG">[UG] Wind, gust at observation time (MI/HR,M/SEC)</option>
<option value="UH">[UH] Wind gust direction associated with the wind gust (in tens of degrees)</option>
<option value="UL">[UL] Wind, travel length accumulated over specified (MI,KM)</option>
<option value="UP">[UP] Peak wind speed (MPH)</option>
<option value="UQ">[UQ] Wind direction and speed combined (SSS.SDDD), a value of 23.0275 would indicate a wind of 23.0 mi/hr from 275 degrees</option>
<option value="UR">[UR] Peak wind direction associated with peak wind speed (in tens of degrees)</option>
<option value="US">[US] Wind, speed (MI/HR,M/SEC)</option>
<option value="UT">[UT] Minute of the peak wind speed (in minutes past the hour, 0-59)</option>
<option value="VB">[VB] Voltage - battery (volt)</option>
<option value="VC">[VC] Generation, surplus capacity of units on line (megawatts)</option>
<option value="VE">[VE] Generation, energy total (megawatt hours)</option>
<option value="VG">[VG] Generation, pumped water, power produced (megawatts)</option>
<option value="VH">[VH] Generation, time (HRS)</option>
<option value="VJ">[VJ] Generation, energy produced from pumped water (megawatt hours)</option>
<option value="VK">[VK] Generation, energy stored in reservoir only (megawatt * “duration”)</option>
<option value="VL">[VL] Generation, storage due to natural flow only (megawatt * “duration”)</option>
<option value="VM">[VM] Generation, losses due to spill and other water losses (megawatt * “duration”)</option>
<option value="VP">[VP] Generation, pumping use, power used (megawatts)</option>
<option value="VQ">[VQ] Generation, pumping use, total energy used (megawatt hours)</option>
<option value="VR">[VR] Generation, stored in reservoir plus natural flow, energy potential (megawatt * “duration”)</option>
<option value="VS">[VS] Generation, station load, energy used (megawatt hours)</option>
<option value="VT">[VT] Generation, power total (megawatts)</option>
<option value="VU">[VU] Generator, status (encoded)</option>
<option value="VW">[VW] Generation station load, power used (megawatts)</option>
<option value="WA">[WA] Water, dissolved nitrogen & argon (PPM, MG/L)</option>
<option value="WC">[WC] Water, conductance (uMHOS/CM)</option>
<option value="WD">[WD] Water, piezometer water depth (IN, CM)</option>
<option value="WG">[WG] Water, dissolved total gases, pressure (IN-HG, MM-HG)</option>
<option value="WH">[WH] Water, dissolved hydrogen sulfide (PPM, MG/L)</option>
<option value="WL">[WL] Water, suspended sediment (PPM, MG/L)</option>
<option value="WO">[WO] Water, dissolved oxygen (PPM, MG/L)</option>
<option value="WP">[WP] Water, ph (PH value)</option>
<option value="WS">[WS] Water, salinity (parts per thousand, PPT)</option>
<option value="WT">[WT] Water, turbidity (JTU)</option>
<option value="WV">[WV] Water, velocity (FT/SEC, M/SEC)</option>
<option value="WX">[WX] Water, Oxygen Saturation (%)</option>
<option value="WY">[WY] Water, Chlorophyll (ppb, ug/L)</option>
<option value="XC">[XC] Total sky cover (tenths)</option>
<option value="XG">[XG] Lightning, number of strikes per grid box (whole number)</option>
<option value="XL">[XL] Lightning, point strike, assumed one strike at transmitted latitude and longitude (whole number)</option>
<option value="XP">[XP] Weather, past NWS synoptic code (see Appendix D)</option>
<option value="XR">[XR] Humidity, relative (%)</option>
<option value="XU">[XU] Humidity, absolute (grams/FT3,grams/M3)</option>
<option value="XV">[XV] Weather, visibility (MI, KM)</option>
<option value="XW">[XW] Weather, present NWS synoptic code (see Appendix C)</option>
<option value="YA">[YA] Number of 15-minute periods a river has been above a specified critical level (whole number)</option>
<option value="YC">[YC] Random report sequence number (whole number)</option>
<option value="YF">[YF] Forward power, a measurement of the DCP, antenna, and coaxial cable (watts)</option>
<option value="YI">[YI] SERFC unique</option>
<option value="YP">[YP] Reserved Code</option>
<option value="YR">[YR] Reflected power, a measurement of the DCP, antenna, and coaxial cable (watts)</option>
<option value="YS">[YS] Sequence number of the number of times the DCP has transmitted (whole number)</option>
<option value="YT">[YT] Number of 15-minute periods since a random report was generated due to an increase of 0.4 inch of precipitation (whole number)</option>
<option value="YU">[YU] GENOR raingage status level 1 - NERON observing sites (YUIRG)</option>
<option value="YV">[YV] A Second Battery Voltage (NERON sites ONLY), voltage 0 (YVIRG)</option>
<option value="YW">[YW] GENOR raingage status level 2 - NERON observing sites (YWIRG)</option>
<option value="YY">[YY] GENOR raingage status level 3 - NERON observing sites (YYIRG)</option>
<option value="YZ">[YZ] Time of Observation – Minutes of the calendar day, minutes 0 - NERON observing sites (YZIRG)</option>
</select>	
		
&nbsp; &nbsp; <strong>Duration:</strong>
<select onChange="javascript: updateMap();" id="duration">
	<option value="D">D Day (24 Hour)</option>
	<option value="I">I Instantaneous</option>
	<option value="Q">Q 6 Hour</option>
</select>	

&nbsp; <strong>Within # of Days:</strong> <input id="days" onChange="javascript: updateMap();" type="text" size="5" name="days" value="2">

</form>
</div></div>

		
<div id="map" class="map">
<div id="popup"></div>
</div>

EOF;

$t->render('full.phtml');
?>