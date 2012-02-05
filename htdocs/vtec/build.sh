#!/bin/sh

# --warning_level VERBOSE
java -jar ~/lib/compiler.jar --js=js/wfos.js  \
--js=js/RowExpander.js --js=js/Printer-all.js \
--js=../ext/ux/menu/EditableItem.js --js=../ext/ux/grid/GridFilters.js \
--js=../ext/ux/grid/filter/Filter.js --js=../ext/ux/form/Spinner.js \
--js=../ext/ux/form/SpinnerStrategy.js --js=../ext/ux/grid/filter/StringFilter.js \
--js=js/overrides.js --js=js/RadarPanel.js --js=js/LSRFeatureStore.js \
--js=js/SBWFeatureStore.js --js=js/SBWIntersectionFeatureStore.js \
--js=js/Ext.ux.SliderTip.js --js=js/static.js \
--js_output_file=app.js
