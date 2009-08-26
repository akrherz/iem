/*
 * Copyright (C) 2008 Eric Lemoine, Camptocamp France SAS
 *
 * This file is part of GeoExt
 *
 * GeoExt is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * GeoExt is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with GeoExt.  If not, see <http://www.gnu.org/licenses/>.
 */

/**
 * @requires GeoExt/data/FeatureStoreMediator.js
 */

Ext.namespace('GeoExt', 'GeoExt.data');

/**
 * Class: GeoExt.data.LayerStoreMediator
 *
 * This class is to be used when one wants to insert, remove, and
 * update features in a grid as a result of features being inserted,
 * removed, modified in a vector layer.
 *
 * Usage example:
 * (start code)
 * var layer = new OpenLayers.Layer.Vector("vector");
 * var store = new Ext.data.Store({
 *     reader: new GeoExt.data.FeatureReader(
 *         {}, [{name: "name", type: "string"}]
 *     )
 * });
 * var mediator = new GeoExt.data.LayerStoreMediator({
 *     store: store,
 *     filter: function(feature) {
 *         return feature.state != OpenLayers.State.UNKNOWN;
 *     }
 * });
 * (end)
 */

/**
 * Constructor: GeoExt.data.LayerStoreMediator
 * Create an instance of GeoExt.data.LayerStoreMediator.
 *
 * Parameters:
 * config - {Object} A config object used to set the layer
 *     store mediator's properties (see below for the list
 *     of supported properties), and configure it with the
 *     Ext store; see the usage example above.
 *
 * Returns:
 * {<GeoExt.data.LayerStoreMediator>}
 */
GeoExt.data.LayerStoreMediator = function(config) {
    var store = config.store;
    // no need to place the store in the instance
    delete config.store;
    Ext.apply(this, config);
    if (!this.layer) {
        OpenLayers.Console.error(
            "layer is missing in config");
    }
    this.featureStoreMediator = new GeoExt.data.FeatureStoreMediator({
        store: store
    });
    if (this.autoActivate) {
        this.activate();
    }
};

GeoExt.data.LayerStoreMediator.prototype = {
    /**
     * APIProperty: layer
     * {<OpenLayers.Layer.Vector>} The vector layer.
     */
    layer: null,

    /**
     * APIProperty: filter
     * {Function} a filter function called for each feature to be
     * inserted, the feature is passed as an argument to the function,
     * if it returns true the feature is inserted into the store,
     * otherwise the feature is not inserted.
     */
    filter: null,

    /**
     * APIProperty: autoActivate
     * {Boolean} True if the mediator must be activated as part of
     * its creation, false otherwise; if false then the mediator must
     * be explicitely activate using the activate method; defaults
     * to true.
     */
    autoActivate: true,

    /**
     * Property: active
     * {Boolean}
     */
    active: false,

    /**
     * Property: featureStoreMediator
     * {<GeoExt.data.featureStoreMediator>} An internal
     * feature store mediator for manually adding features to the
     * Ext store.
     */
    featureStoreMediator: null,

    /**
     * APIMethod: activate
     * Activate the mediator.
     *
     * Returns:
     * {Boolean} - False if the mediator was already active, true
     * otherwise.
     */
    activate: function() {
        if (!this.active) {
            this.layer.events.on({
                featuresadded: this.update,
                featuresremoved: this.update,
                featuremodified: this.update,
                scope: this
            });
            this.active = true;
            return true;
        }
        return false;
    },

    /**
     * APIMethod: deactivate
     * Deactivate the mediator.
     *
     * Returns:
     * {Boolean} - False if the mediator was already deactive, true
     * otherwise.
     */
    deactivate: function() {
        if (this.active) {
            this.layer.events.un({
                featuresadded: this.update,
                featuresremoved: this.update,
                featuremodified: this.update,
                scope: this
            });
            return true;
        }
        return false;
    },

    /**
     * Method: update
     *      Called when features are added, removed or modified. This
     *      function empties the store, loops over the features in
     *      the layer, and for each feature calls the user-defined
     *      filter function, if the return value of the filter function
     *      evaluates to true the feature is added to the store.
     */
    update: function() {
        this.featureStoreMediator.addFeatures(
            this.layer.features,
            {append: false, filter: this.filter});
    }
};
