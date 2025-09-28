# 🚀 Quick Start: Deploy to Mumbai Testnet (FREE)

Deploy your Blue Carbon MRV smart contracts to Polygon Mumbai testnet in minutes - **completely free**!

## 🎯 One-Command Setup

```bash
cd D:\sih_project\blockchain
npm run setup:mumbai
```

This will:
- ✅ Check your environment setup
- ✅ Install dependencies  
- ✅ Compile smart contracts
- ✅ Guide you through deployment

## 📋 Prerequisites (5 minutes)

1. **MetaMask Wallet** 
   - Install [MetaMask](https://metamask.io/)
   - Export your private key: Account Details → Export Private Key

2. **Add Mumbai Network to MetaMask**
   - Network Name: `Mumbai Testnet`
   - RPC URL: `https://rpc-mumbai.maticvigil.com`
   - Chain ID: `80001`
   - Symbol: `MATIC`

3. **Get FREE Test MATIC**
   - Visit [Polygon Faucet](https://faucet.polygon.technology/)
   - Get ~0.1 MATIC (completely free)

4. **Configure Private Key**
   - Edit `.env` file
   - Replace `your_wallet_private_key_here` with your actual key

## ⚡ Manual Deployment

If you prefer step-by-step:

```bash
# 1. Install & compile
npm install
npm run compile

# 2. Deploy to Mumbai
npm run deploy:mumbai
```

## 📊 Expected Results

- **Cost**: ~0.01 MATIC (~$0.01 USD) 
- **Time**: 2-3 minutes
- **Contracts**: MRVRegistry + CarbonCreditToken
- **Output**: Contract addresses saved to `.env.contracts`

## 🎉 What You Get

- ✅ **MRVRegistry**: Manages blue carbon MRV records
- ✅ **CarbonCreditToken**: ERC-1155 carbon credits
- ✅ **Role Management**: Admin, Verifier, Minter roles
- ✅ **Mumbai Explorer**: View on [mumbai.polygonscan.com](https://mumbai.polygonscan.com)

## 📖 Need Help?

- **Detailed Guide**: See `MUMBAI_DEPLOYMENT.md`
- **Troubleshooting**: Common issues covered in guide
- **Support**: Check Polygon/Hardhat documentation

## 🔗 Next Steps

1. Update frontend with contract addresses
2. Test MRV record creation
3. Mint sample carbon credits
4. Deploy to Polygon mainnet for production

---

**🌊 Ready to deploy your Blue Carbon MRV system? Run `npm run setup:mumbai` now!**