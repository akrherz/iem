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
 * @requires GeoExt/data/FeatureReader.js
 */

Ext.namespace('GeoExt', 'GeoExt.data');

/**
 * Class: GeoExt.data.FeatureStoreMediator
 * This class is to be used when one wants to insert features in a store.
 *
 * Usage example:
 * (start code)
 * var store = new Ext.data.Store({
 *     reader: new GeoExt.data.FeatureReader(
 *         {}, [{name: "name", type: "string"}]
 *     )
 * });
 * var mediator = new GeoExt.data.FeatureStoreMediator({
 *     store: store,
 *     append: false,
 *     filter: function(feature) {
 *         return feature.state != OpenLayers.State.UNKNOWN;
 *     }
 * });
 * (end)
 */

/**
 * Constructor: GeoExt.data.FeatureStoreMediator
 * Create an instance of GeoExt.data.FeatureStoreMediator
 *
 * Parameters:
 * config - {Object} A config object used to set the feature
 *     store mediator's properties, see below for the list
 *     of supported properties.
 *
 * Returns:
 * {<GeoExt.data.FeatureStoreMediator>}
 */
GeoExt.data.FeatureStoreMediator = function(config){
    Ext.apply(this, config);
    if (!this.store) {
        OpenLayers.Console.error(
            "store is missing in the config");
    }
    if (!(this.store.reader instanceof GeoExt.data.FeatureReader)) {
        OpenLayers.Console.error(
            "store does not use a FeatureReader");
    }
};

GeoExt.data.FeatureStoreMediator.prototype = {
    /**
     * APIProperty: store
     * {Ext.data.Store} An Ext data store
     */
    store: null,

    /**
     * APIProperty: append
     * {Boolean} False if the store must be cleared before adding new
     * features into it, false otherwise; defaults to true.
     */
    append: true,

    /**
     * APIProperty: filter
     * {Function} a filter function called for each feature to be
     * inserted, the feature is passed as an argument to the function,
     * if it returns true the feature is inserted into the store,
     * otherwise the feature is not inserted.
     */
    filter: null,

    /**
     * APIMethod: addFeatures
     *      Add features to the store.
     * 
     * Parameters:
     * features - {<OpenLayers.Feature.Vector>} or
     *     {Array{<OpenLayers.Feature.Vector>}} A feature or an
     *     array of features to add to the store.
     * config - a config object which can include the properties
     *     "append" and "filter", if set these properties will
     *     override that set in the object.
     */
    addFeatures: function(features, config) {
        if (!Ext.isArray(features)) {
            features = [features];
        }
        config = OpenLayers.Util.applyDefaults(config,
            {append: this.append, filter: this.filter});
        var toAdd = features;
        if (config.filter) {
            toAdd = [];
            var feature;
            for (var i = 0, len = features.length; i < len; i++) {
                feature = features[i];
                if (config.filter(feature)) {
                    toAdd.push(feature);
                }
            }
        }
        // because of a bug in Ext if config.append is false we clean
        // the store ourself and always pass true to loadData, there
        // are cases where passing false to loadData results in Ext
        // trying to dereference an undefined value, see the unit
        // tests test_ExtBug and text_addFeatures_ExtBug for 
        // concrete examples
        if (!config.append) {
            this.store.removeAll();
        }
        this.store.loadData(toAdd, true);
    },

    /**
     * APIMethod: removeFeatures
     *      Remove features from the store.
     *
     * Parameters:
     * features - {<OpenLayers.Feature.Vector>} or
     *      {Array{<OpenLayers.Feature.Vector>}} A feature or an
     *      array of features to remove from the store. If null
     *      all the features in the store are removed.
     */
    removeFeatures: function(features) {
        if (!features) {
            this.store.removeAll();
        } else {
            if (!Ext.isArray(features)) {
                features = [features];
            }
            for (var i = 0, len = features.length; i < len; i++) {
                var feature = features[i];
                var r = this.store.getById(feature.id);
                if (r !== undefined) {
                    this.store.remove(r);
                }
            }
        }
    }
};
