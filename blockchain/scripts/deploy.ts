import { ethers } from "hardhat"; // This is correct for Hardhat runtime environment

async function main() {
  const [deployer] = await ethers.getSigners();

  const Token = await ethers.getContractFactory("CarbonCreditToken");
  const token = await Token.deploy(deployer.address);
  await token.waitForDeployment();
  console.log("CarbonCreditToken deployed to:", await token.getAddress());

  const Registry = await ethers.getContractFactory("MRVRegistry");
  const registry = await Registry.deploy(deployer.address, await token.getAddress());
  await registry.waitForDeployment();
  console.log("MRVRegistry deployed to:", await registry.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});