if (typeof console == "undefined") var console = { log: function() {} }; 
else if (typeof console.log == "undefined") console.log = function() {};

// http://forum.jquery.com/topic/cross-domain-ajax-and-ie
$.ajaxTransport("+*", function( options, originalOptions, jqXHR ) {
    
    if(jQuery.browser.msie && window.XDomainRequest) {
        
        var xdr;
        
        return {
            
            send: function( headers, completeCallback ) {

                // Use Microsoft XDR
                xdr = new XDomainRequest();
                
                xdr.open("get", options.url);
                
                xdr.onload = function() {
                    
                    if(this.contentType.match(/\/xml/)){
                        
                        var dom = new ActiveXObject("Microsoft.XMLDOM");
                        dom.async = false;
                        dom.loadXML(this.responseText);
                        completeCallback(200, "success", [dom]);
                        
                    }else{
                        
                        completeCallback(200, "success", [this.responseText]);
                        
                    }

                };
                
                xdr.ontimeout = function(){
                    completeCallback(408, "error", ["The request timed out."]);
                };
                
                xdr.onerror = function(){
                    completeCallback(404, "error", ["The requested resource could not be found."]);
                };
                
                xdr.send();
          },
          abort: function() {
              if(xdr)xdr.abort();
          }
        };
      }
    });

