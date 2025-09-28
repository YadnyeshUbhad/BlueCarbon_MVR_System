# Mumbai Testnet Deployment Guide
## Blue Carbon MRV Smart Contracts - FREE Deployment

This guide will help you deploy your Blue Carbon MRV smart contracts to Polygon Mumbai testnet **completely free**.

## Prerequisites

### 1. Setup MetaMask Wallet
- Install [MetaMask browser extension](https://metamask.io/)
- Create or import a wallet
- **Important**: Export your private key (Account Details > Export Private Key)

### 2. Add Mumbai Testnet to MetaMask
- Network Name: `Mumbai Testnet`
- New RPC URL: `https://rpc-mumbai.maticvigil.com`
- Chain ID: `80001`
- Currency Symbol: `MATIC`
- Block Explorer URL: `https://mumbai.polygonscan.com/`

### 3. Get FREE Test MATIC Tokens
Visit any of these faucets to get free MATIC for deployment:
- [Polygon Faucet](https://faucet.polygon.technology/)
- [Alchemy Mumbai Faucet](https://mumbaifaucet.com/)
- [QuickNode Faucet](https://faucet.quicknode.com/polygon/mumbai)

You need ~0.01 MATIC for deployment (completely free).

## Deployment Steps

### 1. Configure Environment
Edit the `.env` file and add your private key:

```bash
# Replace with your actual private key from MetaMask
PRIVATE_KEY=0x1234567890abcdef...
```

**⚠️ SECURITY WARNING**: Never share your private key or commit it to version control!

### 2. Install Dependencies
```bash
cd D:\sih_project\blockchain
npm install
```

### 3. Compile Contracts
```bash
npm run compile
```

### 4. Deploy to Mumbai Testnet
```bash
npm run deploy:mumbai
```

## What Happens During Deployment

The deployment script will:

1. **Deploy MRVRegistry Contract** - Manages blue carbon MRV records
2. **Deploy CarbonCreditToken Contract** - ERC-1155 tokens for carbon credits
3. **Setup Roles & Permissions** - Grant initial admin/verifier/minter roles
4. **Verify Setup** - Test basic functionality
5. **Save Deployment Info** - Create deployment record and contract addresses
6. **Generate Environment File** - `.env.contracts` with addresses

## Expected Output

```
Starting deployment of Blue Carbon MRV Smart Contracts...
Deploying contracts with account: 0x1234...
Account balance: 0.1 MATIC

=== Deploying MRV Registry ===
✅ MRV Registry deployed to: 0xABC123...

=== Deploying Carbon Credit Token ===
✅ Carbon Credit Token deployed to: 0xDEF456...

=== Setting up roles and permissions ===
✅ Granted MINTER_ROLE to deployer
✅ Granted VERIFIER_ROLE to deployer

=== Deployment Summary ===
Network: mumbai
Chain ID: 80001
MRV Registry: 0xABC123...
Carbon Token: 0xDEF456...

🎉 Deployment completed successfully!
```

## Post-Deployment

### 1. Contract Addresses
Your deployed contract addresses will be saved in:
- `deployments/deployment-mumbai-[timestamp].json`
- `.env.contracts` (for easy importing)

### 2. Verify on PolygonScan (Optional)
```bash
# Run the verification commands shown in deployment output
npx hardhat verify --network mumbai 0xYourMRVRegistryAddress
npx hardhat verify --network mumbai 0xYourCarbonTokenAddress "0xMRVRegistryAddress" "0xDeployerAddress"
```

### 3. View on Block Explorer
- Visit [Mumbai PolygonScan](https://mumbai.polygonscan.com/)
- Search for your contract addresses
- View transactions and contract details

## Cost Breakdown

| Operation | Cost (MATIC) | USD Equivalent |
|-----------|--------------|----------------|
| MRV Registry Deploy | ~0.003 | ~$0.003 |
| Carbon Token Deploy | ~0.005 | ~$0.005 |
| Role Setup (2 txns) | ~0.002 | ~$0.002 |
| **TOTAL** | **~0.01 MATIC** | **~$0.01** |

## Troubleshooting

### Common Issues:

1. **"Insufficient funds"**
   - Get more test MATIC from faucets listed above

2. **"Network connection failed"**
   - Try alternative RPC URL in `.env`:
   ```
   MUMBAI_RPC_URL=https://polygontestapi.terminet.io/rpc
   ```

3. **"Private key format invalid"**
   - Ensure private key starts with `0x`
   - Remove any quotes or spaces

4. **"Compilation failed"**
   - Run `npm run clean` then `npm run compile`

## Next Steps

1. **Update Frontend**: Use contract addresses from `.env.contracts`
2. **Add More Verifiers**: Grant VERIFIER_ROLE to trusted accounts
3. **Test System**: Create sample MRV records and mint carbon credits
4. **Production Deploy**: Use same process on Polygon mainnet when ready

## Support

- [Polygon Documentation](https://docs.polygon.technology/)
- [Hardhat Documentation](https://hardhat.org/docs)
- [OpenZeppelin Docs](https://docs.openzeppelin.com/)

## Important Notes

- Mumbai testnet is for testing only
- Test MATIC has no real value
- Contracts deployed on Mumbai won't work on Polygon mainnet
- Keep your private key secure and never share it
- This deployment is completely FREE using test tokens