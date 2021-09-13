var htmlInterface = ['<div class="panel panel-default">',
  '<div class="panel-heading">',
    '<a class="btn btn-default pull-right" href="/" id="iemss-metadata-link" target="_new">',
    '<i class="fa fa-info"></i> Station Metadata</a>',
    '<h3 class="panel-title">Select Widget for <span id="iemss-network"></span> Network</h3> ',
    '<br class="clearfix" />',
  '</div>',
  '<div class="panel-body">',
'<div class="row">',
	'<div class="col-sm-6">',

'<div class="btn-group">',
'<button class="btn btn-default btn-sm dropdown-toggle" type="button" data-toggle="dropdown" aria-expanded="false">',
  'Sort Available Stations: <span class="caret"></span>',
'</button>',
'<ul class="dropdown-menu" role="menu">',
	'<li id="iemss-sortbyid"><a href="#">Sort by Identifier</a></li>',
	'<li id="iemss-sortbyname"><a href="#">Sort by Name</a></li>',
'</ul>',
'</div>',

'<select multiple id="stations_in" class="form-control">',
'</select>',
'<div class="form-inline">',
'<div class="form-group">',
    '<input type="text" class="form-control" id="stationfilter" ',
		'placeholder="Enter some text here to filter listing below">',
'</div>',
'<div class="form-group">',
		'<button type="submit" id="stations_add" class="btn btn-default"><i class="fa fa-plus"></i> Add Selected</button>',
		'<button type="submit" id="stations_addall" class="btn btn-default">Add All</button>',
'</div>',
'</div>',
		'</div>',
	'<div class="col-sm-6">',
'<label for="stations_out">Selected Stations:</label>',
'<select multiple id="stations_out" class="form-control" name="stations">',
'</select>',
'<div class="form-group">',
		'<button type="submit" id="stations_del" class="btn btn-default"><i class="fa fa-minus"></i> Remove Selected</button>',
		'<button type="submit" id="stations_delall" class="btn btn-default">Remove All</button>',
'</div>',
	'</div>',
'</div>',
'<br />',
'<div class="row"><div class="col-sm-12">',
		'<div id="map" style="width:100%; height:400px"></div>',
'</div></div>',
  '</div><!-- End of panel-body -->',
'</div><!-- End of panel -->'];

var map, selectedFeature, selectControl, geojson, geojsonSource, network;

//http://www.lessanvaezi.com/filter-select-list-options/
jQuery.fn.filterByText = function(textbox, selectSingleMatch) {
	return this.each(function() {
		var select = this;
		var options = [];
		$(select).find('option').each(function() {
			options.push({value: $(this).val(), text: $(this).text()});
		});
		$(select).data('options', options);
		$(textbox).bind('change keyup', function() {
			var options = $(select).empty().scrollTop(0).data('options');
			var search = $.trim($(this).val());
			var regex = new RegExp(search,'gi');

			$.each(options, function(i) {
				var option = options[i];
				if(option.text.match(regex) !== null) {
					$(select).append(
							$('<option>').text(option.text).val(option.value)
					);
				}
			});
			if (selectSingleMatch === true && 
					$(select).children().length === 1) {
				$(select).children().get(0).selected = true;
			}
		});
	});
};

function sortListing(option){
	$("#stations_in").append($("#stations_in option").remove().sort(function(a, b) {
		var at = $(a).text(), bt = $(b).text();
		if (option == 'name'){
			at = at.slice(at.indexOf(' ')+1);
			bt = bt.slice(bt.indexOf(' ')+1);
		}
		return (at > bt)?1:((at < bt)?-1:0);
	}));
}

