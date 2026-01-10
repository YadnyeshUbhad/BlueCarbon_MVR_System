# ⚙️ Configuration Guide

## Complete Configuration Reference

---

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [Flask Configuration](#flask-configuration)
3. [Database Configuration](#database-configuration)
4. [Blockchain Configuration](#blockchain-configuration)
5. [Firebase Configuration](#firebase-configuration)
6. [Email Configuration](#email-configuration)
7. [External APIs](#external-apis)
8. [Feature Flags](#feature-flags)
9. [Security Settings](#security-settings)
10. [Troubleshooting](#troubleshooting)

---

## Environment Variables

### What is .env?

The `.env` file stores sensitive configuration without committing to version control.

### Location
```
bluecarbon-mrv/
└── .env  ← Create here
```

### Create .env File

```bash
# Create empty file
touch .env  # macOS/Linux
New-Item -Name ".env" -ItemType File  # Windows PowerShell
```

### Never Commit .env!

Add to `.gitignore`:
```
.env
.env.local
.env.*.local
*.key
*.pem
```

---

## Flask Configuration

### Basic Settings

```env
# Flask Environment
FLASK_ENV=development  # development or production
FLASK_DEBUG=True       # Enable debug mode (development only!)
SECRET_KEY=your-super-secret-key-here

# Server Configuration
HOST=127.0.0.1  # localhost
PORT=5000       # Server port
THREADS=4       # Number of worker threads
```

### Available Environments

| Environment | DEBUG | Purpose |
|-------------|-------|---------|
| **development** | True | Local development, auto-reload |
| **testing** | True | Running tests |
| **production** | False | Public deployment |

### Example Configurations

**Development:**
```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-key-not-secret
```

**Production:**
```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=very-long-secure-random-key-min-32-chars
```

---

## Database Configuration

### SQLite (Development)

```env
DATABASE_URL=sqlite:///bluecarbon.db
```

**Pros:**
- ✅ No setup required
- ✅ Perfect for development
- ✅ Single file storage

**Cons:**
- ❌ Not suitable for production
- ❌ Limited concurrent users
- ❌ No advanced features

**File Location:**
```
bluecarbon-mrv/
└── bluecarbon.db  ← Auto-created
```

### PostgreSQL (Production)

```env
DATABASE_URL=postgresql://user:password@host:5432/database
```

**Example:**
```env
DATABASE_URL=postgresql://bluecarbon_user:MySecurePass123@localhost:5432/bluecarbon
```

**Connection String Format:**
```
postgresql://[username]:[password]@[host]:[port]/[database]
```

**Pros:**
- ✅ Production-ready
- ✅ Advanced features
- ✅ Scalable
- ✅ ACID compliance

**Setup PostgreSQL:**

```bash
# Create database
createdb bluecarbon

# Create user
createuser -P bluecarbon_user
# Enter password when prompted

# Grant privileges
psql -d bluecarbon -c "GRANT ALL PRIVILEGES ON DATABASE bluecarbon TO bluecarbon_user;"
```

### MySQL/MariaDB (Alternative)

```env
DATABASE_URL=mysql+pymysql://user:password@host:3306/database
```

### Connection Pooling (Production)

```env
SQLALCHEMY_POOL_SIZE=10
SQLALCHEMY_POOL_RECYCLE=3600
SQLALCHEMY_POOL_PRE_PING=True
```

### Database Initialization

```bash
# Initialize database tables
python -c "from db import init_db; init_db()"

# Verify connection
python -c "from db import get_conn; print(get_conn())"
```

---

## Blockchain Configuration

### Network Selection

```env
# Choose one of: sepolia, mumbai, mainnet, localhost
BLOCKCHAIN_MODE=sepolia
```

### Available Networks

| Network | Mode | RPC URL | Chain ID | Status |
|---------|------|---------|----------|--------|
| **Sepolia** | sepolia | `https://sepolia.infura.io/v3/{ID}` | 11155111 | Testnet |
| **Polygon Mumbai** | mumbai | `https://rpc.ankr.com/polygon_mumbai` | 80001 | Testnet |
| **Ethereum** | mainnet | `https://mainnet.infura.io/v3/{ID}` | 1 | Mainnet |
| **Localhost** | localhost | `http://127.0.0.1:8545` | 31337 | Local |

### RPC Provider Configuration

#### Infura Setup

```env
INFURA_PROJECT_ID=your-project-id-here

# URLs will be constructed as:
# Mainnet: https://mainnet.infura.io/v3/{INFURA_PROJECT_ID}
# Sepolia: https://sepolia.infura.io/v3/{INFURA_PROJECT_ID}
```

**Get Infura API Key:**
1. Visit `https://infura.io`
2. Sign up / Login
3. Create new project
4. Copy Project ID
5. Add to .env

#### Alchemy Setup

```env
ALCHEMY_API_KEY=your-api-key-here

# Used for enhanced features and reliability
```

**Get Alchemy API Key:**
1. Visit `https://alchemy.com`
2. Create account
3. Create app
4. Copy API key
5. Add to .env

#### Etherscan API (Transaction Verification)

```env
ETHERSCAN_API_KEY=your-etherscan-key
```

### Smart Contract Deployment

```bash
# For Sepolia testnet
cd blockchain
npx hardhat run scripts/deploy.js --network sepolia

# For Mumbai testnet
npx hardhat run scripts/deploy.js --network mumbai

# For local testing
npx hardhat run scripts/deploy.js --network localhost
```

### Wallet Configuration

```env
# Deployment wallet private key (NEVER share!)
PRIVATE_KEY=0x1234567890abcdef...

# Or use mnemonic phrase
MNEMONIC=word1 word2 word3 ... word12

# Public address (optional, derived from private key)
PUBLIC_ADDRESS=0x742d35Cc6634C0532925a3b844Bc9e7595f42b00
```

### Gas Configuration

```bash
# In hardhat.config.js or .env
GAS_PRICE=20  # In gwei
GAS_LIMIT=8000000

# Or let network estimate
ESTIMATE_GAS=true
```

### Token Contract Configuration

```env
# Deployed contract addresses
CARBON_TOKEN_ADDRESS=0x123...
MRV_REGISTRY_ADDRESS=0x456...

# Token details
TOKEN_NAME=Blue Carbon Credits
TOKEN_SYMBOL=BCC
TOKEN_DECIMALS=18
```

---

## Firebase Configuration

### Optional - For Authentication & Database

```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@project.iam.gserviceaccount.com
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
```

### Setup Firebase

1. Go to `https://console.firebase.google.com`
2. Create or select project
3. Click gear icon → Project settings
4. Go to Service Accounts tab
5. Click "Generate new private key"
6. Download JSON file
7. Copy values to .env:

```json
{
  "type": "service_account",
  "project_id": "copy-to-FIREBASE_PROJECT_ID",
  "private_key": "copy-to-FIREBASE_PRIVATE_KEY",
  "client_email": "copy-to-FIREBASE_CLIENT_EMAIL",
  "client_id": "...",
  "auth_uri": "...",
  "token_uri": "...",
  "auth_provider_x509_cert_url": "...",
  "client_x509_cert_url": "..."
}
```

### Enable Firestore

1. In Firebase Console: Build → Firestore Database
2. Click "Create Database"
3. Start in production mode
4. Choose region (us-central1 recommended)
5. Done!

---

## Email Configuration

### Gmail SMTP Setup

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password  # NOT your Gmail password!
```

### Generate Gmail App Password

1. Enable 2-factor authentication on Gmail
2. Visit `https://myaccount.google.com/apppasswords`
3. Select Mail and Device type
4. Generate password (16 characters)
5. Copy to `MAIL_PASSWORD` in .env

### Alternative: SendGrid

```env
SENDGRID_API_KEY=SG.your-sendgrid-key
SENDGRID_FROM_EMAIL=noreply@bluecarbon-mrv.org
```

### Alternative: AWS SES

```env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
SES_SENDER_EMAIL=noreply@bluecarbon-mrv.org
```

### Email Settings

```env
# From address for emails
MAIL_DEFAULT_SENDER=noreply@bluecarbon-mrv.org

# Reply-to address
MAIL_REPLY_TO=support@bluecarbon-mrv.org

# Enable email notifications
ENABLE_EMAIL_NOTIFICATIONS=True
```

### Test Email Configuration

```bash
python debug_email.py
```

---

## External APIs

### Sentinel Hub (Satellite Imagery)

```env
SENTINEL_HUB_CLIENT_ID=your-client-id
SENTINEL_HUB_CLIENT_SECRET=your-client-secret
SENTINEL_HUB_INSTANCE_ID=your-instance-id
```

**Get Keys:**
1. Visit `https://sentinelhub.com`
2. Create account & project
3. Register OAuth client
4. Copy credentials

### Google Cloud (Document AI, Vision)

```env
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_API_KEY=your-api-key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

### OpenWeatherMap (Weather Data)

```env
OPENWEATHER_API_KEY=your-api-key
OPENWEATHER_BASE_URL=https://api.openweathermap.org
```

### Earth Explorer (USGS)

```env
EARTH_EXPLORER_API_KEY=your-api-key
```

---

## Feature Flags

### Development Features

```env
# Enable mock/demo mode (no real blockchain)
DEMO_MODE=True

# Enable public access without login
PUBLIC_ACCESS=True

# Enable public demo features
ENABLE_PUBLIC_DEMO=True

# Enable debug logging
DEBUG_LOGGING=True
```

### Production Features

```env
DEMO_MODE=False
PUBLIC_ACCESS=False
ENABLE_PUBLIC_DEMO=False
DEBUG_LOGGING=False
```

### Feature Toggles

```env
# Blockchain features
ENABLE_BLOCKCHAIN=True
ENABLE_TOKEN_MINTING=True
ENABLE_TRADING=True

# Analytics features
ENABLE_ML_PREDICTIONS=True
ENABLE_SATELLITE_DATA=True
ENABLE_DRONE_PROCESSING=True
ENABLE_GIS_ANALYSIS=True

# User features
ENABLE_EMAIL_NOTIFICATIONS=True
ENABLE_PUSH_NOTIFICATIONS=True
ENABLE_TWO_FACTOR_AUTH=False

# Admin features
ENABLE_ADMIN_DASHBOARD=True
ENABLE_ANALYTICS_DASHBOARD=True
```

---

## Security Settings

### Session Security

```env
# Session timeout in minutes
SESSION_TIMEOUT=30

# Cookie settings
SESSION_COOKIE_SECURE=True       # HTTPS only (production)
SESSION_COOKIE_HTTPONLY=True     # JavaScript cannot access
SESSION_COOKIE_SAMESITE=Lax      # CSRF protection
SESSION_COOKIE_NAME=bluecarbon_session
```

### Password Policy

```env
# Minimum password length
MIN_PASSWORD_LENGTH=8

# Require special characters
REQUIRE_SPECIAL_CHARS=True

# Require numbers
REQUIRE_NUMBERS=True

# Password expiration (days, 0 = never)
PASSWORD_EXPIRATION_DAYS=0
```

### Rate Limiting

```env
# Enable rate limiting
ENABLE_RATE_LIMITING=True

# Requests per minute
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Storage backend
RATELIMIT_STORAGE_URL=memory://
# Or use Redis: redis://localhost:6379
```

### CORS Configuration

```env
# Allowed origins
CORS_ORIGINS=http://localhost:3000,http://localhost:5000,https://yourdomain.com

# Allow credentials
CORS_ALLOW_CREDENTIALS=True
```

### JWT Configuration

```env
# JWT expiration (hours)
JWT_EXPIRATION=24

# JWT refresh expiration (days)
JWT_REFRESH_EXPIRATION=30

# JWT algorithm
JWT_ALGORITHM=HS256
```

---

## Logging Configuration

### Log Level

```env
# DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Application logs
APP_LOG_FILE=logs/app.log
APP_LOG_MAX_SIZE=10485760  # 10MB
APP_LOG_BACKUP_COUNT=10

# Database logs
DB_LOG_FILE=logs/database.log
DB_LOG_LEVEL=DEBUG  # More verbose for DB

# Blockchain logs
BLOCKCHAIN_LOG_FILE=logs/blockchain.log
```

### Log Format

```env
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

---

## Performance Settings

### Caching

```env
# Cache type: simple, redis, memcached
CACHE_TYPE=simple
CACHE_DEFAULT_TIMEOUT=300

# Or use Redis
REDIS_URL=redis://localhost:6379/0
```

### Database Connection Pooling

```env
SQLALCHEMY_POOL_SIZE=10
SQLALCHEMY_POOL_RECYCLE=3600
SQLALCHEMY_POOL_PRE_PING=True
```

### File Upload

```env
# Max upload size (in MB)
MAX_UPLOAD_SIZE=50

# Allowed file types
ALLOWED_EXTENSIONS=pdf,jpg,png,csv,xlsx,doc,docx

# Upload directory
UPLOAD_FOLDER=uploads/
```

---

## Troubleshooting

### Issue: .env file not loading

```python
# Make sure this is at the top of app.py
from dotenv import load_dotenv
load_dotenv()

# Or manually load specific file
load_dotenv('.env.production')
```

### Issue: Environment variable not found

```bash
# Restart Flask server after changing .env
# CTRL+C to stop
python app.py  # to restart

# Verify variable is loaded
python -c "import os; print(os.getenv('SECRET_KEY'))"
```

### Issue: Database connection error

```bash
# Test connection
python -c "from db import get_conn; print(get_conn())"

# Check database file/server
# SQLite: ls bluecarbon.db
# PostgreSQL: psql -l
```

### Issue: Blockchain RPC connection fails

```bash
# Test RPC connection
python -c "from web3 import Web3; w3 = Web3(Web3.HTTPProvider('YOUR_RPC_URL')); print(w3.is_connected())"

# Verify API key
echo $INFURA_PROJECT_ID  # Should print your ID
```

---

## Configuration Examples

### Development Setup

```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-not-secure
DATABASE_URL=sqlite:///bluecarbon.db
BLOCKCHAIN_MODE=localhost
DEMO_MODE=True
ENABLE_EMAIL_NOTIFICATIONS=False
```

### Production Setup

```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=very-long-secure-random-key-min-32-characters-here
DATABASE_URL=postgresql://user:password@prod-db-server:5432/bluecarbon
BLOCKCHAIN_MODE=mainnet
INFURA_PROJECT_ID=your-production-infura-id
DEMO_MODE=False
ENABLE_EMAIL_NOTIFICATIONS=True
```

### Staging Setup

```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=staging-secret-key
DATABASE_URL=postgresql://user:password@staging-db:5432/bluecarbon
BLOCKCHAIN_MODE=sepolia
DEMO_MODE=False
```

---

## Best Practices

1. ✅ **Never commit .env** - Add to .gitignore
2. ✅ **Use strong SECRET_KEY** - Min 32 random characters
3. ✅ **Rotate API keys** - Regularly update credentials
4. ✅ **Use environment-specific configs** - Different for dev/prod
5. ✅ **Document required variables** - Keep .env.example updated
6. ✅ **Use HTTPS in production** - Enable SSL/TLS
7. ✅ **Monitor logs** - Check for errors/security issues
8. ✅ **Test configuration** - Verify settings before deployment

---

## Next Steps

- 📖 Read [Installation Guide](INSTALLATION.md)
- 🚀 Check [Deployment Guide](DEPLOYMENT.md)
- 🧪 Review [Testing Guide](TESTING.md)
- 🐛 Report issues on GitHub
