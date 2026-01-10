# 📊 API Documentation

## Complete BlueCarbon MRV API Reference

---

## Table of Contents

1. [Base URL](#base-url)
2. [Authentication](#authentication)
3. [Response Format](#response-format)
4. [Error Codes](#error-codes)
5. [Authentication Endpoints](#authentication-endpoints)
6. [Project Endpoints](#project-endpoints)
7. [Blockchain Endpoints](#blockchain-endpoints)
8. [Analytics Endpoints](#analytics-endpoints)
9. [Admin Endpoints](#admin-endpoints)
10. [File Upload](#file-upload)

---

## Base URL

```
http://localhost:5000/api
```

**Production:**
```
https://your-domain.com/api
```

---

## Authentication

### Header Format

Include JWT token in request headers:

```
Authorization: Bearer YOUR_JWT_TOKEN
```

### Get Token

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Token Expiration

Tokens expire after **24 hours**. Refresh using:

```bash
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN"
```

---

## Response Format

### Success Response

```json
{
  "success": true,
  "status": 200,
  "data": {
    "id": "123",
    "name": "Mangrove Restoration Project"
  },
  "message": "Project created successfully"
}
```

### Error Response

```json
{
  "success": false,
  "status": 400,
  "error": "invalid_request",
  "message": "Project name is required"
}
```

---

## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | CREATED | Resource created |
| 400 | BAD REQUEST | Invalid request format |
| 401 | UNAUTHORIZED | Authentication required |
| 403 | FORBIDDEN | Permission denied |
| 404 | NOT FOUND | Resource not found |
| 409 | CONFLICT | Resource already exists |
| 429 | RATE LIMIT | Too many requests |
| 500 | SERVER ERROR | Internal server error |
| 503 | SERVICE UNAVAILABLE | Server temporarily down |

---

## Authentication Endpoints

### Register User

```
POST /api/auth/register
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "organization": "Ocean Conservation NGO",
  "role": "ngo"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "user_id": "user_123",
    "email": "user@example.com",
    "token": "eyJhbGciOiJIUzI1NiIs..."
  },
  "message": "User registered successfully"
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| email | string | ✓ | User email |
| password | string | ✓ | Min 8 characters |
| full_name | string | ✓ | User full name |
| organization | string | ✓ | Organization name |
| role | enum | ✓ | ngo, admin, industry |

---

### Login

```
POST /api/auth/login
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user_id": "user_123",
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 86400
  },
  "message": "Login successful"
}
```

---

### Verify Email

```
GET /api/auth/verify?token=verification_token
```

**Response (200):**
```json
{
  "success": true,
  "message": "Email verified successfully"
}
```

---

### Get Current User

```
GET /api/auth/user
```

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user_id": "user_123",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "ngo",
    "verified": true,
    "created_at": "2024-01-10T12:00:00Z"
  }
}
```

---

### Refresh Token

```
POST /api/auth/refresh
```

**Headers:**
```
Authorization: Bearer YOUR_REFRESH_TOKEN
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 86400
  }
}
```

---

### Logout

```
POST /api/auth/logout
```

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
```

**Response (200):**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

---

## Project Endpoints

### Create Project

```
POST /api/projects
```

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
```

**Request:**
```json
{
  "name": "Mangrove Restoration Initiative",
  "description": "Restoring coastal mangrove ecosystems",
  "location": {
    "latitude": 12.9716,
    "longitude": 77.5946,
    "area": 500
  },
  "project_type": "mangrove_restoration",
  "duration_years": 10,
  "expected_carbon_credits": 5000,
  "ngo_name": "Ocean Conservation NGO"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "project_id": "proj_12345",
    "status": "pending_verification",
    "created_at": "2024-01-10T12:00:00Z"
  },
  "message": "Project created successfully"
}
```

---

### Get All Projects

```
GET /api/projects
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| status | string | - | pending_verification, verified, rejected |
| page | integer | 1 | Page number |
| limit | integer | 20 | Results per page |
| sort | string | created_at | Sort field |

**Request:**
```bash
curl "http://localhost:5000/api/projects?status=verified&page=1&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "projects": [
      {
        "project_id": "proj_12345",
        "name": "Mangrove Restoration Initiative",
        "status": "verified",
        "carbon_credits": 5000,
        "created_at": "2024-01-10T12:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 45,
      "pages": 5
    }
  }
}
```

---

### Get Project Details

```
GET /api/projects/:project_id
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "project_id": "proj_12345",
    "name": "Mangrove Restoration Initiative",
    "description": "Restoring coastal mangrove ecosystems",
    "status": "verified",
    "location": {
      "latitude": 12.9716,
      "longitude": 77.5946,
      "area": 500
    },
    "carbon_credits": 5000,
    "ngo_name": "Ocean Conservation NGO",
    "created_at": "2024-01-10T12:00:00Z",
    "verified_at": "2024-01-12T10:30:00Z",
    "verified_by": "admin_123"
  }
}
```

---

### Update Project

```
PUT /api/projects/:project_id
```

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
```

**Request:**
```json
{
  "name": "Updated Project Name",
  "description": "Updated description",
  "expected_carbon_credits": 6000
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "project_id": "proj_12345",
    "updated_fields": ["name", "description", "expected_carbon_credits"]
  },
  "message": "Project updated successfully"
}
```

---

### Delete Project

```
DELETE /api/projects/:project_id
```

**Response (200):**
```json
{
  "success": true,
  "message": "Project deleted successfully"
}
```

---

### Search Projects

```
GET /api/projects/search?query=mangrove
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| query | string | Search term |
| type | string | mangrove_restoration, seagrass, salt_marsh |
| status | string | verified, pending_verification |
| min_credits | integer | Minimum carbon credits |
| max_credits | integer | Maximum carbon credits |

---

## Blockchain Endpoints

### Verify Project on Blockchain

```
POST /api/blockchain/verify
```

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
```

**Request:**
```json
{
  "project_id": "proj_12345",
  "verification_data": {
    "carbon_sequestration": 5000,
    "location_hash": "0x1234567890abcdef",
    "timestamp": "2024-01-12T10:30:00Z"
  }
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "project_id": "proj_12345",
    "transaction_hash": "0xabcd1234...",
    "contract_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f42b00",
    "block_number": 1234567,
    "status": "confirmed",
    "timestamp": "2024-01-12T10:30:00Z"
  },
  "message": "Project verified on blockchain"
}
```

---

### Get Transaction Status

```
GET /api/blockchain/status/:transaction_hash
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "transaction_hash": "0xabcd1234...",
    "status": "confirmed",
    "confirmations": 12,
    "gas_used": 125000,
    "gas_price": "25 gwei",
    "from": "0x742d35Cc6634C0532925a3b844Bc9e7595f42b00",
    "to": "0x123456789...",
    "value": "0",
    "block_number": 1234567,
    "timestamp": "2024-01-12T10:30:00Z"
  }
}
```

---

### Mint Carbon Credits

```
POST /api/blockchain/mint
```

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
```

**Request:**
```json
{
  "project_id": "proj_12345",
  "amount": 5000,
  "recipient_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f42b00"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "token_transaction_hash": "0xabcd1234...",
    "amount": 5000,
    "decimals": 18,
    "contract_address": "0x123456...",
    "timestamp": "2024-01-12T10:30:00Z",
    "status": "minted"
  },
  "message": "Tokens minted successfully"
}
```

---

### Get Token Information

```
GET /api/blockchain/tokens/:project_id
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "project_id": "proj_12345",
    "token_name": "Blue Carbon Credits",
    "token_symbol": "BCC",
    "contract_address": "0x123456...",
    "total_supply": 5000,
    "decimals": 18,
    "holders": 15,
    "transfers": 42,
    "last_transfer": "2024-01-12T10:30:00Z"
  }
}
```

---

### Get Transaction History

```
GET /api/blockchain/history/:project_id
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| limit | integer | Max results (default 100) |
| offset | integer | Starting position |
| type | string | mint, transfer, burn |

**Response (200):**
```json
{
  "success": true,
  "data": {
    "project_id": "proj_12345",
    "transactions": [
      {
        "hash": "0xabcd1234...",
        "type": "mint",
        "from": "0x742d35Cc6634C0532925a3b844Bc9e7595f42b00",
        "to": "0x123456789...",
        "amount": 5000,
        "block_number": 1234567,
        "timestamp": "2024-01-12T10:30:00Z"
      }
    ],
    "total": 42
  }
}
```

---

## Analytics Endpoints

### Get Carbon Metrics

```
GET /api/analytics/carbon/:project_id
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "project_id": "proj_12345",
    "carbon_sequestration": {
      "current": 2500,
      "projected": 5000,
      "unit": "tonnes_co2e"
    },
    "forest_area": {
      "current": 250,
      "projected": 500,
      "unit": "hectares"
    },
    "biodiversity_index": 0.78,
    "timestamp": "2024-01-12T10:30:00Z"
  }
}
```

---

### Get Satellite Data

```
GET /api/analytics/satellite/:project_id
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| start_date | string | YYYY-MM-DD |
| end_date | string | YYYY-MM-DD |
| bands | string | RGB, NIR, NDVI |

**Response (200):**
```json
{
  "success": true,
  "data": {
    "project_id": "proj_12345",
    "satellite_data": [
      {
        "date": "2024-01-12",
        "ndvi": 0.65,
        "temperature": 28.5,
        "vegetation_coverage": 0.78,
        "water_coverage": 0.15
      }
    ],
    "source": "Sentinel-2",
    "resolution": "10m"
  }
}
```

---

### Get ML Predictions

```
POST /api/analytics/predict
```

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
```

**Request:**
```json
{
  "project_id": "proj_12345",
  "forecast_years": 10
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "project_id": "proj_12345",
    "predictions": [
      {
        "year": 2024,
        "predicted_carbon_sequestration": 5000,
        "confidence_interval": [4500, 5500]
      },
      {
        "year": 2025,
        "predicted_carbon_sequestration": 5200,
        "confidence_interval": [4700, 5700]
      }
    ],
    "model_accuracy": 0.92,
    "forecast_period_years": 10
  }
}
```

---

### Get GIS Analysis

```
GET /api/analytics/gis/:project_id
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "project_id": "proj_12345",
    "geospatial": {
      "area": 500,
      "perimeter": 2500,
      "coordinates": {
        "north": 12.99,
        "south": 12.95,
        "east": 77.60,
        "west": 77.59
      },
      "soil_type": "alluvial",
      "elevation": 15,
      "slope": 2.5
    },
    "analysis_timestamp": "2024-01-12T10:30:00Z"
  }
}
```

---

### Get Dashboard Data

```
GET /api/analytics/dashboard
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| timeframe | string | 7d, 30d, 90d, 1y |

**Response (200):**
```json
{
  "success": true,
  "data": {
    "total_projects": 150,
    "total_carbon_credits": 750000,
    "verified_projects": 120,
    "pending_verification": 20,
    "rejected": 10,
    "recent_projects": [...],
    "trending_projects": [...],
    "top_ngos": [...]
  }
}
```

---

## Admin Endpoints

### List All Users

```
GET /api/admin/users
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| role | string | ngo, admin, industry |
| page | integer | Page number |
| limit | integer | Results per page |

**Headers:**
```
Authorization: Bearer ADMIN_TOKEN
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "user_id": "user_123",
        "email": "user@example.com",
        "role": "ngo",
        "organization": "Ocean Conservation NGO",
        "verified": true,
        "created_at": "2024-01-10T12:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 250,
      "pages": 13
    }
  }
}
```

---

### List All Projects (Admin)

```
GET /api/admin/projects
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "projects": [
      {
        "project_id": "proj_12345",
        "name": "Mangrove Restoration Initiative",
        "ngo_name": "Ocean Conservation NGO",
        "status": "pending_verification",
        "created_at": "2024-01-10T12:00:00Z"
      }
    ],
    "statistics": {
      "total": 150,
      "pending": 20,
      "verified": 120,
      "rejected": 10
    }
  }
}
```

---

### Approve Project

```
PUT /api/admin/approve/:project_id
```

**Headers:**
```
Authorization: Bearer ADMIN_TOKEN
Content-Type: application/json
```

**Request:**
```json
{
  "verified": true,
  "notes": "Verification complete. All documents approved.",
  "carbon_credits_approved": 5000
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "project_id": "proj_12345",
    "status": "verified",
    "verified_at": "2024-01-12T10:30:00Z",
    "verified_by": "admin_123"
  },
  "message": "Project approved successfully"
}
```

---

### Delete User

```
DELETE /api/admin/user/:user_id
```

**Response (200):**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

---

### Get System Statistics

```
GET /api/admin/stats
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "users": {
      "total": 250,
      "ngo": 100,
      "admin": 5,
      "industry": 145
    },
    "projects": {
      "total": 150,
      "verified": 120,
      "pending": 20,
      "rejected": 10
    },
    "blockchain": {
      "transactions": 450,
      "tokens_minted": 750000,
      "network": "sepolia"
    },
    "system_uptime": 99.9,
    "last_backup": "2024-01-12T10:30:00Z"
  }
}
```

---

## File Upload

### Upload Project Document

```
POST /api/projects/:project_id/upload
```

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
Content-Type: multipart/form-data
```

**Form Data:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | file | ✓ | Document to upload |
| document_type | string | ✓ | site_plan, survey_report, environmental_assessment |

**Request (using curl):**
```bash
curl -X POST http://localhost:5000/api/projects/proj_12345/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "document_type=survey_report"
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "file_id": "file_123",
    "filename": "document.pdf",
    "file_size": 2048576,
    "document_type": "survey_report",
    "upload_url": "/uploads/projects/proj_12345/document.pdf",
    "uploaded_at": "2024-01-12T10:30:00Z"
  },
  "message": "File uploaded successfully"
}
```

---

## Rate Limiting

API requests are rate-limited to **100 requests per minute** per user.

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705055400
```

When limit exceeded:
```json
{
  "success": false,
  "status": 429,
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Try again after 60 seconds.",
  "retry_after": 60
}
```

---

## Testing with cURL

### Example: Create Project

```bash
curl -X POST http://localhost:5000/api/projects \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mangrove Restoration",
    "location": {
      "latitude": 12.9716,
      "longitude": 77.5946,
      "area": 500
    },
    "expected_carbon_credits": 5000
  }'
```

### Example: Get Projects

```bash
curl -X GET "http://localhost:5000/api/projects?status=verified&page=1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Webhooks (Coming Soon)

Subscribe to real-time events:
- `project.created`
- `project.verified`
- `tokens.minted`
- `transaction.confirmed`

---

## SDKs & Libraries

Coming soon:
- JavaScript/TypeScript SDK
- Python SDK
- Go SDK

---

## Need Help?

- 📖 Check [Documentation](docs/)
- 🐛 Report [Issues](https://github.com/your-repo/issues)
- 💬 [Discussions](https://github.com/your-repo/discussions)
- 📧 Email: api-support@bluecarbon-mrv.org

---

**Last Updated:** January 2024  
**API Version:** 1.0.0
