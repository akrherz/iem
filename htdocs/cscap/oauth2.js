function xmlToString(xmlData) { 

    var xmlString;
    //IE
    if (window.ActiveXObject){
        xmlString = xmlData.xml;
    }
    // code for Mozilla, Firefox, Opera, etc.
    else{
        xmlString = (new XMLSerializer()).serializeToString(xmlData);
    }
    return xmlString;
}  

function updateRow(){
	$(entry).children().each(function(j,c){
    		if (c.nodeName == 'gsx:farmercode'){
    			$(c).text('victory');
    		}
	});
	uri = $($(entry).find('link[rel=edit]')).attr('href');
	$.ajax({ // ?sq=farmercode=1
  url: 'ajax-proxy.php?csurl='+ uri,
  headers: {
    'Authorization': 'Bearer ' + access_token
  },
  data : xmlToString(entry),
  processData : false,
  contentType: 'application/atom+xml',
  type : 'PUT',
  success: function(data, status) {
	alert("Saved your entry!");
  	}
  });
	
}

function addRow(){
	x = ['<entry xmlns="http://www.w3.org/2005/Atom"',
    'xmlns:gsx="http://schemas.google.com/spreadsheets/2006/extended">',
  '<gsx:state>1</gsx:state>',
  '<gsx:farmercode>3</gsx:farmercode>',
 '</entry>'].join(" ");

	$.ajax({ // ?sq=farmercode=1
  url: 'ajax-proxy.php?csurl='+ spreadkey,
  headers: {
    'Authorization': 'Bearer ' + access_token
  },
  data : x,
  processData : false,
  contentType: 'application/atom+xml',
  type : 'POST',
  success: function(data, status) {
	alert("added row!");
	updateRow();
  	}
  });
} // End of addRow

function getSpreadsheet(){
	$.ajax({ // ?sq=farmercode=1
  url: spreadkey,
  headers: {
    'Authorization': 'Bearer ' + access_token
  },
  success: function(data, status) {
  	console.log('yo');
    doc = $(data);
    farmercodes = [];
    doc.find('entry').each(function(i,x){
    	thisEntry = x;
    	$(x).children().each(function(j,c){
    		if (c.nodeName == 'gsx:farmercode'){
    			if ($(c).text() == '1'){
    				console.log("Found Entry!");
    				entry = thisEntry;
    			}
    			farmercodes.push( $(c).text() );
    		}
    	});
    });
    setSelector(farmercodes);
    }
  });
	
}

function setSelector(farmercodes){
	 var el = document.getElementById('farmerselector');

     for (i=0;i<farmercodes.length;i++){
         var opt = document.createElement("option");
         opt.text = farmercodes[i];
         opt.value = farmercodes[i];
         el.options.add(opt);
     }
}

function handleClientLoad() {
	console.log("handleClientLoad() called");
	  gapi.client.setApiKey(apiKey);
	  window.setTimeout(checkAuth,1);
	}

	function checkAuth() {
	  gapi.auth.authorize({client_id: clientId, scope: scopes, immediate: true}, handleAuthResult);
	}

	function handleAuthResult(authResult) {
	  var authorizeButton = document.getElementById('authorize-button');
	  if (authResult && !authResult.error) {
	  	access_token = authResult.access_token;
	  	getSpreadsheet();
	  	addRow();
	  	//service.setHeaders({'Authorization': 'Bearer '+ access_token});
	  	//service.getFeed('https://spreadsheets.google.com/feeds/list/0AqZGw0coobCxdE9wN2J4aVE1bUthdWFsWjNrYURHWGc/1/private/full', function(){ console.log('here'); }, function(){ console.log('there'); });
		// Subtract five minutes from expires_in to ensure timely refresh
		var authTimeout = (authResult.expires_in - 5 * 60) * 1000;
		setTimeout(checkAuth, authTimeout);
	    authorizeButton.style.visibility = 'hidden';

	    //gapi.client.load("drive", "v2", function(){
//
		//    });
	   //gapi.client.load("fusiontables", "v1", function(){
	    //	gapi.client.fusiontables.table.insert({'tableID':"1_rt_nw7XmSic3L7rbA5Ok9BbrVyrYiP9sIZRUj4"}, function(){ console.log('here');})
	    //});
	    //google.load("jquery", "1.7.1", {callback : function(){} });
	    //google.load("jqueryui", "1.8.16", {callback : function(){} });
	   

	  } else {
	    authorizeButton.style.visibility = '';
	    authorizeButton.onclick = handleAuthClick;
	  }
	}

	function handleAuthClick(event) {
	  gapi.auth.authorize({client_id: clientId, scope: scopes, immediate: false}, 
			  handleAuthResult);
	  return false;
	}

function OnLoadCallback(){

}
function myinit(){
}