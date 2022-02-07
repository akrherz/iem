/* A combination Openlayers Map + DataTable

Example:

<div
    class="iem-maptable row"
    data-label-field="sname"
    data-geojson-src="/geojson/networks.geojson?network=IA_ASOS">
</div>

*/
// https://datatables.net/plug-ins/api/row().show()
$.fn.dataTable.Api.register('row().show()', function () {
    var page_info = this.table().page.info();
    // Get row index
    var new_row_index = this.index();
    // Row position
    var row_position = this.table()
        .rows({ search: 'applied' })[0]
        .indexOf(new_row_index);
    // Already on right page ?
    if ((row_position >= page_info.start && row_position < page_info.end) || row_position < 0) {
        // Return row object
        return this;
    }
    // Find page number
    var page_to_display = Math.floor(row_position / this.table().page.len());
    // Go to that page
    this.table().page(page_to_display);
    // Return row object
    return this;
});

function get_style(color, text) {
    return new ol.style.Style({
        fill: new ol.style.Fill({
            color: 'rgba(255, 255, 255, 0.6)'
        }),
        text: new ol.style.Text({
            font: '14px Calibri,sans-serif',
            text: text,
            fill: new ol.style.Fill({
                color: color,
                width: 1
            }),
            stroke: new ol.style.Stroke({
                color: '#FFF',
                width: 3
            })
        })
    });
}

function getLabelForFeature(inst, feat) {
    var label = "TBD";
    if (inst.label_field == "id") {
        label = feat.getId();
    } else if (inst.label_field) {
        label = feat.get(inst.label_field).toString();
    }
    return label;
}

function highlightFeature(inst, feat) {
    if (inst.selectedFeature) {
        inst.selectedFeature.setStyle(null);
    }
    inst.selectedFeature = feat;
    feat.setStyle(get_style("#F00", getLabelForFeature(inst, feat)));
}

function init_map(idx, inst) {
    inst.selectedFeature;
    inst.vectorLayer = new ol.layer.Vector({
        title: 'Data',
        source: new ol.source.Vector({
            format: new ol.format.GeoJSON()
        }),
        style: function (feature) {
            var label = "TBD";
            return [get_style("#000", getLabelForFeature(inst, feature))];
        }
    });
    $.ajax({
        method: "GET",
        url: inst.geojson_src,
        dataType: "json",
        success: function (data) {
            if (data.meta) {
                inst.label_field = data.meta.propdefault;
                inst.proporder = data.meta.proporder;
            }
            inst.vectorLayer.getSource().addFeatures(
                (new ol.format.GeoJSON({ featureProjection: 'EPSG:3857' })).readFeatures(data)
            );
        }
    });
    inst.map = new ol.Map({
        target: inst.mapdiv,
        layers: [
            new ol.layer.Tile({
                title: 'OpenStreetMap',
                visible: true,
                source: new ol.source.OSM()
            }),
            inst.vectorLayer
        ],
        view: new ol.View({
            projection: 'EPSG:3857',
            center: [-10575351, 5160979],
            zoom: 3
        })
    });
    inst.map.on('click', function (evt) {
        var feature = inst.map.forEachFeatureAtPixel(evt.pixel,
            function (feature, layer) {
                return feature;
            });
        if (!feature) {
            return;
        }
        highlightFeature(inst, feature);
        var id = feature.getId();
        inst.table.rows().deselect();
        inst.table.row(
            inst.table.rows(function (idx, data, node) {
                if (data["id"] === id) {
                    inst.table.row(idx).select();
                    return true;
                }
                return false;
            })
        ).show().draw(false);

    });

    inst.vectorLayer.getSource().on('change', function (e) {
        if (inst.vectorLayer.getSource().getState() == 'ready' && inst.zoomReset === false) {
            inst.map.getView().fit(
                inst.vectorLayer.getSource().getExtent(),
                {
                    size: inst.map.getSize(),
                    padding: [50, 50, 50, 50]
                }
            );
            inst.zoomReset = true;
        }
        if (inst.table) {
            return;
        }
        var columns = [{ title: 'ID', data: 'id' }];
        $(inst.select).append(
            "<option value=\"id\">ID</option>"
        );
        var data = [];
        // If we have a column order, use it!
        if (inst.proporder) {
            inst.proporder.forEach(function (val) {
                columns.push({ title: val, data: val })
                $(inst.select).append(
                    "<option value=\"" + val + "\">" + val + "</option>"
                );
            });
        }
        inst.vectorLayer.getSource().getFeatures().forEach(function (feat) {
            if (columns.length == 1) {
                feat.getKeys().forEach(function (key) {
                    if (key == "geometry") {
                        return;
                    }
                    $(inst.select).append(
                        "<option value=\"" + key + "\">" + key + "</option>"
                    );
                    columns.push({ title: key, data: key });
                });
            }
            if (!inst.label_field) {
                inst.label_field = "id";
            }
            $(inst.select).val(inst.label_field);
            var props = feat.getProperties();
            props.id = feat.getId();
            data.push(props);
        });
        inst.table = $("#maptable-table" + idx).DataTable({
            columns: columns,
            data: data,
            select: true
        });
        inst.table.on('select', function (e, dt, type, indexes) {
            if (type !== 'row') {
                return;
            }
            var featid = dt.row(indexes).data()["id"];
            var feat = inst.vectorLayer.getSource().getFeatureById(featid);
            highlightFeature(inst, feat);
        });
    });

    // var layerSwitcher = new ol.control.LayerSwitcher();
    // inst.map.addControl(layerSwitcher);
}


function init(idx, div) {
    // Setup the given div for usage
    // Add left and right hand side divs
    var inst = {};
    inst.proporder;
    inst.zoomReset = false;
    inst.geojson_src = $(div).data('geojson-src');
    inst.label_field = $(div).data('label-field');
    var leftcol = document.createElement('div');
    leftcol.className = 'col-md-6';
    inst.mapdiv = document.createElement('div');
    inst.mapdiv.style = "height: 400px";
    leftcol.append(inst.mapdiv);
    var p = document.createElement('p');
    var t = document.createTextNode("Select variable for labels:");
    p.appendChild(t);
    inst.select = document.createElement('select');
    p.appendChild(inst.select);
    $(inst.select).on("change", function () {
        inst.label_field = this.value;
        inst.vectorLayer.setStyle(inst.vectorLayer.getStyle());
        if (inst.selectedFeature) {
            highlightFeature(inst, inst.selectedFeature);
        }
    });
    leftcol.appendChild(p);
    div.append(leftcol);
    var tablediv = document.createElement('div');
    tablediv.className = 'col-md-6';
    inst.table;
    var tableElement = document.createElement('table');
    tableElement.id = "maptable-table" + idx;
    tablediv.appendChild(tableElement);
    div.append(tablediv);

    init_map(idx, inst);
    return inst;
}

// https://learn.jquery.com/plugins/basic-plugin-creation/
(function ($) {

    $.fn.MapTable = function (options) {
        var res = [];
        this.each(function (idx, item) {
            res.push(init(idx, item));
        });
        return res;
    };

}(jQuery));