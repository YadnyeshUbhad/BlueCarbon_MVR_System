# Blue Carbon MRV System - Complete Setup & Run Guide

## 🚀 Quick Start (3 Steps)

### 1. Start Blockchain (Optional - for real blockchain features)
```bash
# Terminal 1: Start Hardhat local blockchain
npx hardhat node

# Terminal 2: Deploy contracts (if blockchain is running)
npx hardhat run scripts/deploy.js --network localhost
```

### 2. Start Flask Application
```bash
# Make sure environment is set up
python app.py
```

### 3. Access the System
- **Public Landing Page**: http://localhost:5000
- **Admin Portal**: http://localhost:5000/admin/login
- **NGO Dashboard**: http://localhost:5000/ngo/dashboard
- **Industry Portal**: http://localhost:5000/industry/login

---

## 🏗️ Complete System Architecture

### **Public Landing Page** (`/`)
- Welcome page for visitors
- Live blockchain stats
- Interactive demo workflow
- Links to all portals and APIs

### **Role-Based Access**
1. **Admin Portal** - System management and project approval
2. **NGO Dashboard** - Project submission and carbon credit management  
3. **Industry Portal** - Carbon credit marketplace and purchasing

### **Blockchain Integration**
- **Real Blockchain**: Uses deployed Hardhat contracts (if running)
- **Simulation Mode**: Falls back to simulation for testing
- **API Endpoints**: RESTful APIs for external integration

---

## 📋 System Features

### **MRV (Measurement, Reporting, Verification)**
- On-chain project registration
- Satellite monitoring integration
- AI-powered verification
- Transparent audit trail

### **Carbon Credit Management**
- ERC-1155 token standard
- Minting, transfer, and retirement
- Marketplace functionality
- Automated pricing and transactions

### **Advanced Features**
- Multi-stakeholder authentication
- Real-time satellite data
- ML-based project verification
- Geospatial analysis
- Token visualization
- Email notifications
- Production monitoring

---

## 🔧 Environment Setup

### **Required Environment Variables** (`.env`)
```bash
# Database
DATABASE_URL=sqlite:///blue_carbon_mrv.db

# Blockchain
HARDHAT_NETWORK_URL=http://localhost:8545
PRIVATE_KEY=ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

# External APIs
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
FIREBASE_CONFIG={"apiKey":"your_key"}

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email
EMAIL_PASS=your_password

# Security
SECRET_KEY=your-very-secure-secret-key-here
```

### **Contract Addresses** (`.env.contracts` - auto-generated)
```bash
MRV_REGISTRY_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
CARBON_CREDIT_TOKEN_ADDRESS=0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
```

---

## 🎯 Demo Workflow

### **Public Demo** (via Landing Page)
1. Visit http://localhost:5000
2. Scroll to "Live Demo" section
3. Fill in project details
4. Click "Run Complete Workflow"
5. Watch the 3-step process:
   - Create MRV Record
   - Verify Record  
   - Mint Carbon Credits

### **API Demo** (Programmatic)
```bash
# Check blockchain status
curl http://localhost:5000/api/real_blockchain/status

# Run demo workflow
curl -X POST http://localhost:5000/api/real_blockchain/demo \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "Demo Mangrove Restoration",
    "location": "Sundarbans, West Bengal", 
    "carbon_amount": 250.5,
    "credits_amount": 200
  }'
```

---

## 🔐 Test Accounts

### **Admin Login**
- Email: `admin@nccr.gov.in`
- Password: `admin123`

### **NGO Login** 
- Email: `ngo@example.org`
- Password: `ngo123`

### **Industry Login**
- Email: `industry@company.com`
- Password: `industry123`

---

## 📊 API Endpoints

### **Blockchain APIs** (`/api/real_blockchain/`)
- `GET /status` - Blockchain connection status
- `POST /demo` - Run complete demo workflow
- `POST /projects/{id}/create_mrv` - Create MRV record
- `POST /mrv/{id}/verify` - Verify MRV record  
- `POST /projects/{id}/mint_credits` - Mint carbon credits
- `POST /credits/transfer` - Transfer credits
- `GET /credits/balance` - Check credit balance

### **Simulation APIs** (`/api/blockchain/`)
- Identical endpoints using blockchain simulation
- Faster for testing and development

### **System APIs**
- `GET /_routes` - List all available routes
- `GET /admin/api/*` - Admin management APIs
- `POST /register` - Role-based user registration
- `POST /login` - Unified authentication

---

## 🐛 Troubleshooting

### **Common Issues**

1. **Blockchain Connection Failed**
   - System automatically falls back to simulation mode
   - Check if Hardhat node is running: `npx hardhat node`

2. **Template Not Found**
   - Templates are in `templates/` directory
   - Check file paths in routes

3. **Database Issues** 
   - SQLite database auto-created on first run
   - Delete `blue_carbon_mrv.db` to reset

4. **Port Already in Use**
   - Change Flask port: `app.run(port=5001)`
   - Or kill existing process

### **Development Mode**
- Templates auto-reload enabled
- Detailed error logging
- Debug mode active

### **Production Deployment**
- Set `ENVIRONMENT=production` in `.env`
- Use proper database (PostgreSQL)
- Configure external APIs
- Set secure secret keys

---

## 🚀 Next Steps

1. **Try the Demo**: Start with the public landing page demo
2. **Explore Dashboards**: Login with test accounts to explore features  
3. **Use APIs**: Integrate with external systems via REST APIs
4. **Deploy to Production**: Follow production configuration guide
5. **Customize**: Modify templates and add new features

## 📞 Support

- Check the logs for detailed error information
- All routes available at: http://localhost:5000/_routes
- System status: http://localhost:5000/api/real_blockchain/status

---

**Happy Carbon Credit Management! 🌱**