$().ready(function() {  
	
	// Make sure clicking the submit button selects all of the selected 
	// stations, this avoids user confusion
	$("form[name='iemss'] :submit").click(function (){
        // Empty input implies that all are selected!
        if ($("#iemss").data("supports-all") != "0" && $('#stations_in option').length == 0){
            // Deselect anything selected so that it does not submit
            $('#stations_out option').prop('selected', false);
            // Add a faked _ALL station
            $("#stations_out").append(
                '<option value="_ALL" selected="selected">ALL</option>'
            );
            return true;
        }
        $('#stations_out option').prop('selected', true);
		// Stop us if we have no stations selected!
		if ($('#stations_out option').length == 0){
			alert("No stations listed in 'Selected Stations'!");
			return false;
		}
		return true;
	});
	
	$("#iemss").append(htmlInterface.join(''));

	network = $("#iemss").data("network");
    var only_online = ($("#iemss").data("only-online") == "1");
	var select_name = $("#iemss").attr("data-name");
	if (select_name){
		$("#stations_out").attr("name", select_name);
	}
	$("#iemss-network").html(network);
	$("#iemss-metadata-link").attr('href', '/sites/networks.php?network='+network);
	
    $("#stations_in").dblclick(function() {
		return !$('#stations_in option:selected').remove().appendTo('#stations_out');
    });
    $("#stations_out").dblclick(function() {
		return !$('#stations_out option:selected').remove().appendTo('#stations_in');
    });

	$('#stations_add').click(function() {  
		return !$('#stations_in option:selected').remove().appendTo('#stations_out');  
	});  
	$('#stations_addall').click(function() {  
		var ret = !$('#stations_in option').remove().appendTo('#stations_out');
		$('#stations_out option').prop('selected', true);
		return ret;
	});  
	$('#stations_delall').click(function() {  
		return !$('#stations_out option').remove().appendTo('#stations_in');  
	});  
	$('#stations_del').click(function() {  
		$('#stations_out option:selected').remove().appendTo('#stations_in');
		$('#stations_out option').each(function(i) {  
			$(this).attr("selected", "selected");  
		});		
		return false;
	});  
	
	$('#iemss-sortbyid').click(function(){
		sortListing("id");
	});
	$('#iemss-sortbyname').click(function(){
		sortListing("name");
	});
	
	
	geojsonSource = new ol.source.Vector({
		format: new ol.format.GeoJSON(),
		projection : ol.proj.get('EPSG:3857'),
		url : '/geojson/network/' + network + '.geojson?only_online=' +
            (only_online ? "1": "0")
	});
	geojson = new ol.layer.Vector({
		source : geojsonSource,
		style : function(feature, resolution){
			var style = [new ol.style.Style({
				image: new ol.style.Circle({
					fill: new ol.style.Fill({
						color: 'rgba(255,0,0,1)'
					}),
					stroke: new ol.style.Stroke({
						color: '#3399CC',
						width: 1.25
					}),
					radius: 5
				})

			})];
			return style;
		}
	});

	map = new ol.Map({
		target: 'map',
		layers: [new ol.layer.Tile({
		      source: new ol.source.OSM()
	    }),
		geojson
		],
		view: new ol.View({
			projection: ol.proj.get('EPSG:3857'),
			center: [-10575351, 5160979],
			zoom: 3
		})
	});

	geojsonSource.on('change', function(e) {
		if (geojsonSource.getState() == 'ready') {
			$.each(geojsonSource.getFeatures(), function (index, feat) {
				$('#stations_in').append($('<option/>', { 
					value: feat.get('sid'),
					text : "["+ feat.get('sid') +"] "+ feat.get('sname') +" "+ feat.get("time_domain")
				}));
			});
			sortListing("id");
			$('#stations_in').filterByText($('#stationfilter'), true);
			map.getView().fit(geojsonSource.getExtent(), map.getSize());
		}
	});

	var $newdiv = $("<div>", {id: "popup", style: "width: 250px;"});
	$("#map").append($newdiv);
	var $newdiv2 = $("<div>", {id: "popover-content"});
	$("#map").append($newdiv2);

	var element = document.getElementById('popup');

	var popup = new ol.Overlay({
		element: element,
		positioning: 'bottom-center',
		stopEvent: false
	});
	map.addOverlay(popup);

	$(element).popover({
		'placement': 'top',
		'html': true,
		content: function() { return $('#popover-content').html(); }
	});
	// display popup on click
	map.on('click', function(evt) {
		var feature = map.forEachFeatureAtPixel(evt.pixel,
				function(feature, layer) {
			return feature;
		});
		if (feature) {
			var geometry = feature.getGeometry();
			var coord = geometry.getCoordinates();
			var sid = feature.get('sid');
			popup.setPosition(coord);
			var content = "<p><strong>SID: </strong>"+ sid
			+"<br /><strong>Name: </strong>"+ feature.get('sname')
            +"<br /><strong>Period:</strong> "+ feature.get("time_domain") +"</p>";
			$('#popover-content').html(content);
			$(element).popover('show');
			$("#stations_in").find("option[value=\""+sid+"\"]").attr("selected", "selected");
		} else {
			$(element).popover('hide');
		}

	});

});  