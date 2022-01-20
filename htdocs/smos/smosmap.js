var controls;
var vectors;
var feature;
/**
     * Define a namespace for the application.
     */
window.app = {};
var app = window.app;

/**
 * @constructor
 * @extends {ol.interaction.Pointer}
 */
app.Drag = function () {

    ol.interaction.Pointer.call(this, {
        handleDownEvent: app.Drag.prototype.handleDownEvent,
        handleDragEvent: app.Drag.prototype.handleDragEvent,
        handleMoveEvent: app.Drag.prototype.handleMoveEvent,
        handleUpEvent: app.Drag.prototype.handleUpEvent
    });

    /**
     * @type {ol.Pixel}
     * @private
     */
    this.coordinate_ = null;

    /**
     * @type {string|undefined}
     * @private
     */
    this.cursor_ = 'pointer';

    /**
     * @type {ol.Feature}
     * @private
     */
    this.feature_ = null;

    /**
     * @type {string|undefined}
     * @private
     */
    this.previousCursor_ = undefined;

};
// https://gis.stackexchange.com/questions/324606
var ol_ext_inherits = function (child, parent) {
    child.prototype = Object.create(parent.prototype);
    child.prototype.constructor = child;
};
ol_ext_inherits(app.Drag, ol.interaction.Pointer);


/**
 * @param {ol.MapBrowserEvent} evt Map browser event.
 * @return {boolean} `true` to start the drag sequence.
 */
app.Drag.prototype.handleDownEvent = function (evt) {
    var map = evt.map;

    var feature = map.forEachFeatureAtPixel(evt.pixel,
        function (feature, layer) {
            return feature;
        });

    if (feature) {
        this.coordinate_ = evt.coordinate;
        this.feature_ = feature;
    }

    return !!feature;
};


/**
 * @param {ol.MapBrowserEvent} evt Map browser event.
 */
app.Drag.prototype.handleDragEvent = function (evt) {
    var map = evt.map;

    map.forEachFeatureAtPixel(evt.pixel,
        function (feature, layer) {
            return feature;
        });

    var deltaX = evt.coordinate[0] - this.coordinate_[0];
    var deltaY = evt.coordinate[1] - this.coordinate_[1];

    var geometry = /** @type {ol.geom.SimpleGeometry} */
        (this.feature_.getGeometry());
    geometry.translate(deltaX, deltaY);

    this.coordinate_[0] = evt.coordinate[0];
    this.coordinate_[1] = evt.coordinate[1];
};


/**
 * @param {ol.MapBrowserEvent} evt Event.
 */
app.Drag.prototype.handleMoveEvent = function (evt) {
    if (this.cursor_) {
        var map = evt.map;
        var feature = map.forEachFeatureAtPixel(evt.pixel,
            function (feature, layer) {
                return feature;
            });
        var element = evt.map.getTargetElement();
        if (feature) {
            if (element.style.cursor != this.cursor_) {
                this.previousCursor_ = element.style.cursor;
                element.style.cursor = this.cursor_;
            }
        } else if (this.previousCursor_ !== undefined) {
            element.style.cursor = this.previousCursor_;
            this.previousCursor_ = undefined;
        }
    }
};


/**
 * @param {ol.MapBrowserEvent} evt Map browser event.
 * @return {boolean} `false` to stop the drag sequence.
 */
app.Drag.prototype.handleUpEvent = function (evt) {
    var ar = ol.proj.transform(this.coordinate_, 'EPSG:3857', 'EPSG:4326');
    $('#lon').val(ar[0].toFixed(4));
    $('#lat').val(ar[1].toFixed(4));
    this.coordinate_ = null;
    this.feature_ = null;
    return false;
};

$(document).ready(
    function () {
        feature = new ol.Feature(new ol.geom.Point(
            ol.proj.transform([-93., 42.], 'EPSG:4326', 'EPSG:3857')
        ));
        /*
         * controls = { drag: new OpenLayers.Control.DragFeature(vectors, {
         * onComplete: function(feature, pixel) { geo =
         * feature.geometry.clone();
         * geo.transform(map.getProjectionObject(), proj);
         * document.getElementById('lon').value = geo.x;
         * document.getElementById('lat').value = geo.y; } }) };
         */
        new ol.Map({
            interactions: ol.interaction.defaults().extend([new app.Drag()]),
            target: 'map',
            controls: [new ol.control.Zoom()],
            layers: [new ol.layer.Tile({
                title: 'OpenStreetMap',
                visible: true,
                source: new ol.source.OSM()
            }), new ol.layer.Vector({
                source: new ol.source.Vector({
                    projection: 'EPSG:3857',
                    features: [feature]
                }),
                style: new ol.style.Style({
                    image: new ol.style.Icon(/** @type {olx.style.IconOptions} */
                        ({
                            anchor: [0.5, 46],
                            anchorXUnits: 'fraction',
                            anchorYUnits: 'pixels',
                            opacity: 0.95,
                            src: '/images/marker.png'
                        })),
                    stroke: new ol.style.Stroke({
                        width: 3,
                        color: [255, 0, 0, 1]
                    }),
                    fill: new ol.style.Fill({
                        color: [0, 0, 255, 0.6]
                    })
                })
            })],
            view: new ol.View({
                projection: 'EPSG:3857',
                center: ol.proj.transform([-94.5, 42.1], 'EPSG:4326',
                    'EPSG:3857'),
                zoom: 7
            })
        }); // end of map
    }); // end of onReady()