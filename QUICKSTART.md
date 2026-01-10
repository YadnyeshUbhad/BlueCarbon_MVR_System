# 🚀 Quick Start Guide

## Get BlueCarbon MRV Running in 5 Minutes

---

## Prerequisites Checklist

Before you start, make sure you have:

- [ ] Python 3.8+ installed
- [ ] Node.js 14+ installed  
- [ ] Git installed
- [ ] Internet connection
- [ ] Text editor (VS Code recommended)

**Not sure?** Check these commands:
```bash
python --version      # Should show 3.8+
node --version        # Should show 14+
npm --version         # Should show 6+
git --version         # Should show 2.x+
```

---

## 5-Minute Setup

### ⏱️ Step 1: Clone Repository (1 min)

```bash
git clone https://github.com/your-username/bluecarbon-mrv.git
cd bluecarbon-mrv
```

### ⏱️ Step 2: Create Virtual Environment (1 min)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal.

### ⏱️ Step 3: Install Dependencies (2 min)

```bash
pip install -r requirements.txt
```

This installs Flask, Web3.py, Pandas, and other packages.

### ⏱️ Step 4: Create .env File (30 sec)

Create a file named `.env` in the project root with:

```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///bluecarbon.db
BLOCKCHAIN_MODE=sepolia
DEMO_MODE=True
```

### ⏱️ Step 5: Run the Application (30 sec)

```bash
python app.py
```

**Success!** You should see:
```
* Running on http://127.0.0.1:5000
* Press CTRL+C to quit
```

### 🎉 Step 6: Open in Browser

Visit: **http://localhost:5000**

You should see the BlueCarbon home page!

---

## What's Running?

Your local setup includes:

| Component | URL | Purpose |
|-----------|-----|---------|
| **Main Portal** | http://localhost:5000 | Home & registration |
| **Admin Panel** | http://localhost:5000/admin | Project verification |
| **NGO Dashboard** | http://localhost:5000/ngo | Project submission |
| **Industry Portal** | http://localhost:5000/industry | Carbon credits |
| **Public Dashboard** | http://localhost:5000 | Public metrics |

---

## Try These Next

### 1️⃣ Create a Test Project

```bash
# Visit NGO portal
http://localhost:5000/ngo

# Click "Submit Project"
# Fill in project details
# Submit form
```

### 2️⃣ Access Admin Panel

```bash
# Visit admin portal
http://localhost:5000/admin

# Login with test credentials
# Review submitted projects
# Click "Verify" to approve
```

### 3️⃣ Check Blockchain

```bash
# View token visualization
http://localhost:5000/blockchain/token-visualization

# See live blockchain stats
http://localhost:5000/blockchain/live-dashboard
```

### 4️⃣ Run Tests

```bash
# Test authentication
python test_authentication.py

# Test blockchain
python test_blockchain.py

# Test complete system
python test_complete_system.py
```

---

## Troubleshooting Quick Fixes

### Issue: Port 5000 Already in Use

```bash
# Change port
flask run --port 5001
```

### Issue: Python/pip Command Not Found

```bash
# Try python3 instead
python3 app.py
pip3 install -r requirements.txt
```

### Issue: Virtual Environment Won't Activate

```bash
# Try full path
# Windows
.\venv\Scripts\activate.bat

# macOS/Linux  
source ./venv/bin/activate
```

### Issue: Dependencies Won't Install

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Try installing without cache
pip install --no-cache-dir -r requirements.txt
```

### Issue: Import Errors

```bash
# Verify venv is activated (see (venv) in terminal)
# Reinstall dependencies
pip install -r requirements.txt
```

---

## Common Commands Reference

| Command | Purpose |
|---------|---------|
| `python app.py` | Start development server |
| `python test_*.py` | Run tests |
| `python -c "from db import init_db; init_db()"` | Initialize database |
| `flask run` | Alternative start method |
| `deactivate` | Exit virtual environment |
| `pip list` | List installed packages |
| `git status` | Check uncommitted changes |

---

## Project Structure Overview

```
bluecarbon-mrv/
├── app.py                 # Main application
├── requirements.txt       # Dependencies
├── .env                   # Environment variables (create this)
├── templates/             # HTML pages
│   ├── index.html         # Home page
│   ├── admin/            # Admin pages
│   ├── ngo/              # NGO pages
│   └── industry/         # Industry pages
├── static/               # CSS, JS, images
├── uploads/              # Uploaded files
├── blockchain/           # Smart contracts
├── tests/                # Test files
└── docs/                 # Documentation
```

---

## Next: Detailed Guides

### Want More Details?

- 📖 **[Installation Guide](INSTALLATION.md)** - Complete step-by-step setup
- ⚙️ **[Configuration Guide](CONFIG.md)** - Configure every component
- 🧪 **[Testing Guide](TESTING.md)** - Run and write tests
- 🚀 **[Deployment Guide](DEPLOYMENT.md)** - Deploy to cloud
- 📚 **[Main README](README.md)** - Full documentation

### Need Help?

- 🐛 **[Report Issues](https://github.com/your-repo/issues)**
- 💬 **[Ask Questions](https://github.com/your-repo/discussions)**
- 📧 **[Email Support](support@bluecarbon-mrv.org)**

---

## What's Included in Demo Mode?

Since `DEMO_MODE=True`, you get:

✅ **Mock Blockchain** - No real ETH needed  
✅ **Test Data** - Pre-populated projects  
✅ **All Features** - Full functionality  
✅ **No API Keys** - Works without external services  

**Perfect for learning and testing!**

---

## Enable Real Features (Optional)

### Use Real Blockchain (Sepolia Testnet)

```env
BLOCKCHAIN_MODE=sepolia
INFURA_PROJECT_ID=your-infura-key  # Get from https://infura.io
```

Then get free testnet ETH: https://www.sepoliafaucet.com

### Enable Email Notifications

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password  # Generate at https://myaccount.google.com/apppasswords
```

### Enable Firebase Authentication

Get Firebase config from: https://console.firebase.google.com

```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-email@iam.gserviceaccount.com
```

---

## Development Tips

### Hot Reload
Changes to Python files automatically reload in development mode.

### Debug Mode
Set `FLASK_DEBUG=True` in `.env` to get detailed error messages.

### Database Reset
```bash
# Delete old database
rm bluecarbon.db  # macOS/Linux
del bluecarbon.db # Windows

# Reinitialize
python -c "from db import init_db; init_db()"
```

### View Logs
```bash
# Check recent logs
tail -f logs/app.log  # macOS/Linux
Get-Content logs/app.log -Tail 20  # Windows
```

---

## Security Note for Developers

⚠️ **Never commit .env to Git!**

The `.env` file contains sensitive secrets. Make sure it's in `.gitignore`:

```bash
# Check .gitignore contains:
cat .gitignore | grep .env
```

---

## Ready to Deploy?

Once you're comfortable with development, check out:
- [Deployment Guide](DEPLOYMENT.md) - Deploy to Railway, Heroku, Google Cloud
- [Production Configuration](CONFIG.md#production-setup) - Secure production settings

---

## You're All Set! 🎉

You now have a working BlueCarbon MRV system running locally.

**Next steps:**
1. Explore the different dashboards
2. Read the [Main README](README.md) for features
3. Check [API Documentation](docs/) for endpoints
4. Deploy to production when ready

**Happy coding!** 💻🌊

---

**Having issues?** See [Troubleshooting](#troubleshooting-quick-fixes) above or create a [GitHub issue](https://github.com/your-repo/issues).
