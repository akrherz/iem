/* Copyright (C) 2008-2009 The Open Source Geospatial Foundation ¹
 * Published under the BSD license.
 * See http://geoext.org/svn/geoext/core/trunk/license.txt for the full text
 * of the license.
 * 
 * ¹ pending approval */

/**
 * @include GeoExt/data/LayerStore.js
 */

Ext.namespace("GeoExt");

/**
 * Class: GeoExt.MapPanel
 *     A map panel is a panel with a map inside it.
 *
 * Example: create a map panel and render it in a div identified
 * by "div-id".
 *
 * (start code)
 * var mapPanel = new GeoExt.MapPanel({
 *     border: false,
 *     renderTo: "div-id",
 *     map: new OpenLayers.Map({
 *         maxExtent: new OpenLayers.Bounds(-90, -45, 90, 45)
 *     })
 * });
 * (end)
 *
 * Example: create a panel including a map panel with a toolbar.
 *
 * (start code)
 * var panel = new Ext.Panel({
 *     items: [{
 *         xtype: "gx_mappanel",
 *         bbar: new Ext.Toolbar()
 *     }]
 * });
 * (end)
 *
 * Inherits from:
 *  - {Ext.Panel}
 */

/**
 * Constructor: GeoExt.MapPanel
 *     Creates a panel with a map inside it.
 *
 * Parameters:
 * config - {Object} A config object. In addition to the config options
 *     of its parent class, this object can receive specific options,
 *     see the API properties to know about these specific options.
 */
GeoExt.MapPanel = Ext.extend(Ext.Panel, {
    /**
     * APIProperty: map
     * {OpenLayers.Map|Object} An {OpenLayers.Map} instance
     * or an {OpenLayers.Map} config object, in the latter case
     * the map panel will take care of creating the {OpenLayers.Map}
     * object.
     */
    map: null,
    
    /**
     * APIProperty: layers
     * {GeoExt.data.LayerStore|GeoExt.data.GroupingStore|Array(OpenLayers.Layer)}
     *     A store holding records. If not provided, an empty
     *     {<GeoExt.data.LayerStore>} will be created. After instantiation
     *     this property will always be an {Ext.data.Store}, even if an array
     *     of {OpenLayers.Layer} was provided.
     */
    layers: null,

    /**
     * APIProperty: center
     * {OpenLayers.LonLat} The lonlat to which the map will
     * be initially centered, to be used in conjunction with
     * the zoom option.
     */
    center: null,

    /**
     * APIProperty: zoom
     * {Number} The initial zoom level of the map, to be used
     * in conjunction with the center option.
     */
    zoom: null,

    /**
     * APIProperty: extent
     * {OpenLayers.Bounds} The initial extent of the map, use
     * either this option of the center and zoom options.
     */
    extent: null,
    
    /**
     * Method: initComponent
     *     Initializes the map panel. Creates an OpenLayers map if
     *     none was provided in the config options passed to the
     *     constructor.
     */
    initComponent: function(){
        if(!(this.map instanceof OpenLayers.Map)) {
            this.map = new OpenLayers.Map(
                Ext.applyIf(this.map || {}, {allOverlays: true})
            );
        }
        var layers = this.layers;
        if(!layers || layers instanceof Array) {
            this.layers = new GeoExt.data.LayerStore({
                layers: layers,
                map: this.map
            });
        }
        
        if(typeof this.center == "string") {
            this.center = OpenLayers.LonLat.fromString(this.center);
        } else if(this.center instanceof Array) {
            this.center = new OpenLayers.LonLat(this.center[0], this.center[1]);
        }
        if(typeof this.extent == "string") {
            this.extent = OpenLayers.Bounds.fromString(this.extent);
        } else if(this.extent instanceof Array) {
            this.extent = OpenLayers.Bounds.fromArray(this.extent);
        }
        
        GeoExt.MapPanel.superclass.initComponent.call(this);       
    },
    
    /**
     * Method: updateMapSize
     * Tell the map that it needs to recaculate its size and position.
     */
    updateMapSize: function() {
        if(this.map) {
            this.map.updateSize();
        }
    },
    
    /**
     * Method: onRender
     *     Private method called after the panel has been
     *     rendered.
     */
    onRender: function() {
        GeoExt.MapPanel.superclass.onRender.apply(this, arguments);
        this.map.render(this.body.dom);
        if(this.map.layers.length > 0) {
            if(this.center) {
                // zoom does not have to be defined
                this.map.setCenter(this.center, this.zoom);
            }  else if(this.extent) {
                this.map.zoomToExtent(this.extent);
            } else {
                this.map.zoomToMaxExtent();
            }
        }
    },
    
    /**
     * Method: afterRender
     * Private method called after the panel has been rendered.
     */
    afterRender: function() {
        GeoExt.MapPanel.superclass.afterRender.apply(this, arguments);
        if(this.ownerCt) {
            this.ownerCt.on("move", this.updateMapSize, this);
        }
    },    

    /**
     * Method: onResize
     *     Private method called after the panel has been
     *     resized.
     */
    onResize: function() {
        GeoExt.MapPanel.superclass.onResize.apply(this, arguments);
        this.updateMapSize();
    },
    
    /**
     * Method: onDestroy
     * Private method called during the destroy sequence.
     */
    onDestroy: function() {
        if(this.ownerCt) {
            this.ownerCt.un("move", this.updateMapSize, this);
        }
        GeoExt.MapPanel.superclass.onDestroy.apply(this, arguments);
    }
    
});

/**
 * XType: gx_mappanel
 */
Ext.reg('gx_mappanel', GeoExt.MapPanel); 
