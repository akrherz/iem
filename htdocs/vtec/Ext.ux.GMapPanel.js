Ext.namespace('Ext.ux.panel');
 
/**
 * @author Shea Frederick - http://www.vinylfox.com
 * @class Ext.ux.panel.GMapPanel
 * @extends Ext.Panel
 * <p>A simple component that adds Google maps functionality to any panel or panel based component
 * (ie: windows).  For information about the Google Maps API see http://code.google.com/apis/maps/index.html.</p>
 * <p>Sample usage:</p>
 * <pre><code>
var panwin = new Ext.Window({
    layout: 'fit',
    closeAction: 'hide',
    title: 'GPanorama Window',
    width:400,
    height:300,
    x: 480,
    y: 60,
        items: {
        xtype: 'gmappanel',
        gmapType: 'panorama',
        setCenter: {
            lat: 42.345573,
            lng: -71.098326
        }
    }
});
 * </code></pre>
 * <p>Another example:</p>
 * <pre><code>
var mapwin = new Ext.Window({
    layout: 'fit',
    title: 'GMap Window',
    id: 'my_map',
    closeAction: 'hide',
    width: 400,
    height: 400,
    x: 40, y: 60,
    items: {
        xtype: 'gmappanel',
        zoomLevel: 14,
        gmapType: 'map',
        id: 'my_map',
        mapConfOpts: ['enableScrollWheelZoom','enableDoubleClickZoom','enableDragging'],
        mapControls: ['GSmallMapControl','GMapTypeControl','NonExistantControl'],
        setCenter: {
            geoCodeAddr: '4 Yawkey Way, Boston, MA, 02215-3409, USA',
            marker: {title: 'Fenway Park'}
        },
        {@link #markers}: [{
            geoCodeAddr: '465 Huntington Avenue, Boston, MA, 02215-5597, USA',
            marker: {title: 'Boston Museum of Fine Arts'},
            listeners: {
                click: function(e){
                    Ext.Msg.alert('Its fine', 'and it is art.');
                }
            }
        },{
            lat: 42.339419,
            lng: -71.09077,
            marker: {title: 'Northeastern University'}
        }]
    }
});
 * </code></pre>
 * <p>Additional functionality from the Google Maps API may be implemented using <b><code>{@link #getMap}</code></b>.
 * For example:<pre><code>
buttons: [{
    text: '+',
    minWidth: 30,
    handler: function(){
        var c = Ext.getCmp('my_map');
        var m = c.{@link #getMap}();
        m.setZoom(m.getZoom()+1);
        c.zoomLevel = m.getZoom();
    }
},{
    text: '-',
    minWidth: 30,
    handler: function(){
        var c = Ext.getCmp('my_map');
        var m = c.{@link #getMap}();
        m.setZoom(m.getZoom()-1);
        c.zoomLevel = m.getZoom();
    }
}]
 * </code></pre></p>
 * <p>This class is maintained at http://code.google.com/p/ext-ux-gmappanel/</p> 
 * <p>For Yahoo maps see: http://developer.yahoo.com/maps/ajax/</p>
 * @xtype gmappanel
 */
