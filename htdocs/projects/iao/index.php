<?php 
require_once "../../../config/settings.inc.php";

require_once "../../../include/myview.php";

$t = new MyView();
$t->title = "Iowa Atmospheric Observatory";
$t->headextra = <<<EOM
<style>
div.hangs p {
  padding-left: 22px ;
  text-indent: -22px ;
}
</style>
EOM;
$t->content = <<<EOF

<h3>Iowa Atmospheric Observatory</h3>

<h4>Overview</h4>

<p>The Iowa Atmospheric Observatory (IAO) was designed and constructed by 
Iowa State University under funding from the National Science 
Foundation Iowa EPSCoR grant (Grant # 1101284).  This distributed 
facility is anchored by its two tall (120-m) towers separated by 
22 km operating continuously since June 2016 in central Iowa.   
Associated short-term field research and teaching activities and 
their associated field observing facilities are deployed for specific 
intensive observing periods (IOPs) or longer term studies.  
Remote sensing instruments also have been and will be deployed for IOPs 
and continuously as new projects develop.</p>

<p>The agricultural landscape surrounding each tower is flat 
(with elevation changes of about +/- 3 m per square mile), 
and the land-use is predominantly (~90%) intensely managed row crops, 
either corn (mature height 1.5-2.0 m) or soybeans ((1.0 m) during the 
growing season.  A few farmsteads of area 2-3 acres (~1 hectare) dot the 
landscape (`1-2 per square mile) consisting of a few 1-2 story buildings 
surrounded by trees typically of height 20-30 ft.  Crops are planted in 
April-May and harvested in September-October.  Outside this growing season 
the landscape is bare with some crop residue giving surface roughness 
elements (not zo) of ~ 5-8 cm.  The Story County tower has grass 
(height ~0.2-0.8 m) in the immediate vicinity (1 hectare) of the tower.</p>
		

<p><a href="http://talltowers.agron.iastate.edu">Tall Towers Project Website</a></p>

<h4>Meteorological Data @ 1 Second Resolution</h4>

<p>A <a href="analog_download.php">download interface</a> exists to request
	this data.  You can also <a href="/plotting/auto/?q=158">generate interactive plots</a>
	of this dataset.</p>
		
<h4>Turbulence Data @ 20 Hertz Resolution</h4>

<p>This information is currently only available in NetCDF files.  If you would
like access to them, please email <a href="mailto:gstakle@iastate.edu">Dr Takle (gstakle@iastate.edu)</a>.</p>




<h4>Acknowledgements</h4>

<p>The IAO towers and associated instrumentation were funded by an 
NSF/EPSCoR grant to the state of Iowa (Grant # 1101284) and as well as 
a follow-on NSF/AGS grant #1701278.  The second of these grant requests was 
successful in part due to key exploratory funding and contributions from 
seed grants from the Ames Laboratory/USDOE and the Center for Global and 
Regional Environmental Research.  In-kind contributions for pre-construction 
exploratory research were provided by the National Renewable Energy 
Laboratory and the University of Colorado (J. Lundquist), the National 
Laboratory for Agriculture and the Environment, and the National Center 
for Atmospheric Research.  These contributions made possible the 
Crop/Wind-energy Experiments (CWEX-10, CWEX-11, CWEX-12, and CWEX-13).</p>


<h3>Publications from the Crop/Wind-energy Experiments and the Iowa Atmospheric Observatory</h3>

<div class="hangs">
<p>Takle, E. S., 2017: Climate. In M. Perrow, ed., 2017:  
Wildlife and Wind Farms – Conflicts and Solutions. Volume I. 
Onshore Potential Effects.  Pelagic Publishing. 298 pp. ISBN 9781784271190.</p>

<p>Takle, E. S., D. A Rajewski, and S. I. Purdy, 2017:  
The Iowa Atmospheric Observatory: Revealing the unique boundary-layer 
characteristics of a wind farm.  Earth Interactions in review</p>

<p>Rajewski, Daniel A., Eugene S. Takle, John H. Prueger, and 
Russell K. Doorenbos, 2016:  Toward understanding the physical 
link between turbines and microclimate impacts from in situ 
measurements in a large wind farm.  J. Geophys. Res. Atmos., 121, 
<a href="http://onlinelibrary.wiley.com/doi/10.1002/2016JD025297/abstract">doi:10.1002/2016JD025297</a></p>

<p>Vanderwende, Brian J., Julie K. Lundquist, Michael E. Rhodes, 
Eugene S. Takle, and Samantha Irvin, 2015:  Observing and simulating the 
summertime low-level jet in central Iowa.  Mon. Wea. Rev., 143, 2319-2339.</p>

<p>Takle,  E S., D. A. Rajewski, J. K. Lundquist, W. A. Gallus, Jr., and 
A. Sharma, 2014:  Measurements in support of wind farm simulations and 
power forecasts:  The Crop/Wind-energy Experiments (CWEX).  The Science of 
Making Torque From Wind, 2014. Journal of Physics: Conference Series, 524 
(2014) 012174  <a href="http://iopscience.iop.org/1742-6596/524/1/012174">doi:10.1088/1742-6596/524/1/012174</a>.</p>

<p>Lundquist, Julie K., Eugene S. Takle, Matthieu Boquet, 
Branko Kosović, Michael E. Rhodes, Daniel Rajewski, Russell Doorenbos, 
Samantha Irvin, Matthew L. Aitken, Katja Friedrich, Paul T. Quelet, 
Jiwan Rana, Clara St. Martin, Brian Vanderwende, and Rochelle Worsnop, 
2014:  Lidar observations of interacting wind turbine wakes in an onshore wind 
farm. The Science of Making Torque From Wind, 2014.  <a href="http://iopscience.iop.org/1748-9326/7/1/014005">Available online</a>.</p>

<p>Rajewski, D.A., Eugene S. Takle, Julie K. Lundquist, John H. 
Prueger, Michael E. Rhodes, Richard Pfeiffer, Jerry L. Hatfield, 
Kristopher K. Spoth, Russell K. Doorenbos, 2014:  Changes in fluxes of 
heat, H2O, and CO2 caused by a large wind farm.  Agric. and For. Meteor., 
194, 175-187. <a href="http://www.sciencedirect.com/science/article/pii/S0168192314000914">DOI: 10.1016/j.agrformet.2014.03.023</a></p>

<p>Rajewski, D. A., Eugene S. Takle, Julie K. Lundquist, Steven Oncley, 
John H. Prueger, Thomas W. Horst, Michael E. Rhodes, Richard Pfeiffer, 
Jerry L. Hatfield, Kristopher K. Spoth, and Russell K. Doorenbos, 2013:  
CWEX:  Crop/Wind-energy Experiment: Observations of surface-layer, 
boundary-layer and mesoscale interactions with a wind farm.  
Bull. Amer. Meteor. Soc., 94, 655-672.  <a href="http://journals.ametsoc.org/doi/abs/10.1175/BAMS-D-11-00240.1">doi: 10.1175/BAMS-D-11-00240</a></p>
</div>

<h3>Presentations from the Crop/Wind-energy Experiments and the Iowa Atmospheric Observatory</h3>

<div class="hangs">
<p>Takle, E. S., R. A. Rajewski, S. L. Purdy, J. Sun, and S. Zilitinkevich, 2017:  Exchanges to surface and boundary layer reconsidered:  Introducing FaNTASTIC-1.  International Conference on Future Technologies for Wind Energy.  Boulder CO, October 2017.
<p>Rajewski, D. A., E. S. Takle, and S. L. Purdy, 2017:  Tall tower measurements of wake loss characteristics within a low-density wind farm.  International Conference on Future Technologies for Wind Energy.  Boulder CO, October 2017.
<p>Takle, Eugene S., Daryl Herzmann, and Dan Rajewski, 2016:  Wind-farm power production diagnostic tools with applications to wake steering.  Invited presentation.  National Renewable Energy Laboratory (DOE), Boulder CO
<p>Takle, Eugene S., Daryl Herzmann, and Dan Rajewski, 2016:  Power-production diagnostic tools for low-density wind farms with applications to wake steering. Amer. Geophys Union Fall Meeting.  San Francisco.   December
<p>Takle, E. S., 2017:  Wind Energy:  An outdoor laboratory has been established to collect reliable wind speed and turbulence data for use with computational models of wind turbine systems.  Poster displayed at the EPSCoR Legislator Breakfast at the Iowa Statehouse.
<p>Takle, E. S., D. A. Rajewski, and S. L. Irvin, 2017:  Identical twin towers for studies of natural turbuence and wind farm boundary layers.  8th Conf. on Wea., Climate, Water and the New Energy Economy, 23 Jan., Amer. Meteor. Soc., Seattle, WA.
<p>Rajewski, Daniel A., Eugene S. Takle, Julie K. Lundquist, Samantha L. Irvin, and Russell K. Doorenbos, 2015:  Spatial characteristics of power variability from a large wind farm in Iowa during the 2013 Crop/Wind Energy Experiment (CWEX-13).  Sixth Conference on Weather, Climate, and the New Energy Economy. American Meteorological Society. Phoenix, AZ
<p>Lundquist, Julie K., E. S. Takle, M. Boquet, B. Kosovic, M. E. Rhodes, D. A. Rajewski, R. K. Doorenbos, S. Irvin, M. Aitken, K. Friedrich, P. T. Quelet, J. Rana, C. St. Martin, B. J. Vanderwende, and R. Worsnop, 2014:  Lidar observations of the variation of wind turbine wakes with inflow conditions in an onshore wind farm.  21st Symposium on Boundary Layers and Turbulence.  American Meteorological Society.  Leeds, UK.
<p>Lundquist, J. K., E.S. Takle, M. Boquet, B. Kosovic, M.E. Rhodes, D. Rajewski, R. Doorenboos, S. Irvin, M.L. Aitken, K. Friedrich, P.T. Quelet, J. Rana, C. St. Martin, B. Vanderwende, W. Rochelle, Lidar observations of interacting wind turbine wakes in an onshore wind farm, European Wind Energy Association 2014. (2014) 33–36. 
<p>Selvaraj, S.,  A. Chaves, E. Takle and A. Sharma, “Numerical Prediction of Surface Flow Convergence Phenomenon in Windfarms” in Proc. of the Conference on Wind Energy Science and Technology, RUZGEM, Ankara, Turkey, Oct 3-4, 2013.
<p>Rajewski, D. A., E. S. Takle, J. H. Prueger, S. Oncley, J. K. Lundquist, T. W. Horst, M. E. Rhodes, R. L. Pfeiffer, J. L. Hatfield, K. K. Spoth, and R. Doorenbos, 2013:  Wind Turbine Wake Investigation from Surface Measurements during the 2010 and 2011 Crop Wind-Energy EXperiments (CWEX-10/11).  Fourth Conference on Weather, Climate, and the New Energy Economy.  American Meteorological Society.  Austin, TX.  
<p>Takle, E. S., D. A. Rajewski, J. Prueger, Steven Oncley, J. K. Lundquist, Thomas W. Horst, Michael E. Rhodes, Richard Pfeiffer, Jerry L. Hatfield, Kristopher K. Spoth, Russell K. Doorenbos, 2013:  CWEX-10/11:  Overview of Results From the First Two Crop/Wind-Energy Experiments.   Fourth Conference on Weather, Climate, and the New Energy Economy.  American Meteorological Society.  Austin, TX.  
<p>Takle, E. S., D. A. Rajewski, J. Prueger, Steven Oncley, J. K. Lundquist, Thomas W. Horst, Michael E. Rhodes, Richard Pfeiffer, Jerry L. Hatfield, Kristopher K. Spoth, Russell K. Doorenbos, 2012:  CWEX-10/11:  Overview of Results From the First Two Crop/Wind-Energy Experiments.  American Geophysical Union Fall Meeting, San Francisco.
<p>Rajewski, D. A.,  E. S. Takle, J. H. Prueger, S.P. Oncley, T. W. Horst, R. Pfeiffer, J. L. Hatfield, K. K. Spoth, R.K. Doorenbos, 2012:  Evaluation of surface energy and carbon fluxes within a large wind farm during the CWEX-10/11 Crop Wind-Energy eXperiments.  American Geophysical Union Fall Meeting, San Francisco.
<p>Rajewski, D. R., E. S. Takle, T. W. Horst, S. P. Oncley, J.K. Lundquist, M. E. Rhodes, and K. K. Spoth, 2012:  Crop-Wind-Energy Experiment 2011 (CWEX11).  16th Symposium on Meteorological Observation and Instrumentation.   Amer. Meteorol. Soc. 23-26 Janurary. New Orleans.  
<p>Takle, E. S., D. A. Rajewski, J. H. Prueger, J. K. Lundquist, M. Aitken, M. E. Rhodes, A. J. Deppe, F. E. Goodman, K. C. Carter, L. Mattison, S. L. Rabideau, A. J. Rosenberg, C. L. Whitfield, and J. Hatfield, 2010:  Wind and flux measurements in a windfarm co-located with agricultural production. Presented at the American Geophysical Union Fall Meeting, San Francisco.  (Invited presentation)
<p>Rhodes, M. E., , M. L. Aitken, J. K. Lundquist, E. S. Takle, and J. Prueger, 2010:  Effect of wind turbine wakes on cropland surface fluxes in the US Great Plains during a Nocturnal Low Level Jet.  Presented at the American Geophysical Union Fall Meeting, San Francisco.
<p>Takle, E. S., D. A. Rajewski, M. Segal, R. Elmore, J. Hatfield, J. H. Prueger, and S. E. Taylor, 2009:  Interaction of turbine-generated turbulence with agricultural crops:  conceptual framework and prelimnary results.  Presentation at American Geophysical Union Fall Meeting, San Francisco.
</div>


EOF;

$t->render('single.phtml');
?>