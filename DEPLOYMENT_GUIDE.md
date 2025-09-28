# 🌊 Blue Carbon MRV System - Complete Deployment Guide

## Overview

This guide will help you deploy the complete **Blue Carbon MRV (Measurement, Reporting, and Verification) system** with **real blockchain integration** for carbon credit management.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask API     │    │   Blockchain    │
│   (Templates)   │◄──►│   (Python)      │◄──►│   (Hardhat)     │
│                 │    │                 │    │                 │
│ • Admin Portal  │    │ • REST APIs     │    │ • Smart         │
│ • NGO Dashboard │    │ • Web3          │    │   Contracts     │
│ • Industry UI   │    │   Integration   │    │ • Carbon        │
└─────────────────┘    └─────────────────┘    │   Credits       │
                                              └─────────────────┘
```

## 🚀 Quick Start (Automated)

### Option 1: One-Command Deployment

```bash
cd D:\sih_project
python start_fullstack.py
```

This automatically:
- ✅ Checks all requirements
- ✅ Starts local blockchain (Hardhat)
- ✅ Deploys smart contracts
- ✅ Starts Flask web application
- ✅ Provides all access URLs

**Expected Output:**
```
🌊 BLUE CARBON MRV FULL STACK DEPLOYMENT
========================================
Starting blockchain-enabled carbon credit management system...

🔍 Checking requirements...
✅ Node.js: v20.19.0
✅ Python dependencies: OK
✅ All requirements met!

🔗 Starting local blockchain node...
✅ Blockchain node started (localhost:8545)
✅ Smart contracts deployed successfully

🌐 Starting Flask application...
✅ Flask application started
🌐 Web interface: http://127.0.0.1:5000
🎯 SYSTEM READY!
```

---

## 🔧 Manual Deployment (Step-by-Step)

### Step 1: Prerequisites

**System Requirements:**
- Windows 10/11
- Python 3.8+
- Node.js 16+
- Git

**Check Prerequisites:**
```powershell
# Check Python
python --version

# Check Node.js
node --version

# Check npm
npm --version
```

### Step 2: Install Python Dependencies

```bash
cd D:\sih_project
pip install flask web3 python-dotenv
```

### Step 3: Install Blockchain Dependencies

```bash
cd D:\sih_project\blockchain
npm install
```

### Step 4: Compile Smart Contracts

```bash
cd D:\sih_project\blockchain
npm run compile
```

### Step 5: Start Blockchain Network

**Terminal 1 (Keep Running):**
```bash
cd D:\sih_project\blockchain
npx hardhat node
```

You should see:
```
Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545

Accounts
========
Account #0: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 (10000 ETH)
```

### Step 6: Deploy Smart Contracts

**Terminal 2:**
```bash
cd D:\sih_project\blockchain
npx hardhat run scripts/deploy.js --network localhost
```

Expected output:
```
Starting deployment of Blue Carbon MRV Smart Contracts...
✅ MRV Registry deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3
✅ Carbon Credit Token deployed to: 0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
🎉 Deployment completed successfully!
```

### Step 7: Start Flask Application

**Terminal 3:**
```bash
cd D:\sih_project
python app.py
```

Expected output:
```
🌊 BlueCarbon MRV System Starting Up
Flask Environment: development
Server: http://127.0.0.1:5000
🔗 Available API Endpoints:
   • /api/real_blockchain/status - Real blockchain status
   • /api/real_blockchain/demo - Carbon credit workflow demo
```

---

## 🌐 Access Points

### Web Interfaces

| Interface | URL | Purpose |
|-----------|-----|---------|
| **Main Dashboard** | http://127.0.0.1:5000 | Project overview |
| **Admin Portal** | http://127.0.0.1:5000/admin/login | System administration |
| **NGO Dashboard** | http://127.0.0.1:5000/ngo/dashboard | NGO project management |
| **Industry Portal** | http://127.0.0.1:5000/industry/login | Carbon credit purchasing |

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/real_blockchain/status` | GET | Blockchain connection status |
| `/api/real_blockchain/demo` | POST | Complete workflow demo |
| `/api/real_blockchain/credits/transfer` | POST | Transfer carbon credits |
| `/api/real_blockchain/projects/{id}/mint_credits` | POST | Mint carbon credits |

---

## 🧪 Testing the System

### 1. Check Blockchain Status

```bash
curl http://127.0.0.1:5000/api/real_blockchain/status
```

Expected response:
```json
{
  "success": true,
  "data": {
    "real_blockchain_available": true,
    "connected": true,
    "contract_addresses": {
      "mrv_registry": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
      "carbon_token": "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512"
    },
    "stats": {
      "connected": true,
      "network": "Hardhat Local",
      "chain_id": 31337,
      "block_number": 2
    }
  }
}
```

