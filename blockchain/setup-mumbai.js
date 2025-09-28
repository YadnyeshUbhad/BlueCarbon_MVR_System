#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🚀 Blue Carbon MRV Smart Contracts - Mumbai Setup');
console.log('================================================\n');

// Check if .env exists and has private key
const envPath = path.join(__dirname, '.env');
let needsPrivateKey = false;

if (!fs.existsSync(envPath)) {
  console.log('❌ .env file not found');
  needsPrivateKey = true;
} else {
  const envContent = fs.readFileSync(envPath, 'utf8');
  if (!envContent.includes('PRIVATE_KEY=0x') || envContent.includes('your_wallet_private_key_here')) {
    console.log('❌ Private key not configured in .env');
    needsPrivateKey = true;
  }
}

if (needsPrivateKey) {
  console.log('\n📋 SETUP REQUIRED:');
  console.log('1. Get your private key from MetaMask:');
  console.log('   - MetaMask → Account Details → Export Private Key');
  console.log('2. Edit .env file and replace:');
  console.log('   PRIVATE_KEY=your_wallet_private_key_here');
  console.log('   with:');
  console.log('   PRIVATE_KEY=0x123456789abcdef... (your actual key)');
  console.log('\n3. Get free test MATIC from:');
  console.log('   - https://faucet.polygon.technology/');
  console.log('   - https://mumbaifaucet.com/');
  console.log('\n4. Then run this script again!\n');
  process.exit(1);
}

console.log('✅ Environment configuration found');

// Check node modules
if (!fs.existsSync(path.join(__dirname, 'node_modules'))) {
  console.log('📦 Installing dependencies...');
  try {
    execSync('npm install', { stdio: 'inherit', cwd: __dirname });
    console.log('✅ Dependencies installed');
  } catch (error) {
    console.log('❌ Failed to install dependencies');
    console.log('Run manually: npm install');
    process.exit(1);
  }
} else {
  console.log('✅ Dependencies already installed');
}

// Compile contracts
console.log('🔨 Compiling smart contracts...');
try {
  execSync('npm run compile', { stdio: 'inherit', cwd: __dirname });
  console.log('✅ Contracts compiled successfully');
} catch (error) {
  console.log('❌ Compilation failed');
  console.log('Check contract code for syntax errors');
  process.exit(1);
}

// Check for contracts
const contractsPath = path.join(__dirname, 'contracts');
const mrvRegistryExists = fs.existsSync(path.join(contractsPath, 'MRVRegistry.sol'));
const carbonTokenExists = fs.existsSync(path.join(contractsPath, 'CarbonCreditToken.sol'));

if (!mrvRegistryExists || !carbonTokenExists) {
  console.log('❌ Smart contract files missing');
  console.log('Expected:');
  console.log('- contracts/MRVRegistry.sol');
  console.log('- contracts/CarbonCreditToken.sol');
  process.exit(1);
}

console.log('✅ Smart contracts found');

// Ready to deploy
console.log('\n🎯 Ready for deployment!');
console.log('Run the following command to deploy to Mumbai testnet:');
console.log('npm run deploy:mumbai');
console.log('\n📖 For detailed instructions, see: MUMBAI_DEPLOYMENT.md');
console.log('\n💡 Expected cost: ~0.01 MATIC (FREE with testnet faucet)');

// Ask if user wants to proceed with deployment
const readline = require('readline');
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

rl.question('\n🚀 Would you like to deploy now? (y/N): ', (answer) => {
  rl.close();
  
  if (answer.toLowerCase() === 'y' || answer.toLowerCase() === 'yes') {
    console.log('\n🚀 Starting deployment to Mumbai testnet...\n');
    try {
      execSync('npm run deploy:mumbai', { stdio: 'inherit', cwd: __dirname });
    } catch (error) {
      console.log('\n❌ Deployment failed');
      console.log('Check the error messages above for troubleshooting');
      process.exit(1);
    }
  } else {
    console.log('\n👋 No problem! Run "npm run deploy:mumbai" when you\'re ready.');
    console.log('💡 Make sure you have test MATIC in your wallet first!');
  }
});