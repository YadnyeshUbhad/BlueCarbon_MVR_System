const { ethers } = require("hardhat");

async function main() {
  console.log("Starting deployment of Blue Carbon MRV Smart Contracts...");

  // Get deployer account
  const [deployer] = await ethers.getSigners();
  console.log(`Deploying contracts with account: ${deployer.address}`);
  console.log(`Account balance: ${ethers.formatEther(await ethers.provider.getBalance(deployer.address))} POL`);

  // Deploy MRV Registry first
  console.log("\n=== Deploying MRV Registry ===");
  const MRVRegistry = await ethers.getContractFactory("MRVRegistry");
  const mrvRegistry = await MRVRegistry.deploy();
  await mrvRegistry.waitForDeployment();
  
  const mrvAddress = await mrvRegistry.getAddress();
  console.log(`✅ MRV Registry deployed to: ${mrvAddress}`);
  
  // Wait for a few block confirmations
  console.log("Waiting for confirmations...");
  // Note: ethers v6 handles confirmations automatically

  // Deploy Carbon Credit Token with MRV Registry address
  console.log("\n=== Deploying Carbon Credit Token ===");
  const CarbonCreditToken = await ethers.getContractFactory("CarbonCreditToken");
  const carbonToken = await CarbonCreditToken.deploy(
    mrvAddress, // MRV Registry address
    deployer.address     // Admin address
  );
  await carbonToken.waitForDeployment();
  
  const carbonAddress = await carbonToken.getAddress();
  console.log(`✅ Carbon Credit Token deployed to: ${carbonAddress}`);
  
  // Wait for confirmations
  // Note: ethers v6 handles confirmations automatically

  // Setup initial roles and permissions
  console.log("\n=== Setting up roles and permissions ===");
  
  // Grant MINTER_ROLE to deployer for initial setup
  const MINTER_ROLE = await carbonToken.MINTER_ROLE();
  await carbonToken.grantMinterRole(deployer.address);
  console.log("✅ Granted MINTER_ROLE to deployer");

  // Grant VERIFIER_ROLE to deployer for initial setup
  await mrvRegistry.grantVerifierRole(deployer.address);
  console.log("✅ Granted VERIFIER_ROLE to deployer");

  // Verify contract setup
  console.log("\n=== Verifying Contract Setup ===");
  
  // Check MRV Registry
  const totalRecords = await mrvRegistry.getTotalRecords();
  console.log(`MRV Registry total records: ${totalRecords}`);
  
  // Check Carbon Token
  const tokenName = await carbonToken.name();
  const tokenSymbol = await carbonToken.symbol();
  const tokenDecimals = await carbonToken.decimals();
  const totalBatches = await carbonToken.getTotalBatches();
  
  console.log(`Carbon Token: ${tokenName} (${tokenSymbol})`);
  console.log(`Decimals: ${tokenDecimals}`);
  console.log(`Total batches: ${totalBatches}`);

  // Save deployment information
  const network = await ethers.provider.getNetwork();
  const deploymentInfo = {
    network: {
      name: network.name,
      chainId: network.chainId.toString()
    },
    timestamp: new Date().toISOString(),
    deployer: deployer.address,
    contracts: {
      MRVRegistry: {
        address: mrvAddress
      },
      CarbonCreditToken: {
        address: carbonAddress
      }
    }
  };

  console.log("\n=== Deployment Summary ===");
  console.log("Network:", deploymentInfo.network.name);
  console.log("Chain ID:", deploymentInfo.network.chainId);
  console.log("Deployer:", deploymentInfo.deployer);
  console.log("MRV Registry:", deploymentInfo.contracts.MRVRegistry.address);
  console.log("Carbon Token:", deploymentInfo.contracts.CarbonCreditToken.address);

  // Save deployment info to file
  const fs = require('fs');
  const path = require('path');
  
  const deploymentsDir = path.join(__dirname, '..', 'deployments');
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }
  
  const deploymentFile = path.join(
    deploymentsDir, 
    `deployment-${deploymentInfo.network.name}-${Date.now()}.json`
  );
  
  fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));
  console.log(`\n📄 Deployment info saved to: ${deploymentFile}`);

  // Create environment variables file
  const envContent = `
# Blue Carbon MRV Smart Contract Addresses
# Network: ${deploymentInfo.network.name} (Chain ID: ${deploymentInfo.network.chainId})
# Deployed: ${deploymentInfo.timestamp}

MRV_REGISTRY_ADDRESS=${mrvAddress}
CARBON_TOKEN_ADDRESS=${carbonAddress}
DEPLOYER_ADDRESS=${deployer.address}
NETWORK_NAME=${deploymentInfo.network.name}
CHAIN_ID=${deploymentInfo.network.chainId}
`;

  const envFile = path.join(__dirname, '..', '.env.contracts');
  fs.writeFileSync(envFile, envContent);
  console.log(`📄 Contract addresses saved to: ${envFile}`);

  console.log("\n🎉 Deployment completed successfully!");
  
  // Instructions for next steps
  console.log("\n=== Next Steps ===");
  console.log("1. Verify contracts on block explorer if deploying to public network");
  console.log("2. Update frontend configuration with contract addresses");
  console.log("3. Set up additional verifiers and minters as needed");
  console.log("4. Test the system with sample MRV data");
  
  if (deploymentInfo.network.name !== "hardhat" && deploymentInfo.network.name !== "localhost") {
    console.log("\n=== Verification Commands ===");
    console.log(`npx hardhat verify --network ${deploymentInfo.network.name} ${mrvAddress}`);
    console.log(`npx hardhat verify --network ${deploymentInfo.network.name} ${carbonAddress} "${mrvAddress}" "${deployer.address}"`);
  }
}

// Handle deployment errors
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:");
    console.error(error);
    process.exit(1);
  });