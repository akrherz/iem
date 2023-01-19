function addTime() {
  var d = new Date();
  document.form.tzoff.value=(d.getTimezoneOffset()*60);
}

function reverseLayer(lyr) {
  if ( document.getElementById ) {
    var w = document.getElementById(lyr);
    if (w.style.display == "none") { 
       w.style.display = "block";
      var w2 = document.getElementById("datawindow");
      w2.style.top = "120px";
      w2.style.left = "5px";
    }
    else { 
      w.style.display = "none"; 
      var w2 = document.getElementById("datawindow");
      w2.style.top = "5px";
      w2.style.left = "5px";
    }

  }
}

function handsOff2( ) {
  //reverseLayer("iem-header");
  //reverseLayer("iem-footer");
}

function handsOff( ) {
  //reverseLayer("iem-header");
  //reverseLayer("iem-footer");
  if (document.myform.autopilot.value == 1){
    document.myform.autopilot.value = 0;
  } else {
    document.myform.autopilot.value = 1;
  }
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