### 2. Run Complete Carbon Credit Workflow

```bash
curl -X POST http://127.0.0.1:5000/api/real_blockchain/demo \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "Test Mangrove Project",
    "location": "Sundarbans, West Bengal", 
    "carbon_amount": 250.5,
    "credits_amount": 200.0
  }'
```

Expected workflow:
```json
{
  "success": true,
  "data": {
    "workflow_steps": [
      {
        "step": 1,
        "action": "Create MRV Record",
        "success": true,
        "record_id": 1
      },
      {
        "step": 2, 
        "action": "Verify MRV Record",
        "success": true,
        "record_id": 1
      },
      {
        "step": 3,
        "action": "Mint Carbon Credits", 
        "success": true,
        "token_id": 1,
        "amount": 200.0
      }
    ],
    "blockchain_type": "Real Blockchain (Hardhat)"
  }
}
```

### 3. Test Credit Transfer

```bash
curl -X POST http://127.0.0.1:5000/api/real_blockchain/credits/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "token_id": "1",
    "from_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
    "to_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
    "amount": 50
  }'
```

---

## 📊 System Features

### ✅ Blockchain Features

- **Real Smart Contracts**: Deployed on local Hardhat network
- **MRV Registry**: On-chain verification of carbon measurements  
- **Carbon Credit Tokens**: ERC-1155 multi-token standard
- **Role-Based Access**: Admin, Verifier, Minter roles
- **Transfer System**: Credit transfers between addresses

### ✅ Web Application Features

- **Admin Dashboard**: Project approval and management
- **NGO Portal**: Project submission and tracking
- **Industry Interface**: Carbon credit marketplace
- **Real-time Monitoring**: Blockchain transaction tracking
- **API Integration**: RESTful APIs for all operations

### ✅ Integration Features

- **Web3 Connection**: Direct smart contract interaction
- **Automatic Fallback**: Simulation mode if blockchain unavailable
- **Transaction Monitoring**: Real-time blockchain event tracking
- **Error Handling**: Comprehensive error management

---

## 🔧 Configuration

### Environment Variables

Create/edit `.env` in project root:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Database
DATABASE_URL=sqlite:///bluecarbon.db

# Blockchain Configuration  
BLOCKCHAIN_NETWORK=localhost
BLOCKCHAIN_RPC_URL=http://127.0.0.1:8545

# Email (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Contract Addresses

The system automatically reads contract addresses from:
`blockchain/.env.contracts` (generated during deployment)

---

## 🐛 Troubleshooting

### Common Issues

**1. "Network connection refused"**
```bash
# Ensure Hardhat node is running
cd blockchain
npx hardhat node
```

**2. "Contracts not deployed"**  
```bash
cd blockchain
npx hardhat run scripts/deploy.js --network localhost
```

**3. "Web3 connection failed"**
- Check if blockchain node is running on port 8545
- Verify contract addresses in `blockchain/.env.contracts`

**4. "Flask import errors"**
```bash
pip install flask web3 python-dotenv
```

### Logs and Debugging

**Blockchain Logs:**
- Hardhat console output shows all transactions
- Contract events logged in real-time

**Flask Logs:**
- Check console output for API errors
- Enable debug mode: `FLASK_ENV=development`

---

## 🚀 Production Deployment

### For Production Use:

1. **Replace Hardhat** with real network (Polygon, Ethereum)
2. **Configure production database** (PostgreSQL recommended)
3. **Set up proper authentication** and authorization
4. **Enable HTTPS** and security headers
5. **Configure monitoring** and logging
6. **Set up backup systems** for database and contracts

### Network Migration:

```bash
# Deploy to Polygon Mumbai (testnet)
cd blockchain
npm run deploy:mumbai

# Deploy to Polygon Mainnet (production)
npm run deploy:polygon
```

---

## 📚 Additional Resources

- **Smart Contract Documentation**: `blockchain/contracts/`
- **API Documentation**: Check Flask routes in `app.py`
- **Frontend Templates**: `templates/` directory
- **Test Scripts**: `blockchain/test/` directory

## 🎯 Success Indicators

Your system is working correctly when you see:

- ✅ Blockchain node running on localhost:8545
- ✅ Smart contracts deployed with addresses
- ✅ Flask app running on localhost:5000
- ✅ `/api/real_blockchain/status` returns connected: true
- ✅ Demo workflow completes successfully
- ✅ Web interface loads admin/NGO/industry portals

**🎉 Congratulations! Your Blue Carbon MRV system with real blockchain integration is now running!**