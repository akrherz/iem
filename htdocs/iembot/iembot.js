    var rooms = new Array();
    var activeRoom = "";
    var theDate = new Date();
    var ccount = 0;
    // Generic object to store last update times
    var dsLast = new Object();

    function leadingZero(nr)
    {
	  if (nr < 10) nr = "0" + nr;
	  return nr;
    }
    function leadingZeroTwo(nr)
    {
	  if (nr < 10) return "00" + nr;
	  if (nr < 100) return "0" + nr;
	  return nr;
    }

function toTicks(s)
{
    //alert(s); exit();
    var d = new Date();
    d.setYear( parseInt(s.substring(0,4)) );
    d.setMonth( parseInt(s.substring(4,6),10) - 1 );
    d.setDate( parseInt(s.substring(6,8),10) );
    d.setHours( parseInt(s.substring(8,10),10) );
    d.setMinutes( parseInt(s.substring(10,12),10) );
    d.setSeconds( parseInt(s.substring(12,14),10) );
    //d.setMilliseconds( parseInt(s.substring(15,18)) );
    return d;
}

function makeRPCCall(roomname) {
    if (! document.getElementById(roomname +"_log")) { return; }

    eval("var lastUpdate = dsLast."+roomname);
    iembot.getUpdate.userdata = roomname;
    iembot.getUpdate(roomname, lastUpdate);
    var now = new Date();
    document.getElementById( roomname +"_time").innerHTML = now.getHours() +":"+ leadingZero(now.getMinutes()) +":"+ leadingZero(now.getSeconds());

}

function updateCB(rslt, state, extra) {
  var roomname = extra.userdata;
  if(state != __RPC_SUCCESS__) {
    return; 
  }
  for (var i=0; i < rslt.length; i++)
  {
    if (rslt[i].length == 0){ continue; }
    var a = document.createElement('div');
    a.className = 'message';
    a.style.border = '1px';
    if (i == (rslt.length -1) ) { 
      eval("dsLast."+roomname +" = "+ rslt[i][0] ); 
    }
	if (document.myForm.iembot.checked && rslt[i][2] == "iembot") { continue; }
    if (roomname != activeRoom){ document.getElementById( roomname +"_control").style.background = "#c00"; }
    var logDate = new Date( toTicks(rslt[i][1])  - (theDate.getTimezoneOffset() * 60000) );
    var mess = rslt[i][3];

    mess = mess.replace(/&amp;/g, '&').replace(/href/g, 'target="_new" href');
    var nn = " &lt;"+ rslt[i][2] +"&gt; ";
    if (roomname == "peopletalk"){ nn = " "; }
    a.innerHTML =  (logDate.getMonth() +1) +"/"+ logDate.getDate() +" "+ logDate.getHours() +":"+ leadingZero(logDate.getMinutes()) +":"+ leadingZero(logDate.getSeconds()) + nn + mess ;
    document.getElementById( roomname +"_log").insertBefore(a, document.getElementById( roomname +"_log").firstChild);
  }
  ccount -= 1;
}

function botcaller(roomname)
{
  if (! document.getElementById(roomname +"_log")) { return; }
  if (ccount > 1000)
  { 
    alert("Connection Error limit reached, please reload the page. Sorry!");
    return;
  }
  ccount += 1;
  setTimeout("botcaller('"+roomname+"')", 7000);
  setTimeout("makeRPCCall('"+roomname+"')", 5000);
}



function clearRoom()
{
  if (activeRoom == ""){
   alert("ERROR: No room visible for clearing.");
  } else {
    document.getElementById( activeRoom +"_log").innerHTML = "";
  }
}

function switcher( toRoom ) 
{
    if (activeRoom != "" && document.getElementById( activeRoom +"_control")) {
      document.getElementById( activeRoom +"_control").style.background = "#eee";
    }
    activeRoom = toRoom;
    for (var i=0; i < rooms.length; i++){
      document.getElementById( rooms[i] +"_log").style.display = "none";
    }
    document.getElementById( toRoom +"_control").style.background = "#0c0";
    document.getElementById( toRoom +"_log").style.display = "block";

}

//setTimeout('document.location=document.location',300000);

function removeRoom(roomname)
{
  var node = document.getElementById(roomname + '_control');
  node.parentNode.removeChild(node);
  var node = document.getElementById(roomname + '_log');
  node.parentNode.removeChild(node);
  for (var i=0; i < rooms.length; i++){
    if (rooms[i] == roomname){ rooms.splice(i,1); }
  }
  if (rooms.length > 0)
  {
    switcher( rooms[0] );
  }
}

function addRoom(roomname)
{
  eval("dsLast."+roomname +" = 0;");
  
  var tabrow = document.getElementById( 'tabrow' );
  var s = document.createElement('div');
  s.id = roomname +"_control";
  s.style.cssFloat = "left";
  s.style.styleFloat = "left";
  //s.style.clear = "none";
  s.style.background = "#c00";
  s.style.padding = "5px";
  //s.style.width = "2";
  
  s.innerHTML = "<a href=\"javascript: switcher('"+ roomname +"');\">"+ roomname +"</a> [<a href=\"javascript: removeRoom('"+roomname+"');\">x</a>]<br /><div id=\""+ roomname +"_time\">Updating</div>";
  tabrow.appendChild(s);

  var logwindow = document.getElementById( 'logwindow' );
  s = document.createElement('div');
  s.id = roomname +"_log";
  s.style.display = "none";
  //t = document.createTextNode(roomname);
  //s.appendChild(t);
  s.innerHTML = "";
  logwindow.appendChild(s);

  ccount += 1;
  setTimeout("makeRPCCall('"+roomname+"')", 100);
  setTimeout("botcaller('"+roomname+"')", 500);
}

function addWFO()
{
  var idx = document.myForm.wfo.selectedIndex;
  var newRoom = document.myForm.wfo.options[idx].value;
  for (var i=0; i < rooms.length; i++){
    if (rooms[i] == newRoom){ return; }
  }
  rooms[rooms.length ] = newRoom;
  addRoom( newRoom );
  switcher( newRoom);
}
