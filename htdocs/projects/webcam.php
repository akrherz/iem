<?php 
require_once "../../config/settings.inc.php";
define("IEM_APPID", 98);
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "Webcam Project";

$t->content = <<<EOM
<h3>IEM Webcam Project</h3>

<p>One of the unique datasets collected by the IEM are weather webcam imagery.
These images provide very valuable data for folks interested in the current
weather conditions and archived!  Our webcam imagery dates back to 2003 with
images saved every 5 minutes for that period!</p>

<div class="row">
<div class="col-md-6">
<img src="/archive/data/2005/11/12/camera/KCCI-016/KCCI-016_200511122300.jpg"
		class="img img-responsive" />
<br />Webcam on the top of ISU Agronomy Hall capturing a tornado off to the
		north and west back on 12 Nov 2005.
</div>
<div class="col-md-6">
<object width="100%" height="350">
<param name="movie" value="https://youtube.com/v/yXnkzeCU3bE"></param>
<param name="wmode" value="transparent"></param>
<embed src="https://youtube.com/v/yXnkzeCU3bE" 
type="application/x-shockwave-flash" wmode="transparent" width="425" 
height="350"></embed></object>

<br />An awesome gravity wave lapse from near Tama, IA.  This lapse has over
		1 million views on YouTube!
</div>
</div>

<h4>Available Tools:</h4>
<ul>
	<li><a href="/current/webcam.php">Current/Archived Still Images</a>
		<br />This page contains a simple listing of webcam images</li>
	<li><a href="/current/viewer.phtml">High Resolution + Live</a>
		<br />This page contains the most recent captured image in its
		highest resolution and has an interactive map to select sites.</li>
	<li><a href="/current/bloop.phtml">Loops</a>
		<br />This page generates a timelapse for a webcam and period of your
		choice.</li>
	<li><a href="/current/camlapse/">Recent Movies</a>
		<br />For the webcam networks operated by KCCI, KCRG, and KELO, the
		IEM generates five timelapses per day for specific periods during
		each day.  These are used on-air and the most recent lapse is available
		online.</li>
	<li><a href="/cool/">Cool Lapses</a>
		<br />This page contains the best lapses that have been uploaded to
		<a href="https://youtube.com/akrherz">daryl's youtube channel</a>.</li>
</ul>

<h4>Frequently Asked Questions</h4>
		
<p><strong>What hardware are you using?</strong>
<br />The TV networks contain a mix of Canon VB-C10, VB-C50 and VB-C60 model
		webcams.  The newer webcams are Axis brand, due to the requirement for
		HD video.  These webcams are autonomous and only need Internet and
		power to work.  They run an embedded operating system / web server,
		which allows some
		<a href="https://github.com/akrherz/pyVBCam">custom software</a> to
		poll images from.</p>

<p><strong>What costs are involved?</strong>
<br />The physical hardware (mounting bracket, camera housing, and webcam)
		runs about $2,000.  There are cheaper options, but this is what we
		have traditionally seen sites use.  The power usage is neglegible
		and usually donated by the webcam's host.  The Internet requirements
		are for fast upload speeds as the webcam needs to serve out its
		imagery.  Having 1 megabit upload speed will provide a workable 
		video stream.  The IEM provides collection and archival services
		at no cost and without warranty.  There is no lock-in with our webcam
		collection software and so other tools can access the webcams at
		the same time we are polling for images to archive.</p>

<p><strong>We'd like to build a webcam network, can you help?</strong>
<br />In general, the IEM can not physically help with your construction
		of a webcam network, but can provide some guidance based on our
		experience.  Please <a href="/info/contacts.php">contact us</a>
		and let us know your interest!</p>

<p><strong>Where are the best places to mount a webcam?</strong>
<br />Great question!  You want a very stable and high location without
		tree or building obstruction.  Obvious places like communication
		towers are not the best due to shaking of the tower and they are
		typically full of other equipment.  Placing them on grain elevators
		is problematic due to dust and shaking.  Placing them at schools
		is diffcult as they often do not have a high view and their local
		ethernet networks can be difficult to work with.  We have had luck
		with municipal locations, like town squares, clock towers, and
		private downtown buildings.</p>
		
<p><strong>Which directions are the most important to see?</strong>
<br />Nearly all webcam houses create a blind spot whereby the webcam
		can not see past its housing mount.  Having this blind spot be to
		either your south or northeast is likely ideal as you can see
		passing storms to your north and the sun rise/setting.  Storms
		typically approach us from the west, so the west view is very
		important.  Supercell thunderstorms, the ones that produce high
		impact weather, are usually best seen will pointing the webcam
		southwest thru northwest thru northeast.  These are directions
		where the "meso" / "wall cloud" can be seen.</p>
EOM;
$t->render('single.phtml');
