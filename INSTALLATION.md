# 📦 Installation Guide

## Complete Step-by-Step Installation Instructions

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Clone Repository](#clone-repository)
3. [Python Setup](#python-setup)
4. [Dependencies Installation](#dependencies-installation)
5. [Environment Configuration](#environment-configuration)
6. [Database Setup](#database-setup)
7. [Blockchain Setup](#blockchain-setup)
8. [Verify Installation](#verify-installation)

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **Node.js**: 14.0 or higher
- **RAM**: 4GB
- **Storage**: 2GB free space
- **Internet**: Required for blockchain & API operations

### Recommended
- **Python**: 3.10+
- **RAM**: 8GB
- **Storage**: 5GB
- **GPU**: Optional, for ML predictions

### Check Your System

```bash
# Check Python version
python --version
# Expected: Python 3.8 or higher

# Check Node.js version
node --version
npm --version
# Expected: Node 14+, npm 6+

# Check Git
git --version
# Expected: Git 2.x+
```

---

## Clone Repository

### Using Git

```bash
# Clone the repository
git clone https://github.com/your-username/bluecarbon-mrv.git

# Navigate to project
cd bluecarbon-mrv

# Check project structure
ls -la
```

### Or Download as ZIP

1. Visit: `https://github.com/your-username/bluecarbon-mrv`
2. Click **Code** → **Download ZIP**
3. Extract the ZIP file
4. Open terminal in the extracted folder

---

## Python Setup

### Step 1: Create Virtual Environment

#### On Windows

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# You should see (venv) in your terminal
```

#### On macOS/Linux

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) in your terminal
```

### Step 2: Verify Virtual Environment

```bash
# Check Python path (should be in venv)
which python
# Windows: where python
# Should show path containing 'venv'

# Check pip location
pip --version
# Should mention the venv path
```

---

## Dependencies Installation

### Step 1: Upgrade pip

```bash
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Verify upgrade
pip --version
```

### Step 2: Install Python Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or with production dependencies
pip install -r requirements_production.txt

# Installation might take 2-5 minutes
```

### Step 3: Verify Installation

```bash
# Check Flask installation
python -c "import flask; print(flask.__version__)"
# Expected: 2.3.3

# Check other key packages
python -c "import numpy; print(numpy.__version__)"
python -c "import pandas; print(pandas.__version__)"

# List all installed packages
pip list
```

### Step 4: Install Node.js Dependencies (Blockchain)

```bash
# Navigate to blockchain folder
cd blockchain

# Install npm packages
npm install

# Verify installation
npm list

# Return to root
cd ..
```

---

## Environment Configuration

### Step 1: Create .env File

```bash
# In project root directory, create .env file
# Windows (PowerShell)
New-Item -Name ".env" -ItemType File

# macOS/Linux
touch .env
```

### Step 2: Add Configuration

Edit the `.env` file and add:

```env
# ========================================
# Flask Configuration
# ========================================
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-super-secret-key-change-this
HOST=127.0.0.1
PORT=5000

# ========================================
# Database Configuration
# ========================================
# SQLite (Development)
DATABASE_URL=sqlite:///bluecarbon.db

# PostgreSQL (Production)
# DATABASE_URL=postgresql://user:password@localhost:5432/bluecarbon

# ========================================
# Blockchain Configuration
# ========================================
BLOCKCHAIN_MODE=sepolia
BLOCKCHAIN_NETWORK=ethereum
INFURA_PROJECT_ID=your-infura-project-id
ALCHEMY_API_KEY=your-alchemy-api-key

# ========================================
# Firebase Configuration (Optional)
# ========================================
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY=your-firebase-private-key
FIREBASE_CLIENT_EMAIL=your-firebase-email@gmail.com
FIREBASE_DATABASE_URL=your-firebase-db-url

# ========================================
# Email Configuration (Optional)
# ========================================
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# ========================================
# External APIs (Optional)
# ========================================
SENTINEL_HUB_API_KEY=your-sentinel-key
GOOGLE_CLOUD_API_KEY=your-google-api-key

# ========================================
# Feature Flags
# ========================================
ENABLE_PUBLIC_DEMO=True
DEMO_MODE=True
PUBLIC_ACCESS=True
DEBUG_LOGGING=True
```

### Step 3: Get Required API Keys

#### Infura (Blockchain RPC)
1. Visit: `https://infura.io`
2. Sign up / Login
3. Create new project
4. Copy Project ID to `INFURA_PROJECT_ID`

#### Firebase (Optional - Authentication)
1. Visit: `https://console.firebase.google.com`
2. Create new project
3. Enable Authentication & Firestore
4. Download service account key
5. Copy credentials to `.env`

#### Alchemy (Alternative RPC)
1. Visit: `https://alchemy.com`
2. Create account
3. Create app
4. Copy API key to `ALCHEMY_API_KEY`

#### Gmail (Email Notifications)
1. Enable 2-factor authentication
2. Generate app password: `https://myaccount.google.com/apppasswords`
3. Use app password in `MAIL_PASSWORD`

---

## Database Setup

### SQLite (Development - No Setup Needed)

SQLite database is automatically created on first run. No additional setup required!

```bash
# Database file will be created as:
# bluecarbon.db
```

### PostgreSQL (Production)

#### Install PostgreSQL

**Windows**: Download from `https://www.postgresql.org/download/windows/`

**macOS**:
```bash
brew install postgresql
```

**Linux (Ubuntu)**:
```bash
sudo apt-get install postgresql postgresql-contrib
```

#### Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE bluecarbon;

# Create user
CREATE USER bluecarbon_user WITH PASSWORD 'your-secure-password';

# Grant privileges
ALTER ROLE bluecarbon_user SET client_encoding TO 'utf8';
ALTER ROLE bluecarbon_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE bluecarbon_user SET default_transaction_deferrable TO on;
ALTER ROLE bluecarbon_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE bluecarbon TO bluecarbon_user;

# Exit
\q
```

#### Update .env

```env
DATABASE_URL=postgresql://bluecarbon_user:your-secure-password@localhost:5432/bluecarbon
```

#### Initialize Database

```bash
python -c "from db import init_db; init_db()"
```

---

## Blockchain Setup

### Local Testing (Hardhat)

```bash
# Navigate to blockchain folder
cd blockchain

# Start local Hardhat node (in separate terminal)
npx hardhat node

# Output will show 20 test accounts with private keys
# Copy these for testing

# Back in main terminal, compile contracts
npx hardhat compile

# Deploy to local network
npx hardhat run scripts/deploy.js --network localhost

# Return to project root
cd ..
```

### Sepolia Testnet Setup

#### Step 1: Get Testnet ETH

```bash
# Visit Sepolia faucet (requires GitHub/Alchemy account)
https://www.sepoliafaucet.com

# Or use backup faucet
https://sepolifaucet.io

# Paste your wallet address and request funds
# You'll receive test ETH in ~1-2 minutes
```

#### Step 2: Update Environment

```env
BLOCKCHAIN_MODE=sepolia
INFURA_PROJECT_ID=your-infura-project-id
```

#### Step 3: Deploy Contracts

```bash
# Navigate to blockchain folder
cd blockchain

# Compile contracts
npx hardhat compile

# Deploy to Sepolia
npx hardhat run scripts/deploy.js --network sepolia

# Copy contract addresses from output to your config

# Return to root
cd ..
```

### Mumbai Testnet (Polygon)

```env
BLOCKCHAIN_MODE=mumbai
ALCHEMY_API_KEY=your-alchemy-api-key
```

Visit faucet: `https://faucet.polygon.technology/`

---

## Verify Installation

### Step 1: Test Python Environment

```bash
# Run Python interpreter
python

# In Python shell, test imports
import flask
import pandas
import numpy
import cv2
from PIL import Image
import web3

# All should import without errors
# Exit with:
exit()
```

### Step 2: Test Flask Application

```bash
# Start Flask app
python app.py

# Output should show:
# * Running on http://127.0.0.1:5000
# * Press CTRL+C to quit

# In browser, visit: http://localhost:5000
# You should see the home page

# Stop with: CTRL+C
```

### Step 3: Test Database

```bash
# Check if database file exists
ls -la bluecarbon.db
# Windows: dir bluecarbon.db

# Test database connection
python -c "from db import get_conn; print(get_conn())"
# Should return database connection without errors
```

### Step 4: Test Blockchain

```bash
# Test blockchain connectivity
python -c "from blockchain_sim import blockchain_mrv; print('Blockchain loaded')"

# If using real blockchain:
python -c "from web3 import Web3; print(Web3.is_address('0x' + '0'*40))"
```

### Step 5: Run Tests

```bash
# Run test suite
python -m pytest test_endpoints.py -v

# Or run specific test
python test_authentication.py

# Expected output: All tests PASSED
```

---

## Troubleshooting

### Issue: Python Command Not Found

```bash
# Windows: Use python3 or py
py --version

# macOS/Linux: Use python3
python3 --version
```

### Issue: Virtual Environment Not Activating

```bash
# Check venv location
dir venv  # Windows
ls -la venv  # macOS/Linux

# Try full path to activate
Windows:
.\venv\Scripts\activate.bat

macOS/Linux:
source ./venv/bin/activate
```

### Issue: pip install Fails

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Try installing with no cache
pip install --no-cache-dir -r requirements.txt

# Or install packages individually
pip install Flask==2.3.3
pip install web3
```

### Issue: Port 5000 Already in Use

```bash
# Windows: Kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux: Kill process
lsof -i :5000
kill -9 <PID>

# Or use different port
flask run --port 5001
```

### Issue: Database Lock Error

```bash
# Remove old database file
rm bluecarbon.db  # macOS/Linux
del bluecarbon.db  # Windows

# Reinitialize database
python -c "from db import init_db; init_db()"
```

---

## Next Steps

After successful installation:

1. ✅ Start the application: `python app.py`
2. ✅ Access at: `http://localhost:5000`
3. ✅ Read [Usage Guide](USAGE.md)
4. ✅ Check [API Documentation](API.md)
5. ✅ Review [Blockchain Guide](blockchain/README.md)

---

## Getting Help

- 📖 Check [README.md](README.md)
- 🔗 Review [Configuration Guide](CONFIG.md)
- 🐛 Report issues on [GitHub Issues](https://github.com/your-repo/issues)
- 💬 Ask questions on [GitHub Discussions](https://github.com/your-repo/discussions)

---

**Installation Complete!** 🎉

You're now ready to use the BlueCarbon MRV System. Happy coding!
