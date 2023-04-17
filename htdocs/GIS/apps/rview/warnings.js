function addTime() {
  var d = new Date();
  document.form.tzoff.value=(d.getTimezoneOffset()*60);
}

function showControl(layerName){
  var oldval = document.getElementById(layerName).style.display;
  setLayerDisplay("layers-control", 'none');
  setLayerDisplay("locations-control", 'none');
  setLayerDisplay("time-control", 'none');
  setLayerDisplay("options-control", 'none');
  if (oldval == 'none'){
      setLayerDisplay(layerName, 'block');	  
  }
}
function setLayerDisplay( layerName, d ) {
  if ( document.getElementById ) {
    var w = document.getElementById(layerName);
    w.style.display = d;
  }
}
function flipLayerDisplay( layerName) {
  if ( document.getElementById ) {
    var w = document.getElementById(layerName);
    if (w.style.display == "none") { 
      w.style.display = "block";
    } else {
      w.style.display = "none";
    }
  }
}

$(document).ready(() => {
    $(".iemselect2").select2();
});
