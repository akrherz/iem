#!/usr/bin/env node

// Simple test runner for iemjs package
console.log('🧪 Running iemjs test suite...\n');

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const tests = [
    { name: 'Syntax Validation', script: 'test:syntax' },
    { name: 'Import Tests', script: 'test:imports' },
    { name: 'Export Tests', script: 'test:exports' }
];

function runTest(testName, script) {
    return new Promise((resolve, reject) => {
        console.log(`🔄 Running: ${testName}...`);
        
        const npm = spawn('npm', ['run', script], {
            stdio: 'pipe',
            cwd: path.join(__dirname, '..')
        });
        
        let stdout = '';
        let stderr = '';
        
        npm.stdout.on('data', (data) => {
            stdout += data.toString();
        });
        
        npm.stderr.on('data', (data) => {
            stderr += data.toString();
        });
        
        npm.on('close', (code) => {
            if (code === 0) {
                console.log(`✅ ${testName} passed`);
                resolve(stdout);
            } else {
                console.error(`❌ ${testName} failed`);
                console.error(stderr);
                reject(new Error(`${testName} failed with code ${code}`));
            }
        });
    });
}

async function runAllTests() {
    let passedTests = 0;
    const totalTests = tests.length;
    
    for (const test of tests) {
        try {
            await runTest(test.name, test.script);
            passedTests++;
        } catch (error) {
            console.error(`\n💥 Test suite failed at: ${test.name}`);
            console.error(`Error: ${error.message}`);
            process.exit(1);
        }
    }
    
    console.log(`\n🎉 All tests passed! (${passedTests}/${totalTests})`);
    console.log('📦 Package is ready for publishing!');
}

// Run the tests
runAllTests().catch(error => {
    console.error('💥 Test runner failed:', error.message);
    process.exit(1);
});

export { runAllTests };
