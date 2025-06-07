#!/usr/bin/env node

// Test script to validate ES module imports
console.log('🧪 Testing ES module imports...');

async function testImports() {
    try {
        // Test domUtils imports
        const domUtils = await import('../src/domUtils.js');
        console.log('✅ domUtils.js imported successfully');
        
        // Verify key functions exist
        const expectedFunctions = ['escapeHTML', 'getElement', 'requireSelectElement', 'requireInputElement'];
        for (const fn of expectedFunctions) {
            if (typeof domUtils[fn] !== 'function') {
                throw new Error(`Missing or invalid function: ${fn}`);
            }
        }
        console.log(`✅ domUtils exports ${expectedFunctions.length} expected functions`);
        
        // Test iemdata imports
        const iemdata = await import('../src/iemdata.js');
        console.log('✅ iemdata.js imported successfully');
                
        const expectedData = ['states', 'vtec_phenomena_dict', 'vtec_sig_dict'];
        for (const key of expectedData) {
            if (!Array.isArray(iemdata[key])) {
                throw new Error(`Missing or invalid data array: ${key}`);
            }
        }
        console.log(`✅ iemdata contains ${expectedData.length} expected data arrays`);
        
        // Test main index imports
        const main = await import('../src/index.js');
        console.log('✅ index.js imported successfully');
        
        // Verify re-exports work
        if (typeof main.escapeHTML !== 'function') {
            throw new Error('escapeHTML not re-exported from index.js');
        }
        console.log('🎉 All import tests passed!');
        
    } catch (error) {
        console.error('❌ Import test failed:', error.message);
        process.exit(1);
    }
}

testImports();
