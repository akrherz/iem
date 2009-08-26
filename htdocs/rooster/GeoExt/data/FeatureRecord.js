/* Copyright (C) 2008-2009 The Open Source Geospatial Foundation
 * Published under the BSD license.
 * See http://geoext.org/svn/geoext/core/trunk/license.txt for the full text
 * of the license.
 * 
 * pending approval */

Ext.namespace("GeoExt.data");

/**
 * Class: GeoExt.data.FeatureRecord
 * A subclass of {Ext.data.Record} which provides a special record that
 * represents an {OpenLayers.Feature}. This record will always have at
 * least "feature", "fid", and "state" fields in its data. The id of
 * the record will be the same as the id of the feature it represents.
 * 
 * Inherits from
 * - {Ext.data.Record}
 */
GeoExt.data.FeatureRecord = Ext.data.Record.create([
    {name: "feature"}, {name: "state"}, {name: "fid"}
]);

/**
 * APIMethod: copy
 * Creates a copy of this Record.
 * 
 * Paremters:
 * id - {String} (optional) A new Record id.
 *
 * Returns:
 * {GeoExt.data.LayerRecord} A new layer record.
 */
GeoExt.data.FeatureRecord.prototype.copy = function(id) {
    var feature = this.get("feature") && this.get("feature").clone();
    return new this.constructor(
        Ext.applyIf({feature: feature}, this.data),
        id || this.id
    );
};

/**
 * APIFunction: GeoExt.data.FeatureRecord.create
 * Creates a constructor for a FeatureRecord, optionally with additional
 * fields.
 * 
 * Parameters:
 * o - {Array} Field definition as in {Ext.data.Record.create}. Can be omitted
 *     if no additional fields are required (records will always have fields
 *     {OpenLayers.Feature} "feature", {String} "state" and {String} "fid".
 *
 * Returns:
 * {Function} A specialized {<GeoExt.data.FeatureRecord>} constructor.
 */
GeoExt.data.FeatureRecord.create = function(o) {
    var f = Ext.extend(GeoExt.data.FeatureRecord, {});
    var p = f.prototype;
    if(o) {
        for(var i = 0, len = o.length; i < len; i++){
            p.fields.add(new Ext.data.Field(o[i]));
        }
    }
    return f;
};
