<div align="center">

# 🌊 BlueCarbon MRV System

**A Blockchain-Powered Monitoring, Reporting & Verification Platform for Blue Carbon Ecosystems**

*Developed for Smart India Hackathon 2024 - Revolutionizing Blue Carbon Conservation Through Technology*

### 🚀 [Live Demo](http://localhost:5000) 
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


<div align="center">

### 🌍 Making Blue Carbon Monitoring Transparent & Accessible

**Built with ❤️ for Environmental Conservation**

⭐ If you find this project useful, please give it a star!

[⬆ Back to Top](#-bluecarbon-mrv-system)

</div>
