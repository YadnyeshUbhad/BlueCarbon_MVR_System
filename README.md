<div align="center">

# 🌊 BlueCarbon MRV System

**A Blockchain-Powered Monitoring, Reporting & Verification Platform for Blue Carbon Ecosystems**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com)
[![Blockchain](https://img.shields.io/badge/Blockchain-Web3.py-orange.svg)](https://ethereum.org)
[![PWA](https://img.shields.io/badge/PWA-Progressive%20Web%20App-purple.svg)](https://web.dev/progressive-web-apps)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Developed for Smart India Hackathon 2024 - Revolutionizing Blue Carbon Conservation Through Technology*

### 🚀 [Live Demo](http://localhost:5000) | 📚 [Documentation](docs/) | 🐛 [Report Bug](https://github.com/your-repo/issues)

</div>

---

## 📑 Table of Contents

- [🎯 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🏗️ System Architecture](#-system-architecture)
- [🛠️ Tech Stack](#️-tech-stack)
- [📋 Prerequisites](#-prerequisites)
- [🚀 Quick Start Guide](#-quick-start-guide)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Application](#running-the-application)
- [🔧 Configuration Guide](#-configuration-guide)
- [📊 API Endpoints](#-api-endpoints)
- [🔗 Blockchain Integration](#-blockchain-integration)
- [🗂️ Project Structure](#-project-structure)
- [🧪 Testing](#-testing)
- [📱 Progressive Web App](#-progressive-web-app)
- [🚀 Deployment](#-deployment)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [📞 Support](#-support)

---

## 🎯 Overview

The BlueCarbon MRV System is a comprehensive blockchain-powered platform that enables **transparent monitoring, reporting, and verification** of blue carbon ecosystem restoration projects. Our system tokenizes carbon credits, provides real-time analytics, and creates an immutable audit trail for environmental conservation efforts.

### 🌊 What is Blue Carbon?

Blue carbon refers to carbon captured by the world's ocean and coastal ecosystems, particularly:
- 🌿 **Mangrove Forests** - Capture up to 10x faster than terrestrial forests
- 🌾 **Seagrass Meadows** - Rich biodiversity and carbon storage
- 🏞️ **Salt Marshes** - Coastal protection and carbon sequestration

### 🎯 Project Objectives

| Objective | Solution |
|-----------|----------|
| **Transparency** | Immutable blockchain records for all transactions |
| **Efficiency** | Automated verification and tokenization processes |
| **Accessibility** | Multi-stakeholder portal for NGOs, admins, and industry |
| **Innovation** | AI-powered predictions and satellite monitoring |
| **Scalability** | PWA technology for offline field work |

---

## ✨ Key Features

### 🔗 **Blockchain Integration**
- ✅ **Immutable Project Records** - Cryptographic hashing ensures data integrity
- ✅ **Smart Contract Tokens** - Automated carbon credit tokenization (ERC-20 compatible)
- ✅ **Transparent Transactions** - Complete audit trail with full transaction history
- ✅ **Multi-Chain Support** - Ethereum, Polygon (Mumbai), Sepolia testnet
- ✅ **Decentralized Verification** - Multi-stakeholder validation system

### 📱 **Multi-Stakeholder Portal**

| Role | Features |
|------|----------|
| **NGO Portal** 🟦 | Project submission, monitoring, impact tracking |
| **Admin Portal** 🟨 | Project verification, user management, oversight |
| **Industry Portal** 🟥 | Carbon credit marketplace, trading, portfolio |
| **Public Dashboard** 🟩 | Real-time environmental metrics, statistics |

### 🤖 **Advanced Analytics & AI**
- 🧠 **AI Predictions** - 20-year carbon sequestration forecasting using ML models
- 🛰️ **Satellite Monitoring** - Real-time remote sensing data integration
- 🚁 **Drone Processing** - Aerial imagery analysis and 3D mapping
- 🗺️ **GIS Analysis** - Geospatial site assessment and carbon calculations
- 📊 **Data Visualization** - Interactive dashboards with real-time metrics

### 📱 **Progressive Web App (PWA)**
- 📶 **Offline Functionality** - Field data collection without internet
- 🔄 **Background Sync** - Automatic data synchronization when online
- 🔔 **Push Notifications** - Real-time project updates and alerts
- 📱 **Mobile Optimized** - Touch-friendly interface for field workers
- 💾 **Local Storage** - Data persistence on user devices

### 🔐 **Security & Authentication**
- 🔑 **JWT Authentication** - Secure token-based authentication
- 👤 **Role-Based Access Control** - Fine-grained permission system
- 🔒 **Password Security** - bcrypt hashing with salts
- 📧 **Email Verification** - Two-factor authentication support
- 🛡️ **CSRF Protection** - Cross-site request forgery prevention

---

## 🏗️ System Architecture

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                          │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │   NGO Portal │ Admin Portal │Industry Portal│Public Dashboard│ │
│  │  Dashboard   │  Dashboard   │   Dashboard   │     PWA       │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   FLASK WEB SERVER                               │
│  ┌──────────────┬──────────────┬──────────────────────────────┐  │
│  │API Gateway   │Authentication│  Session Management           │  │
│  └──────────────┴──────────────┴──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 BUSINESS LOGIC LAYER                             │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │ Project Mgmt │ Blockchain   │Token Management  │Verification  │ │
│  │              │ Service      │                  │Engine        │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                DATA PROCESSING LAYER                             │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │ Satellite    │ Drone Image  │ ML Prediction│ GIS Analysis │  │
│  │ Data         │ Analyzer     │ Engine       │ & Carbon     │  │
│  │ Processor    │              │              │ Calculation  │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  BLOCKCHAIN LAYER                                │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │Smart Contract│ Transaction  │Token Lifecycle  │Audit Trail │  │
│  │Interface     │ Manager      │                 │& Hash Gen   │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DATA STORAGE LAYER                            │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │  Project DB  │   User DB    │Transaction   │ File Storage │  │
│  │              │              │ Ledger       │              │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
NGO User              Admin User           Industry User
   │                     │                     │
   ├─ Submit Project     │                     │
   │   ├─> Flask API ────┼─ Verify Project    │
   │   │                 │   ├─> Blockchain   │
   │   │                 │   │   ├─ Mint Tokens─> Marketplace
   │   │                 │   │   └─ Record TX   └─ Purchase
   │   │                 │   └─> DB             └─ Transfer
   │   │                 │
   │   └─ Upload Files ──┼─ Document AI
   │                     │
   └─ Track Status ──────┼─ Real-time Updates
                         │
                    Generate Audit Trail
                    Store on Blockchain
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose | Version |
|-----------|---------|---------|
| **Python** | Core programming language | 3.8+ |
| **Flask** | Web framework | 2.3.3 |
| **Web3.py** | Blockchain interaction | Latest |
| **SQLite/PostgreSQL** | Database | Latest |
| **Pandas** | Data analysis | 1.5.3 |
| **OpenCV** | Image processing | 4.8.0 |
| **Pillow** | Image handling | 9.5.0 |

### Frontend
| Technology | Purpose |
|-----------|---------|
| **HTML5** | Markup and structure |
| **CSS3** | Styling with Glassmorphism effects |
| **JavaScript** | Client-side interactivity |
| **Service Worker** | PWA offline functionality |
| **Jinja2** | Template engine |

### Blockchain
| Technology | Purpose |
|-----------|---------|
| **Solidity** | Smart contracts |
| **Hardhat** | Development framework |
| **Ethereum/Polygon** | Blockchain networks |
| **MetaMask** | Wallet integration |

### External APIs & Services
| Service | Purpose |
|---------|---------|
| **Firebase** | Authentication & real-time database |
| **Sentinel Hub** | Satellite imagery |
| **Google Cloud AI** | Document verification |
| **Geospatial APIs** | Location services |

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software
- **Python 3.8 or higher** - [Download](https://www.python.org/downloads/)
- **Node.js 14+ & npm** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)
- **Git Bash / Terminal** - For running commands

### Optional but Recommended
- **Docker** - For containerized deployment
- **MetaMask** - For blockchain interaction (Chrome/Firefox extension)
- **Postman** - For API testing
- **VS Code** - Code editor

### System Requirements
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: At least 2GB free space
- **OS**: Windows, macOS, or Linux

---

## 🚀 Quick Start Guide

### Installation

#### 1️⃣ Clone the Repository

```bash
# Clone the project
git clone https://github.com/your-username/bluecarbon-mrv.git

# Navigate to project directory
cd bluecarbon-mrv
```

#### 2️⃣ Create Virtual Environment (Python)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

#### 3️⃣ Install Python Dependencies

```bash
# Install all Python packages
pip install -r requirements.txt

# Or for production dependencies
pip install -r requirements_production.txt
```

#### 4️⃣ Install Node.js Dependencies (for Blockchain)

```bash
# Navigate to blockchain directory
cd blockchain

# Install dependencies
npm install

# Return to project root
cd ..
```

#### 5️⃣ Setup Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///bluecarbon.db

# Blockchain Configuration
BLOCKCHAIN_MODE=sepolia
INFURA_PROJECT_ID=your-infura-id
ALCHEMY_API_KEY=your-alchemy-key

# Firebase Configuration (Optional)
FIREBASE_PROJECT_ID=your-firebase-id
FIREBASE_PRIVATE_KEY=your-firebase-private-key
FIREBASE_CLIENT_EMAIL=your-firebase-email

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# External APIs (Optional)
SENTINEL_HUB_API_KEY=your-sentinel-key
GOOGLE_CLOUD_API_KEY=your-google-key

# Feature Flags
ENABLE_PUBLIC_DEMO=True
DEMO_MODE=True
PUBLIC_ACCESS=True
```

### Configuration

#### Database Setup

```bash
# Initialize the database
python -c "from db import init_db; init_db()"
```

#### Blockchain Setup (Optional - for Smart Contract Deployment)

```bash
# Navigate to blockchain directory
cd blockchain

# Compile smart contracts
npx hardhat compile

# Deploy to testnet (requires accounts configured)
npx hardhat run scripts/deploy.js --network sepolia

# Return to project root
cd ..
```

### Running the Application

#### Development Mode

```bash
# Method 1: Direct Python execution
python app.py

# Method 2: Using Flask CLI
set FLASK_APP=app.py  # On Windows
export FLASK_APP=app.py  # On macOS/Linux
flask run

# Method 3: Using startup script
python start.py
```

#### Access the Application

```
Main Portal:        http://localhost:5000
NGO Dashboard:      http://localhost:5000/ngo
Admin Dashboard:    http://localhost:5000/admin
Industry Portal:    http://localhost:5000/industry
Public Dashboard:   http://localhost:5000/
```

#### Production Mode

```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using the production startup script
python start_production.py
```

---

## 🔧 Configuration Guide

### Application Configuration Files

#### `config.py` - Base Configuration
```python
- DEBUG: Enable/disable debug mode
- SECRET_KEY: Session encryption key
- DATABASE_URL: Database connection string
- PORT: Server port (default: 5000)
- HOST: Server host (default: localhost)
```

#### `production_config.py` - Production Settings
```python
- is_production(): Check production mode
- get_database_connection(): Get DB connection
- record_metric(): Log performance metrics
- get_integration_config(): External service configs
```

### Database Configuration

#### SQLite (Development - Default)
```
DATABASE_URL=sqlite:///bluecarbon.db
```

#### PostgreSQL (Production)
```
DATABASE_URL=postgresql://user:password@localhost:5432/bluecarbon
```

### Blockchain Configuration

#### Supported Networks

| Network | RPC URL | Chain ID |
|---------|---------|----------|
| **Sepolia (Testnet)** | https://sepolia.infura.io/v3/{ID} | 11155111 |
| **Polygon Mumbai** | https://rpc.ankr.com/polygon_mumbai | 80001 |
| **Ethereum Mainnet** | https://mainnet.infura.io/v3/{ID} | 1 |
| **Localhost Hardhat** | http://127.0.0.1:8545 | 31337 |

#### Get Testnet Funds

```bash
# Sepolia Faucet
https://www.sepoliafaucet.com

# Mumbai Faucet
https://faucet.polygon.technology/

# Ethereum Goerli (if using)
https://goerlifaucet.com
```

---

## 📊 API Endpoints

### Authentication Endpoints

```
POST   /api/auth/register       - Register new user
POST   /api/auth/login          - User login
POST   /api/auth/logout         - User logout
GET    /api/auth/verify         - Verify email
POST   /api/auth/refresh        - Refresh JWT token
GET    /api/auth/user           - Get current user info
```

### Project Management Endpoints

```
GET    /api/projects            - Get all projects
POST   /api/projects            - Create new project
GET    /api/projects/<id>       - Get project details
PUT    /api/projects/<id>       - Update project
DELETE /api/projects/<id>       - Delete project
GET    /api/projects/search     - Search projects
```

### Blockchain Endpoints

```
POST   /api/blockchain/verify   - Verify project on blockchain
GET    /api/blockchain/status   - Get transaction status
POST   /api/blockchain/mint     - Mint carbon credits
GET    /api/blockchain/tokens   - Get token info
GET    /api/blockchain/history  - Get transaction history
```

### Analytics Endpoints

```
GET    /api/analytics/carbon    - Get carbon metrics
GET    /api/analytics/satellite - Get satellite data
POST   /api/analytics/predict   - Get ML predictions
GET    /api/analytics/gis       - Get GIS analysis
GET    /api/analytics/dashboard - Get dashboard data
```

### Admin Endpoints

```
GET    /api/admin/users         - List all users
GET    /api/admin/projects      - List all projects
PUT    /api/admin/approve/<id>  - Approve project
DELETE /api/admin/user/<id>     - Delete user
GET    /api/admin/stats         - Get system statistics
```

### Web Routes (UI)

```
GET    /                        - Home page
GET    /admin                   - Admin portal
GET    /industry                - Industry portal
GET    /ngo                     - NGO dashboard
GET    /public                  - Public dashboard
```

---

## 🔗 Blockchain Integration

### Smart Contracts

#### CarbonCreditToken.sol
ERC-20 token for carbon credits with custom functionality:

```solidity
// Token details
name: "Blue Carbon Credits"
symbol: "BCC"
decimals: 18

// Functions
- mint(address to, uint256 amount): Mint new tokens
- burn(uint256 amount): Burn tokens
- transfer(address to, uint256 amount): Transfer tokens
- approve(address spender, uint256 amount): Approve spending
- transferFrom(address from, address to, uint256 amount): Transfer on behalf
```

#### MRVRegistry.sol
Project registration and verification smart contract:

```solidity
// Project Structure
- name: Project name
- location: Geographic coordinates
- carbonCredits: Number of credits
- verified: Verification status
- timestamp: Registration time
- owner: Project owner address

// Functions
- registerProject(): Register new project
- verifyProject(): Admin verification
- mintTokens(): Create carbon credits
- recordTransaction(): Log blockchain transaction
- getProjectHistory(): Retrieve audit trail
```

### Transaction Flow

```
1. NGO Creates Project
   └─> Submit project details to system

2. System Processes Data
   └─> Validate, calculate carbon metrics

3. Smart Contract Receives Data
   └─> Project registered on blockchain

4. Transaction Mined
   └─> Data immutably stored

5. Tokens Minted
   └─> Carbon credits created

6. Immutable Audit Trail
   └─> Full transaction history recorded
```

---

## 🗂️ Project Structure

```
bluecarbon-mrv/
│
├── 📄 Core Application Files
│   ├── app.py                              # Main Flask application
│   ├── config.py                           # Configuration settings
│   ├── db.py                               # Database utilities
│   ├── auth.py                             # Authentication logic
│   ├── wsgi.py                             # WSGI application
│   └── production_config.py                # Production configuration
│
├── 📁 blockchain/                          # Smart contracts & blockchain
│   ├── contracts/
│   │   ├── CarbonCreditToken.sol           # ERC-20 token
│   │   └── MRVRegistry.sol                 # Project registry
│   ├── scripts/
│   ├── test/
│   ├── ignition/
│   ├── hardhat.config.js
│   └── package.json
│
├── 📁 templates/                           # HTML Templates
│   ├── base.html                           # Base template
│   ├── index.html                          # Home page
│   ├── register.html                       # Registration
│   ├── admin/
│   │   ├── dashboard.html
│   │   └── ...
│   ├── ngo/
│   │   ├── dashboard.html
│   │   └── ...
│   └── industry/
│       ├── dashboard.html
│       └── ...
│
├── 📁 static/                              # Static Files
│   ├── css/
│   │   ├── style.css                       # Main styles
│   │   └── ...
│   ├── js/
│   │   ├── main.js
│   │   └── ...
│   ├── manifest.json                       # PWA manifest
│   └── sw.js                               # Service Worker
│
├── 📁 uploads/                             # User Uploads
│   └── projects/
│
├── 🔧 Blockchain Modules
│   ├── blockchain_sim.py                   # Simulation engine
│   ├── blockchain_routes.py                # API routes
│   ├── real_blockchain_routes.py           # Production blockchain
│   ├── blockchain_audit_system.py          # Audit trail
│   └── web3_integration.py                 # Web3 integration
│
├── 📊 Analytics & Data Processing
│   ├── ml_predictions.py                   # ML predictions
│   ├── satellite_integration.py            # Satellite data
│   ├── drone_processing.py                 # Drone imagery
│   ├── geospatial_analysis.py              # GIS analysis
│   ├── carbon_impact_calculator.py         # Carbon calculations
│   └── real_satellite_apis.py              # Satellite APIs
│
├── 🔐 Security & Integration
│   ├── firebase_client.py                  # Firebase auth
│   ├── email_notifications.py              # Email system
│   ├── notification_system.py              # Notifications
│   ├── approval_workflow_system.py         # Workflow
│   ├── mrv_workflow_system.py              # MRV workflow
│   ├── trust_score_system.py               # Trust scoring
│   └── verifiable_credentials.py           # VC system
│
├── 📁 docs/                                # Documentation
│   ├── architecture-diagram.md
│   ├── visual-overview.md
│   └── ...
│
├── 🧪 Tests
│   ├── test_app_blockchain.py
│   ├── test_authentication.py
│   ├── test_endpoints.py
│   ├── test_complete_system.py
│   └── test_carbon_calculation.py
│
├── ⚙️ Configuration & Deployment
│   ├── requirements.txt
│   ├── requirements_production.txt
│   ├── .env.example
│   ├── .gitignore
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── Procfile
│   ├── railway.json
│   └── start_production.py
│
└── 📚 Additional Documentation
    ├── README.md                           # Main README
    ├── CARBON_CALCULATION_METHODOLOGY.md
    ├── CARBON_CALCULATION_EXAMPLE.md
    └── sample_tree_data.csv
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest test_endpoints.py -v

# Run with coverage report
python -m pytest --cov=. --cov-report=html

# Run blockchain tests
python test_blockchain.py

# Run authentication tests
python test_authentication.py

# Run complete system tests
python test_complete_system.py

# Run carbon calculation tests
python test_carbon_calculation.py
```

### Test Files Available

| Test File | Coverage |
|-----------|----------|
| `test_endpoints.py` | API endpoint testing |
| `test_authentication.py` | Authentication & login flows |
| `test_blockchain.py` | Blockchain integration |
| `test_carbon_calculation.py` | Carbon metrics calculation |
| `test_complete_system.py` | End-to-end flows |
| `test_complete_system.py` | Full system integration |

### Expected Test Results

```
✅ Blockchain initialization: PASSED
✅ Project submission: PASSED
✅ Authentication: PASSED
✅ Token minting: PASSED
✅ Carbon calculations: PASSED
✅ Database operations: PASSED
✅ API endpoints: PASSED
```

---

## 📱 Progressive Web App (PWA)

### Installation on Mobile

1. **Open in Browser**: Launch the app in Chrome/Firefox on mobile
2. **Install Prompt**: Tap "Install" when prompted
3. **Home Screen**: App appears as native icon

### PWA Features Enabled

#### Service Worker (`static/sw.js`)
- ✅ Offline functionality
- ✅ Cache-first caching strategy
- ✅ Background synchronization
- ✅ Push notifications

#### Web App Manifest (`static/manifest.json`)
```json
{
  "name": "BlueCarbon MRV System",
  "short_name": "BlueCarbon",
  "icons": [
    {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"}
  ],
  "theme_color": "#001f3f",
  "background_color": "#ffffff",
  "display": "standalone",
  "scope": "/",
  "start_url": "/"
}
```

### Offline Capabilities

- ✅ View cached projects offline
- ✅ Create draft projects (synced when online)
- ✅ Access offline data storage
- ✅ Automatic background sync
- ✅ Push notification support

---

## 🚀 Deployment

### Local Development

```bash
# Method 1: Direct run
python app.py

# Method 2: Flask development server
flask run --debug

# Method 3: Start script
python start.py
```

### Docker Deployment

#### Build Docker Image

```bash
# Build the image
docker build -t bluecarbon-mrv:latest .

# Run container
docker run -p 5000:5000 \
  -e DATABASE_URL="sqlite:///bluecarbon.db" \
  -e SECRET_KEY="your-secret" \
  -e FLASK_ENV="production" \
  bluecarbon-mrv:latest
```

#### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Cloud Deployment Options

#### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up

# View logs
railway logs
```

#### Heroku

```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login

# Create app
heroku create your-app-name

# Set environment
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

#### Google Cloud

```bash
# Install Google Cloud CLI
# https://cloud.google.com/sdk/docs/install

# Initialize
gcloud init
gcloud app create

# Deploy
gcloud app deploy

# View logs
gcloud app logs read -f
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### 1️⃣ Fork the Repository

```bash
git clone https://github.com/your-username/bluecarbon-mrv.git
cd bluecarbon-mrv
```

### 2️⃣ Create Feature Branch

```bash
git checkout -b feature/your-amazing-feature
```

### 3️⃣ Make Changes

- Follow PEP 8 style guide
- Add meaningful comments
- Update documentation
- Add tests for new features

### 4️⃣ Commit & Push

```bash
git add .
git commit -m "Add amazing feature"
git push origin feature/your-amazing-feature
```

### 5️⃣ Open Pull Request

- Provide clear description
- Link related issues
- Request code review

### Code Standards

```python
# PEP 8 Compliant
# Use meaningful names
# Add docstrings

def calculate_carbon_sequestration(area: float, duration: int) -> float:
    """
    Calculate carbon sequestration amount.
    
    Args:
        area: Area in hectares
        duration: Duration in years
        
    Returns:
        Carbon sequestration in tonnes CO2
    """
    # Implementation
    pass
```

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2024 BlueCarbon Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

---

## 📞 Support

### Need Help?

- 📖 **Documentation**: Check [docs/](docs/) folder
- 🐛 **Report Bugs**: [GitHub Issues](https://github.com/your-repo/issues)
- 💬 **Ask Questions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- 📧 **Email**: support@bluecarbon-mrv.org

### Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Web3.py Docs](https://web3py.readthedocs.io/)
- [Solidity Docs](https://docs.soliditylang.org/)
- [Firebase Docs](https://firebase.google.com/docs)

### Community

- [Twitter](https://twitter.com/bluecarbonmrv)
- [Discord](https://discord.gg/bluecarbon)
- [GitHub Discussions](https://github.com/your-repo/discussions)

---

## 🏆 Acknowledgments

### Smart India Hackathon 2024
Developed as part of the Smart India Hackathon 2024 initiative for environmental sustainability and blockchain innovation.

### Technologies & Contributors
- Flask & Python ecosystem
- Ethereum blockchain network
- Geospatial & satellite APIs
- Open-source community

---

<div align="center">

### 🌍 Making Blue Carbon Monitoring Transparent & Accessible

**Built with ❤️ for Environmental Conservation**

⭐ If you find this project useful, please give it a star!

[⬆ Back to Top](#-bluecarbon-mrv-system)

</div>
