function addTime() {
  var d = new Date();
  document.form.tzoff.value=(d.getTimezoneOffset()*60);
}

function reverseLayer(lyr) {
  if ( document.getElementById ) {
    var w = document.getElementById(lyr);
    if (w.style.display == "none") { 
       w.style.display = "block"; 
      var w = document.getElementById("datawindow");
      w.style.top = "120px";
      w.style.left = "210px";
    }
    else { 
      w.style.display = "none"; 
      var w = document.getElementById("datawindow");
      w.style.top = "30px";
      w.style.left = "5px";
    }


  }
}

function handsOff2( ) {
  reverseLayer("iem-header");
  reverseLayer("iem-footer");
  reverseLayer("controls");
}

function handsOff( ) {
  reverseLayer("iem-header");
  reverseLayer("iem-footer");
  reverseLayer("controls");
  if (document.myform.autopilot.value == 1){
    document.myform.autopilot.value = 0;
  } else {
    document.myform.autopilot.value = 1;
  }
}
function showControl(layerName){
  setLayerDisplay("layers-control", 'none');
  setLayerDisplay("locations-control", 'none');
  setLayerDisplay("time-control", 'none');
  setLayerDisplay("options-control", 'none');
  setLayerDisplay(layerName, 'block');
}
function setLayerDisplay( layerName, d ) {
  if ( document.getElementById ) {
    var w = document.getElementById(layerName);
    w.style.display = d;
  }
}