Ext.ux.GMapPanel = Ext.extend(Ext.Panel, {
    /**
     * @cfg {Boolean} border
     * Defaults to <tt>false</tt>.  See {@link Ext.Panel}.<code>{@link Ext.Panel#border border}</code>.
     */
    border: false,

    /**
     * @cfg {Array} respErrors
     * An array of msg/code pairs.
     */
    respErrors: [{
            code: 400, // G_GEO_BAD_REQUEST
            msg: 'A directions request could not be successfully parsed. For example, the request may have been rejected if it contained more than the maximum number of waypoints allowed.' 
        },{
            code: 601, // G_GEO_MISSING_QUERY
            msg: 'The HTTP q parameter was either missing or had no value. For geocoding requests, this means that an empty address was specified as input. For directions requests, this means that no query was specified in the input.'
        },{
            code: 604, // G_GEO_UNKNOWN_DIRECTIONS
            msg: 'The GDirections object could not compute directions between the points mentioned in the query. This is usually because there is no route available between the two points, or because we do not have data for routing in that region.'
        }],
    /**
     * @cfg {String} respErrorTitle
     * Defaults to <tt>'Error'</tt>.
     */
    respErrorTitle : 'Error',
    /**
     * @cfg {String} geoErrorMsgUnable
     * Defaults to <tt>'Unable to Locate the Address you provided'</tt>.
     */
    geoErrorMsgUnable : 'Unable to Locate the Address you provided',
    /**
     * @cfg {String} geoErrorTitle
     * Defaults to <tt>'Address Location Error'</tt>.
     */
    geoErrorTitle : 'Address Location Error',
    /**
     * @cfg {String} geoErrorMsgAccuracy
     * Defaults to <tt>'The address provided has a low accuracy.<br><br>Level {0} Accuracy (8 = Exact Match, 1 = Vague Match)'</tt>.
     */
    geoErrorMsgAccuracy : 'The address provided has a low accuracy.<br><br>Level {0} Accuracy (8 = Exact Match, 1 = Vague Match)',
    /**
     * @cfg {String} gmapType
     * The type of map to display, generic options available are: 'map', 'panorama'.
     * Defaults to <tt>'map'</tt>. 
     * More specific maps can be used by specifying the google map type:
     * <div class="mdetail-params"><ul>
     * <li><b><code>G_NORMAL_MAP</code></b> : <div class="sub-desc"><p>
     * Displays the default road map view
     * </p></div></li>
     * <li><b><code>G_SATELLITE_MAP</code></b> : <div class="sub-desc"><p>
     * Displays Google Earth satellite images
     * </p></div></li>
     * <li><b><code>G_HYBRID_MAP</code></b> : <div class="sub-desc"><p>
     * Displays a mixture of normal and satellite views
     * </p></div></li>
     * <li><b><code>G_DEFAULT_MAP_TYPES</code></b> : <div class="sub-desc"><p>
     * Contains an array of the above three types, useful for iterative processing.
     * </p></div></li>
     * <li><b><code>G_PHYSICAL_MAP</code></b> : <div class="sub-desc"><p>
     * Displays a physical map based on terrain information. 
     * </p></div></li>
     * <li><b><code>G_MOON_ELEVATION_MAP</code></b> : <div class="sub-desc"><p>
     * Displays a shaded terrain map of the surface of the Moon, color-coded by altitude.
     * </p></div></li>
     * <li><b><code>G_MOON_VISIBLE_MAP</code></b> : <div class="sub-desc"><p>
     * Displays photographic imagery taken from orbit around the moon.
     * </p></div></li>
     * <li><b><code>G_MARS_ELEVATION_MAP</code></b> : <div class="sub-desc"><p>
     * Displays a shaded terrain map of the surface of Mars, color-coded by altitude.
     * </p></div></li>
     * <li><b><code>G_MARS_VISIBLE_MAP</code></b> : <div class="sub-desc"><p>
     * Displays photographs taken from orbit around Mars.
     * </p></div></li>
     * <li><b><code>G_MARS_INFRARED_MAP</code></b> : <div class="sub-desc"><p>
     * Displays a shaded infrared map of the surface of Mars, where warmer areas appear brighter and colder areas appear darker.
     * </p></div></li>
     * <li><b><code>G_SKY_VISIBLE_MAP</code></b> : <div class="sub-desc"><p>
     * Displays a mosaic of the sky, as seen from Earth, covering the full celestial sphere.
     * </p></div></li>
     * </ul></div>
     * Sample usage:
     * <pre><code>
     * gmapType: G_MOON_VISIBLE_MAP
     * </code></pre>
     */
    gmapType : 'map',
    /**
     * @cfg {Object} setCenter
     * The initial center location of the map. The map needs to be centered before it can be used.
     * A marker is not required to be specified. 
     * More markers can be added to the map using the <code>{@link #markers}</code> array.
     * For example:
     * <pre><code>
setCenter: {
    geoCodeAddr: '4 Yawkey Way, Boston, MA, 02215-3409, USA',
    marker: {title: 'Fenway Park'}
},

// or just specify lat/long
setCenter: {
    lat: 42.345573,
    lng: -71.098326
}
     * </code></pre>
     */
    /**
     * @cfg {Number} zoomLevel
     * The zoom level to initialize the map at, generally between 1 (whole planet) and 40 (street).
     * Also used as the zoom level for panoramas, zero specifies no zoom at all.
     * Defaults to <tt>3</tt>.
     */
    zoomLevel: 3,
    /**
     * @cfg {Number} yaw
     * The Yaw, or rotational direction of the users perspective in degrees. Only applies to panoramas.
     * Defaults to <tt>180</tt>.
     */
    yaw: 180,
    /**
     * @cfg {Number} pitch
     * The pitch, or vertical direction of the users perspective in degrees.
     * Defaults to <tt>0</tt> (straight ahead). Valid values are between +90 (straight up) and -90 (straight down). 
     */
    pitch: 0,
    /**
     * @cfg {Boolean} displayGeoErrors
     * True to display geocoding errors to the end user via a message box.
     * Defaults to <tt>false</tt>.
     */
    displayGeoErrors: false,
    /**
     * @cfg {Boolean} minGeoAccuracy
     * The level (between 1 & 8) to display an accuracy error below. Defaults to <tt>7</tt>. For additional information
     * see <a href="http://code.google.com/apis/maps/documentation/reference.html#GGeoAddressAccuracy">here</a>.
     */
    minGeoAccuracy: 7,
    /**
     * @cfg {Array} mapConfOpts
     * Array of strings representing configuration methods to call, a full list can be found
     * <a href="http://code.google.com/apis/maps/documentation/reference.html#GMap2">here</a>.
     * For example:
     * <pre><code>
     * mapConfOpts: ['enableScrollWheelZoom','enableDoubleClickZoom','enableDragging'],
     * </code></pre>
     */
    /**
     * @cfg {Array} mapControls
     * Array of strings representing map controls to initialize, a full list can be found
     * <a href="http://code.google.com/apis/maps/documentation/reference.html#GControlImpl">here</a>.
     * For example:
     * <pre><code>
     * mapControls: ['GSmallMapControl','GMapTypeControl','NonExistantControl']
     * </code></pre>
     */
    /**
     * @cfg {Array} markers
     * Markers may be added to the map. Instead of specifying <code>lat</code>/<code>lng</code>,
     * geocoding can be specified via a <code>geoCodeAddr</code> string.
     * For example:
     * <pre><code>
markers: [{
    //lat: 42.339641,
    //lng: -71.094224,
    // instead of lat/lng:
    geoCodeAddr: '465 Huntington Avenue, Boston, MA, 02215-5597, USA',
    marker: {title: 'Boston Museum of Fine Arts'},
    listeners: {
        click: function(e){
            Ext.Msg.alert('Its fine', 'and its art.');
        }
    }
},{
    lat: 42.339419,
    lng: -71.09077,
    marker: {title: 'Northeastern University'}
}]
     * </code></pre>
     */
    // private
    mapDefined: false,
    // private
    mapDefinedGMap: false,
    // private
    initComponent : function(){
        
        this.addEvents(
            /**
             * @event mapready
             * Fires when the map is ready for interaction
             * @param {GMapPanel} this
             * @param {GMap} map
             */
            'mapready'
        );
        Ext.ux.GMapPanel.superclass.initComponent.call(this);        

    },
    // private
    afterRender : function(){
        
        var wh = this.ownerCt.getSize();
        Ext.applyIf(this, wh);
        
        Ext.ux.GMapPanel.superclass.afterRender.call(this);    
        
        if (this.gmapType === 'map'){
            this.gmap = new GMap2(this.body.dom);
			this.mapDefined = true;
			this.mapDefinedGMap = true;
        }
        
        if (this.gmapType === 'panorama'){
            this.gmap = new GStreetviewPanorama(this.body.dom);
			this.mapDefined = true;
        }

		if (!this.mapDefined && this.gmapType){
			this.gmap = new GMap2(this.body.dom);
			this.gmap.setMapType(this.gmapType);
			this.mapDefined = true;
			this.mapDefinedGMap = true;
		}
        
        GEvent.bind(this.getMap(), 'load', this, this.onMapReady);
        
        if (typeof this.setCenter === 'object') {
            if (typeof this.setCenter.geoCodeAddr === 'string'){
                this.geoCodeLookup(this.setCenter.geoCodeAddr, this.setCenter.marker, false, true, this.setCenter.listeners);
            }else{
                if (this.gmapType === 'map'){
                    var point = this.fixLatLng(new GLatLng(this.setCenter.lat,this.setCenter.lng));
                    this.getMap().setCenter(point, this.zoomLevel);    
                }
                if (typeof this.setCenter.marker === 'object' && typeof point === 'object') {
                    this.addMarker(point, this.setCenter.marker, this.setCenter.marker.clear);
                }
            }
            if (this.gmapType === 'panorama'){
                this.getMap().setLocationAndPOV(new GLatLng(this.setCenter.lat,this.setCenter.lng), {yaw: this.yaw, pitch: this.pitch, zoom: this.zoomLevel});
            }
        }

    },
    // private
    onMapReady : function(){
        
        this.addMapControls();
        this.addOptions();
        
        this.addMarkers(this.markers);
        this.addKMLOverlay(this.autoLoadKML);
        
        this.fireEvent('mapready', this, this.getMap());
        
    },
    // private
    onResize : function(w, h){
        
        Ext.ux.GMapPanel.superclass.onResize.call(this, w, h);

        // check for the existance of the google map in case the onResize fires too early
        if (typeof this.getMap() == 'object') {
            this.getMap().checkResize();
        }

    },
    // private
    setSize : function(width, height, animate){
        
        Ext.ux.GMapPanel.superclass.setSize.call(this, width, height, animate);
        
        // check for the existance of the google map in case setSize is called too early
        if (typeof this.getMap() == 'object') {
            this.getMap().checkResize();
        }
        
    },
    /**
     * Returns the current google map which can be used to call Google Maps API specific handlers.
     * @return {GMap} this
     */
    getMap : function(){
        
        return this.gmap;
        
    },
    /**
     * Returns the maps center as a GLatLng object
     * @return {GLatLng} this
     */
    getCenter : function(){
        
        return this.fixLatLng(this.getMap().getCenter());
        
    },
    /**
     * Returns the maps center as a simple object
     * @return {Object} this has lat and lng properties only
     */
    getCenterLatLng : function(){
        
        var ll = this.getCenter();
        return {lat: ll.lat(), lng: ll.lng()};
        
    },
    /**
     * Creates markers from the array that is passed in. Each marker must consist of at least
     * <code>lat</code> and <code>lng</code> properties or a <code>geoCodeAddr</code>.
     * @param {Array} markers an array of marker objects
     */
    addMarkers : function(markers) {
        
        if (Ext.isArray(markers)){
            for (var i = 0; i < markers.length; i++) {
                if (typeof markers[i].geoCodeAddr == 'string') {
                    this.geoCodeLookup(markers[i].geoCodeAddr, markers[i].marker, false, markers[i].setCenter, markers[i].listeners);
                }else{
                    var mkr_point = this.fixLatLng(new GLatLng(markers[i].lat, markers[i].lng));
                    this.addMarker(mkr_point, markers[i].marker, false, markers[i].setCenter, markers[i].listeners);
                }
            }
        }
        
    },
    /**
     * Creates a single marker.
     * @param {Object} point a GLatLng point
     * @param {Object} marker a marker object consisting of at least lat and lng
     * @param {Boolean} clear clear other markers before creating this marker
     * @param {Boolean} center true to center the map on this marker
     * @param {Object} listeners a listeners config
     */
    addMarker : function(point, marker, clear, center, listeners){
        
        Ext.applyIf(marker,G_DEFAULT_ICON);

        if (clear === true){
            this.getMap().clearOverlays();
        }
        if (center === true) {
            this.getMap().setCenter(point, this.zoomLevel);
        }

        var mark = new GMarker(point,marker);
        if (typeof listeners === 'object'){
            for (evt in listeners) {
                GEvent.bind(mark, evt, this, listeners[evt]);
            }
        }
        this.getMap().addOverlay(mark);

    },
    // private
    addMapControls : function(){
        
        if (this.gmapType === 'map') {
            if (Ext.isArray(this.mapControls)) {
                for(i=0;i<this.mapControls.length;i++){
                    this.addMapControl(this.mapControls[i]);
                }
            }else if(typeof this.mapControls === 'string'){
                this.addMapControl(this.mapControls);
            }else if(typeof this.mapControls === 'object'){
                this.getMap().addControl(this.mapControls);
            }
        }
        
    },
    /**
     * Adds a GMap control to the map.
     * @param {String/Object} mc a string representation of the control to be instantiated or an already instantiated control.
     */
    addMapControl : function(mc){
        
        if (Ext.isObject(mc)) {
            this.getMap().addControl(mc);
        } else {
            var mcf = window[mc];
            if (typeof mcf === 'function') {
                this.getMap().addControl(new mcf());
            }
        }
        
    },
    // private
    addOptions : function(){
        
        if (Ext.isArray(this.mapConfOpts)) {
            var mc;
            for(i=0;i<this.mapConfOpts.length;i++){
                this.addOption(this.mapConfOpts[i]);
            }
        }else if(typeof this.mapConfOpts === 'string'){
            this.addOption(this.mapConfOpts);
        }        
        
    },
    /**
     * Adds a GMap option to the map.
     * @param {String} mo a string representation of the option to be instantiated.
     */
    addOption : function(mo){
        
        var mof = this.getMap()[mo];
        if (typeof mof === 'function') {
            this.getMap()[mo]();
        }    
        
    },
    /**
     * Loads a KML file into the map.
     * @param {String} kmlfile a string URL to the KML file.
     */
    addKMLOverlay : function(kmlfile){
        
        if (typeof kmlfile === 'string' && kmlfile !== '') {
            var geoXml = new GGeoXml(kmlfile);
            this.getMap().addOverlay(geoXml);
        }
        
    },
    /**
     * Looks up and address and optionally add a marker, center the map to this location, or
     * clear other markers. Sample usage:
     * <pre><code>
buttons: [
    {
        text: 'Fenway Park',
        handler: function(){
            var addr = '4 Yawkey Way, Boston, MA, 02215-3409, USA';
            Ext.getCmp('my_map').geoCodeLookup(addr, undefined, false, true, undefined);
        }
    },{
        text: 'Zoom Fenway Park',
        handler: function(){
            Ext.getCmp('my_map').zoomLevel = 19;
            var addr = '4 Yawkey Way, Boston, MA, 02215-3409, USA';
            Ext.getCmp('my_map').geoCodeLookup(addr, undefined, false, true, undefined);
        }
    },{
        text: 'Low Accuracy',
        handler: function(){
            Ext.getCmp('my_map').geoCodeLookup('Paris, France', undefined, false, true, undefined);
        }
    },{

        text: 'Bogus Address',
        handler: function(){
            var addr = 'Some Fake, Address, For, Errors';
            Ext.getCmp('my_map').geoCodeLookup(addr, undefined, false, true, undefined);
        }
    }
]
     * </code></pre>
     * @param {String} addr the address to lookup.
     * @param {Object} marker the marker to add (optional).
     * @param {Boolean} clear clear other markers before creating this marker
     * @param {Boolean} center true to set this point as the center of the map.
     * @param {Object} listeners a listeners config
     */
    geoCodeLookup : function(addr, marker, clear, center, listeners) {
        
        if (!this.geocoder) {
            this.geocoder = new GClientGeocoder();
        }
        this.geocoder.getLocations(addr, this.addAddressToMap.createDelegate(this, [addr, marker, clear, center, listeners], true));
        
    },
    // private
    addAddressToMap : function(response, addr, marker, clear, center, listeners){
        if (!response || response.Status.code != 200) {
            this.respErrorMsg(response.Status.code);
        }else{
            place = response.Placemark[0];
            addressinfo = place.AddressDetails;
            accuracy = addressinfo.Accuracy;
            if (accuracy === 0) {
                this.geoErrorMsg(this.geoErrorTitle, this.geoErrorMsgUnable);
            }else{
                if (accuracy < this.minGeoAccuracy) {
                    this.geoErrorMsg(this.geoErrorTitle, String.format(this.geoErrorMsgAccuracy, accuracy));
                }else{
                    point = this.fixLatLng(new GLatLng(place.Point.coordinates[1], place.Point.coordinates[0]));
                    if (center){
                        this.getMap().setCenter(point, this.zoomLevel);
                    }
                    if (typeof marker === 'object') {
                        if (!marker.title){
                            marker.title = place.address;
                        }
                        Ext.applyIf(marker, G_DEFAULT_ICON);
                        this.addMarker(point, marker, clear, false, listeners);
                    }
                }
            }
        }
        
    },
    // private
    geoErrorMsg : function(title,msg){
        if (this.displayGeoErrors) {
            Ext.MessageBox.alert(title,msg);
        }
    },
    // private
    respErrorMsg : function(code){
        Ext.each(this.respErrors, function(obj){
            if (code == obj.code){
                Ext.MessageBox.alert(this.respErrorTitle, obj.msg);
            }
        }, this);
    },
 	// private
	// used to inverse the lat/lng coordinates to correct locations on the sky map
	fixLatLng : function(llo){
        if (this.getMap().getCurrentMapType()) {
            if (this.getMap().getCurrentMapType().QO == 'visible') {
                llo.lat(180 - llo.lat());
                llo.lng(180 - llo.lng());
            }
        }
		return llo;
	}
});

Ext.reg('gmappanel',Ext.ux.GMapPanel); 