function xmlescape(text){
        text = text.replace(/\&/g, "&amp;");
        text = text.replace(/</g,  "&lt;");
        text = text.replace(/>/g,  "&gt;");
        text = text.replace(/'/g,  "&apos;");
        text = text.replace(/"/g,  "&quot;");
        return text;
}

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

function clearForm(){
	$("#theform")[0].reset();
	$('#farmerselector').val('invalid');
	currentEntry = [null, null, null, null, null, null, null];
}

function getValuesFromForm(){
	var values = {};
	/* Get radio's that are checked */
	$("#theform input[type=radio]:checked").each(function(){
		//console.log("Found radio "+ this.name);
        values[ this.name.replace(/_/g,"").toLowerCase() ] = $(this).val();
    });
	
	// Update a previously existing row in the database
	$('#theform input[type=text]').each(function() {
        values[this.name.replace(/_/g,"").toLowerCase()] = $(this).val();
    });
    
    // textareas
	$('#theform textarea').each(function() {
        values[this.name.replace(/_/g,"").toLowerCase()] = $(this).val();
    });
    return values;
}

function updateRow(){
	if (currentEntry[0] == null){
		//console.log("updateRow aborted due to null");
		return;
	}
	var values = getValuesFromForm();
    
   	$(currentEntry).each(function(i,ce){
   		var index = i;
   		$(ce).children().each(function(j,c){
    		if (c.nodeName.substr(0,3) == 'gsx'){
    			$(c).text( values[c.nodeName.substr(4,1000)] );
    		}
			if (c.nodeName == 'gsx:updated'){
				console.log("Setting updated for i"+ i);
				$(c).text( new Date() );
			}		
		});

		uri = $($(ce).find('link[rel=edit]')).attr('href');
		//console.log("looping over i "+ i +" uri is "+ uri);
  		if (uri === undefined || uri == null) return;
		$.ajax({ // ?sq=farmercode=1
  			url: 'ajax-proxy.php?csurl='+ uri,
  			headers: {
    			'Authorization': 'Bearer ' + access_token
  			},
  			data : xmlToString(ce),
  			processData : false,
  			contentType: 'application/atom+xml',
  			type : 'PUT',
	  		error: function(data, status){
	  			msg = "";
	  			for (prop in data){
	  				msg += "property: " + prop + " value: [" + data[prop] + "]\n";

	  			}
	  			console.log(msg);
	  			alert("Encountered error: "+ msg);
	  		},
  			success: function(data, status) {
				currentEntry[i] = data.childNodes[0];
				console.log("Entry "+ i+" was saved!");
				if (i == 6) alert("Entry updated!");
  			}
  		});		
   	});
	
}

function addRow(){
	
	var values = getValuesFromForm();
	
	x = [['<entry xmlns="http://www.w3.org/2005/Atom"',
    'xmlns:gsx="http://schemas.google.com/spreadsheets/2006/extended">'],
    ['<entry xmlns="http://www.w3.org/2005/Atom"',
    'xmlns:gsx="http://schemas.google.com/spreadsheets/2006/extended">'],
    ['<entry xmlns="http://www.w3.org/2005/Atom"',
    'xmlns:gsx="http://schemas.google.com/spreadsheets/2006/extended">'],
    ['<entry xmlns="http://www.w3.org/2005/Atom"',
    'xmlns:gsx="http://schemas.google.com/spreadsheets/2006/extended">'],
    ['<entry xmlns="http://www.w3.org/2005/Atom"',
    'xmlns:gsx="http://schemas.google.com/spreadsheets/2006/extended">'],
    ['<entry xmlns="http://www.w3.org/2005/Atom"',
    'xmlns:gsx="http://schemas.google.com/spreadsheets/2006/extended">'],
    ['<entry xmlns="http://www.w3.org/2005/Atom"',
    'xmlns:gsx="http://schemas.google.com/spreadsheets/2006/extended">']];

    for (var prop in values){
    	var n;
    	if (prop.search('field1') == 0 || prop.search('f1') == 0){
    		n = 1;
    	} else if (prop.search('field2') == 0 || prop.search('f2') == 0){
    		n = 2;    		
    	} else {
    		n = 0;
    	}
    	if (prop.search('r2') == 2){
    		n += 2;
    	}
    	else if (prop.search('r3') == 2){
    		n += 4;
    	}
    
    	//console.log("prop "+ prop +" n "+ n);
    	v = values[prop];
    	if (v == '' || v == null ) {
    		x[n].push("<gsx:"+ prop +"/>");
    	} else {
	    	x[n].push("<gsx:"+ prop +">"+ xmlescape(v) +"</gsx:"+ prop +">");		
    	}
    	if (prop == 'field1name' || prop == 'field1id'){
    		x[3].push("<gsx:"+ prop +">"+ xmlescape(v) +"</gsx:"+ prop +">");		
    		x[5].push("<gsx:"+ prop +">"+ xmlescape(v) +"</gsx:"+ prop +">");		
    	}
    	if (prop == 'field2name' || prop == 'field2id'){
    		x[4].push("<gsx:"+ prop +">"+ xmlescape(v) +"</gsx:"+ prop +">");		
    		x[6].push("<gsx:"+ prop +">"+ xmlescape(v) +"</gsx:"+ prop +">");		
    	}
    }
    $(x).each(function(i,xi){
    	if (i > 0){
	    	x[i].push('<gsx:farmercode>'+ xmlescape(values['farmercode']) +'</gsx:farmercode>');
    	}    	
    	x[i].push('<gsx:updated>'+ (new Date()) +'</gsx:updated>');
	    x[i].push('</entry>');
    });
    
    $(spreadkeys).each(function(i,spreadkey){
	    $.ajax({ // ?sq=farmercode=1
	  		url: 'ajax-proxy.php?csurl='+ spreadkey,
		  	headers: {
	    		'Authorization': 'Bearer ' + access_token
	  		},
	  		data : x[i].join(" "),
	  		processData : false,
	  		contentType: 'application/atom+xml',
	  		type : 'POST',
	  		success: function(data, status) {
	  			if (i == 0) alert("Saved Entry, thank you!");
	  		},
	  		error: function(data, status){
	  			msg = "";
	  			for (prop in data){
	  				msg += "property: " + prop + " value: [" + data[prop] + "]\n";

	  			}
	  			console.log(msg);
	  			alert("Encountered error: "+ msg);
	  		}
	  	});
    });

	
} // End of addRow

// Download the google spreadsheets and generate farmer selector codes
function getSpreadsheets(){
	$(spreadkeys).each(function(i,spreadkey){
		$.ajax({ // ?sq=farmercode=1
			cache: false,
		  url: spreadkey,
		  headers: {
		    'Authorization': 'Bearer ' + access_token
		  },		  
	  	  error: function(data, status){
	  			msg = "";
	  			for (prop in data){
	  				msg += "property: " + prop + " value: [" + data[prop] + "]\n";

	  			}
	  			console.log(msg);
	  			alert("Encountered error: "+ msg);
	  	  }, 
		  success: function(data, status) {
			// Save this object back to globals for later use
		  	spreadsheetDocs[i] = $(data);
		  	if (i == 0){
		    	farmercodes = [];
		    	spreadsheetDocs[i].find('entry').each(function(i,x){
		    		$(x).children().each(function(j,c){
		    			if (c.nodeName == 'gsx:farmercode'){
		    				farmercodes.push( $(c).text() );
		    			}
		    		});
		   		});
		    	setSelector(farmercodes);
		  	}
		    }
		  });
	});
}

function setFormValue(key, val){
	//console.log('Setting form key '+ key +' value '+ val);
	l = $('#theform [name='+key+']');
	if (l.length == 0){
		console.log("Failed to find form key "+ key);
		return;
	}
	if (l.length == 1){
		$(l).val( val);
		return;
	}
	/* Trickier radio buttons! default to no*/
	//console.log("RADIO "+ key );
	$(l[1]).attr("checked", true);
	l = $('#theform [name='+key+'][value='+val+']');
	if (l.length == 1){
		$(l[0]).attr("checked", true);
	}
}

function loadEntryInfoForm(i){
	// Take the currentEntry and load it into the form!
	$(currentEntry[i]).children().each(function(j,c){
    		if (c.nodeName.substr(0,3) == 'gsx'){
    			setFormValue(c.nodeName.substr(4,1000), $(c).text());
    		}
	});
		
}

function setFarmer(farmercode){
	if (farmercode == 'invalid') return;
	currentEntry = [null, null, null, null, null, null, null];
	$(spreadsheetDocs).each(function(i, spreadsheetDoc){
		var index = i;
		spreadsheetDoc.find('entry').each(function(i,x){
    		thisEntry = x;
    		$(x).children().each(function(j,c){
    			if (c.nodeName == 'gsx:farmercode'){
    				if ($(c).text() == farmercode){
    					currentEntry[index] = thisEntry;
    					loadEntryInfoForm(index);
    				}
    			}
    		});
    	});
	});
    editting = true;
}

function addNewEntry(){
	editting = false;
	addRow();
}

function setSelector(farmercodes){
	 var el = document.getElementById('farmerselector');
	 // Empty it out first
	 while (el.hasChildNodes()){
	 	el.removeChild(el.childNodes[0]);
	 }

	 var opt = document.createElement("option");
     opt.text = '-- SELECT FROM LIST --';
     opt.value = 'invalid';
     el.options.add(opt);
	 
     for (i=0;i<farmercodes.length;i++){
         var opt = document.createElement("option");
         opt.text = farmercodes[i];
         opt.value = farmercodes[i];
         el.options.add(opt);
     }
}

function handleClientLoad() {
	//console.log("handleClientLoad() called");
	  gapi.client.setApiKey(apiKey);
	  window.setTimeout(checkAuth,1);
	}

	function checkAuth() {
	  gapi.auth.authorize({client_id: clientId, scope: scopes, immediate: true}, handleAuthResult);
	}

	function handleAuthResult(authResult) {
	  var notAuthorizedDiv = document.getElementById('needtoauthenticate');
	  var authorizedDiv = document.getElementById('authenticated');
	  if (authResult && !authResult.error) {
	  	access_token = authResult.access_token;
	  	getSpreadsheets();
		// Subtract five minutes from expires_in to ensure timely refresh
		var authTimeout = (authResult.expires_in - 5 * 60) * 1000;
		setTimeout(checkAuth, authTimeout);
	    notAuthorizedDiv.style.display = 'none';
	    authorizedDiv.style.display = 'block';	   

	  } else {

	  }
	}

	function handleAuthClick(event) {
	  gapi.auth.authorize({client_id: clientId, scope: scopes, immediate: false}, 
			  handleAuthResult);
	  return false;
	}
