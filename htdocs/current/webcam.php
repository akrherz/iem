<?php
/* 
 * This is an Extjs application that allows historical and current viewing of
 * webcam images.
 */
require_once "../../config/settings.inc.php";
define("IEM_APPID", 9);
require_once "../../include/myview.php";

$t = new MyView();
$t->headextra = <<<EOM
<link rel="stylesheet" type="text/css" href="https://extjs.cachefly.net/ext/gpl/5.0.0/build/packages/ext-theme-neptune/build/resources/ext-theme-neptune-all.css"/>
<link rel="stylesheet" type="text/css" href="webcam.css"/>
EOM;
$t->jsextra = <<<EOM
<script type="text/javascript" src="https://extjs.cachefly.net/ext/gpl/5.0.0/build/ext-all.js"></script>
<script type='text/javascript' src='webcam.js'></script>
EOM;
$t->title = "Webcams";
$t->content = <<<EOM
<div class="row">
  <div class="col-md-12">
    <h3><i class="fa fa-camera"></i> Web Camera Interactive Viewer</h3>
    <p class="lead">
      View current and historical webcam imagery from across Iowa. 
      Switch to archived mode to browse historical images.
    </p>
  </div>
</div>

<div class="row">
  <div class="col-md-12">
    <div id="main" style="height: 700px;"></div>
  </div>
</div>

<div class="row mt-3">
  <div class="col-md-12">
    <div class="card">
      <div class="card-header">
        <button class="btn btn-link p-0" type="button" data-bs-toggle="collapse" 
                data-bs-target="#helpContent" aria-expanded="false" aria-controls="helpContent">
          <i class="fa fa-info-circle"></i> Help & Cool Archived Images
        </button>
      </div>
      <div class="collapse" id="helpContent">
        <div class="card-body">
          <p>This application provides an interactive view of current and historical
          web camera imagery. Click on the 'Real Time' button above to switch the
          application into 'Archived Mode'. You can then select the time of interest
          and the application will automatically update to show you the images. The IEM has archived images every 5 minutes, but may have an image every minute during active weather.</p>
          
          <h5>Cool Archived Images:</h5>
          <ul>
           <li><a class="ccool" href="#" data-opt="KCCI-200406120032">11 Jun 2004 - 7:32 PM, Webster City Tornado</a></li>
           <li><a class="ccool" href="#" data-opt="KCCI-200505270115">26 May 2005 - 7:15 PM, Pella Double Rainbow</a></li>
           <li><a class="ccool" href="#" data-opt="KCCI-200506090255">8 Jun 2005 - 8:55 PM, All sorts of colours</a></li>
           <li><a class="ccool" href="#" data-opt="KCCI-200509081730">8 Sep 2005 - 12:30 PM, Blurry shot of Ames Tornado</a></li>
           <li><a class="ccool" href="#" data-opt="KCCI-200511122238">12 Nov 2005 - 4:38 PM, Woodward tornado from Madrid</a></li>
           <li><a class="ccool" href="#" data-opt="KCCI-200511122300">12 Nov 2005 - 5:00 PM, Ames tornado</a></li>
           <li><a class="ccool" href="#" data-opt="KCCI-200607172150">17 Jul 2006 - 4:50 PM, Tama possible brief tornado</a></li>
           <li><a class="ccool" href="#" data-opt="KCCI-200710022256">2 Oct 2007 - 5:56 PM, Twin Cedars possible tornado</a></li>
           <li><a class="ccool" href="#" data-opt="KCCI-200808310120">30 Aug 2008 - 8:20 PM, Interesting Sunset Halos</a></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</div>

EOM;
$t->render('full.phtml');
