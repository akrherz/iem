#!/usr/bin/env node

// Test script to validate package exports configuration
console.log('🧪 Testing package exports...');

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function testExports() {
    try {
        // Read package.json
        const packageJsonPath = path.join(__dirname, '..', 'package.json');
        const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
        console.log(`📦 Testing package: ${packageJson.name}@${packageJson.version}`);
        
        // Check main entry point
        if (!packageJson.main) {
            throw new Error('No main entry point defined');
        }
        
        const mainPath = path.join(__dirname, '..', packageJson.main);
        if (!fs.existsSync(mainPath)) {
            throw new Error(`Main entry point does not exist: ${packageJson.main}`);
        }
        console.log(`✅ Main entry point exists: ${packageJson.main}`);
        
        // Check exports
        if (!packageJson.exports || typeof packageJson.exports !== 'object') {
            throw new Error('No exports defined');
        }
        
        console.log('🔍 Checking exports...');
        for (const [exportName, exportPath] of Object.entries(packageJson.exports)) {
            const fullExportPath = path.join(__dirname, '..', exportPath);
            if (!fs.existsSync(fullExportPath)) {
                throw new Error(`Export path does not exist: ${exportPath} (for export: ${exportName})`);
            }
            console.log(`  ✅ ${exportName} -> ${exportPath}`);
        }
        
        // Check files array
        if (!packageJson.files || !Array.isArray(packageJson.files)) {
            throw new Error('No files array defined');
        }
        
        console.log('🔍 Checking files array...');
        for (const filePattern of packageJson.files) {
            // Simple check for basic patterns
            if (filePattern.includes('**')) {
                const baseDir = filePattern.split('**')[0];
                if (baseDir) {
                    const fullBaseDir = path.join(__dirname, '..', baseDir);
                    if (!fs.existsSync(fullBaseDir)) {
                        throw new Error(`Base directory for pattern does not exist: ${baseDir}`);
                    }
                }
            } else {
                const fullFilePath = path.join(__dirname, '..', filePattern);
                if (!fs.existsSync(fullFilePath)) {
                    console.warn(`⚠️  File pattern may not match any files: ${filePattern}`);
                }
            }
            console.log(`  ✅ ${filePattern}`);
        }
        
        // Test that we can simulate npm pack
        console.log('📦 Validating package structure...');
        
        // Check for required metadata
        const requiredFields = ['name', 'version', 'description', 'license'];
        for (const field of requiredFields) {
            if (!packageJson[field]) {
                throw new Error(`Missing required field: ${field}`);
            }
        }
        console.log('✅ All required package.json fields present');
        
        console.log('🎉 All export tests passed!');
        
    } catch (error) {
        console.error('❌ Export test failed:', error.message);
        process.exit(1);
    }
}

testExports();
