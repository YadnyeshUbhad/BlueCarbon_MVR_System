# BlueCarbon MVR System Architecture

## System Overview Diagram

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI1[Main Portal - Glassmorphism UI]
        UI2[NGO Dashboard]
        UI3[Admin Dashboard] 
        UI4[Industry Dashboard]
        UI5[PWA Mobile Interface]
    end

    subgraph "Application Layer"
        APP1[Flask Web Server]
        APP2[API Gateway]
        APP3[Authentication Service]
        APP4[Session Management]
    end

    subgraph "Business Logic Layer"
        BL1[Project Management]
        BL2[Blockchain Service]
        BL3[Token Management]
        BL4[Verification Engine]
        BL5[Analytics Engine]
    end

    subgraph "Data Processing Layer"
        DP1[Satellite Data Processor]
        DP2[Drone Image Analyzer]
        DP3[ML Prediction Engine]
        DP4[GIS Calculator]
        DP5[Carbon Calculator]
    end

    subgraph "Blockchain Layer"
        BC1[Smart Contract Interface]
        BC2[Transaction Manager]
        BC3[Token Lifecycle]
        BC4[Audit Trail]
        BC5[Hash Generator]
    end

    subgraph "Data Storage Layer"
        DB1[Project Database]
        DB2[User Database]
        DB3[Transaction Ledger]
        DB4[File Storage]
        DB5[Cache Layer]
    end

    UI1 --> APP1
    UI2 --> APP1
    UI3 --> APP1
    UI4 --> APP1
    UI5 --> APP1

    APP1 --> APP2
    APP2 --> BL1
    APP2 --> BL2
    APP2 --> BL3

    BL1 --> DP1
    BL1 --> DP2
    BL2 --> BC1
    BL3 --> BC2
    BL4 --> DP3
    BL5 --> DP4
    BL5 --> DP5

    BC1 --> BC2
    BC2 --> BC3
    BC3 --> BC4
    BC4 --> BC5

    BL1 --> DB1
    BL2 --> DB3
    APP3 --> DB2
    DP1 --> DB4
    DP2 --> DB4

    BC4 --> DB3
    BC5 --> DB3
```

## Data Flow Sequence

```mermaid
sequenceDiagram
    participant NGO as NGO User
    participant Web as Web Interface
    participant API as Flask API
    participant Logic as Business Logic
    participant BC as Blockchain
    participant DB as Database
    participant Admin as Admin User
    participant Industry as Industry User

    NGO->>Web: Access Portal
    Web->>NGO: Display Glassmorphism UI
    
    NGO->>Web: Submit Project
    Web->>API: POST /projects/submit
    API->>Logic: Validate Project Data
    Logic->>BC: Create Blockchain Record
    BC->>BC: Generate Transaction Hash
    BC-->>Logic: Return Project ID
    Logic->>DB: Store Project Data
    DB-->>Logic: Confirmation
    Logic-->>API: Project Created
    API-->>Web: Success Response
    Web-->>NGO: Project ID Displayed
    
    Admin->>Web: Login to Admin Portal
    Web->>API: POST /admin/login
    API->>Logic: Verify Credentials
    Logic->>DB: Check User Permissions
    DB-->>Logic: Admin Confirmed
    Logic-->>API: Auth Token
    API-->>Web: Dashboard Access
    
    Admin->>Web: Review Project
    Web->>API: GET /projects/{id}
    API->>Logic: Fetch Project Details
    Logic->>DB: Retrieve Project Data
    DB-->>Logic: Project Information
    Logic->>BC: Verify Blockchain Record
    BC-->>Logic: Verification Status
    Logic-->>API: Complete Project Data
    API-->>Web: Project Dashboard
    
    Admin->>Web: Approve Project
    Web->>API: POST /projects/{id}/verify
    API->>Logic: Process Verification
    Logic->>BC: Update Project Status
    BC->>BC: Mint Carbon Tokens
    BC-->>Logic: Token IDs Generated
    Logic->>DB: Update Project Status
    Logic-->>API: Verification Complete
    API-->>Web: Success Confirmation
    
    Industry->>Web: Browse Carbon Credits
    Web->>API: GET /blockchain/token-visualization
    API->>Logic: Fetch Token Data
    Logic->>BC: Query Token Information
    BC-->>Logic: Token Portfolio
    Logic-->>API: Token Analytics
    API-->>Web: Visualization Dashboard
    
    Industry->>Web: Purchase Tokens
    Web->>API: POST /blockchain/transfer
    API->>Logic: Validate Transfer
    Logic->>BC: Execute Token Transfer
    BC->>BC: Update Ownership
    BC-->>Logic: Transfer Confirmation
    Logic->>DB: Record Transaction
    Logic-->>API: Transfer Complete
    API-->>Web: Success Message
```

## Component Interaction Diagram

```mermaid
graph LR
    subgraph "Frontend Components"
        A[Main Portal HTML]
        B[CSS Animations]
        C[JavaScript PWA]
        D[Dashboard Templates]
    end

    subgraph "Backend Services"
        E[Flask Routes]
        F[Blockchain Service]
        G[Project Manager]
        H[Token Service]
        I[Verification Engine]
    end

    subgraph "Data Models"
        J[Project Model]
        K[User Model]
        L[Token Model]
        M[Transaction Model]
    end

    subgraph "External Interfaces"
        N[Blockchain Mock]
        O[File Storage]
        P[Cache System]
    end

    A --> E
    B --> A
    C --> E
    D --> E

    E --> F
    E --> G
    F --> H
    G --> I
    H --> L
    I --> J

    J --> N
    K --> O
    L --> N
    M --> P

    F --> M
    G --> J
    H --> M
    I --> K
```

## Technology Stack Visualization

```mermaid
graph TD
    subgraph "Presentation Layer"
        HTML[HTML5 + CSS3]
        JS[JavaScript ES6+]
        PWA[Service Worker]
        RESP[Responsive Design]
    end

    subgraph "Application Framework"
        FLASK[Flask Web Framework]
        JINJA[Jinja2 Templates]
        WTF[WTForms]
        LOGIN[Flask-Login]
    end

    subgraph "Business Logic"
        BLOCKCHAIN[Blockchain Module]
        PROJECT[Project Management]
        TOKEN[Token Lifecycle]
        VERIFY[Verification Engine]
    end

    subgraph "Data Processing"
        NUMPY[NumPy]
        OPENCV[OpenCV]
        CALC[Carbon Calculator]
        PREDICT[ML Predictor]
    end

    subgraph "Data Storage"
        MEMORY[In-Memory DB]
        FILES[File System]
        CACHE[Cache Layer]
        AUDIT[Audit Trail]
    end

    HTML --> FLASK
    JS --> FLASK
    PWA --> FLASK
    RESP --> HTML

    FLASK --> BLOCKCHAIN
    FLASK --> PROJECT
    JINJA --> HTML
    WTF --> FLASK
    LOGIN --> FLASK

    BLOCKCHAIN --> TOKEN
    PROJECT --> VERIFY
    TOKEN --> AUDIT
    VERIFY --> PROJECT

    PROJECT --> NUMPY
    VERIFY --> OPENCV
    TOKEN --> CALC
    PROJECT --> PREDICT

    PROJECT --> MEMORY
    VERIFY --> FILES
    TOKEN --> CACHE
    BLOCKCHAIN --> AUDIT
```

## Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        AUTH[Authentication]
        AUTHZ[Authorization]
        ENCRYPT[Encryption]
        AUDIT[Audit Logging]
        VALIDATE[Input Validation]
    end

    subgraph "User Access Control"
        LOGIN[Login System]
        SESSION[Session Management]
        PERM[Permission Checks]
        ROLE[Role-Based Access]
    end

    subgraph "Data Protection"
        HASH[Password Hashing]
        TOKEN[CSRF Tokens]
        SANITIZE[Data Sanitization]
        SECURE[HTTPS Enforcement]
    end

    subgraph "Blockchain Security"
        CRYPTO[Cryptographic Hashing]
        IMMUTABLE[Immutable Records]
        VERIFY[Transaction Verification]
        CONSENSUS[Consensus Mechanism]
    end

    AUTH --> LOGIN
    AUTHZ --> PERM
    ENCRYPT --> HASH
    AUDIT --> VALIDATE

    LOGIN --> SESSION
    SESSION --> ROLE
    PERM --> ROLE
    ROLE --> AUTHZ

    HASH --> TOKEN
    TOKEN --> SANITIZE
    SANITIZE --> SECURE
    SECURE --> VALIDATE

    CRYPTO --> IMMUTABLE
    IMMUTABLE --> VERIFY
    VERIFY --> CONSENSUS
    CONSENSUS --> AUDIT
```

---

## How to Use These Diagrams

These Mermaid diagrams are designed to render automatically on GitHub. They provide:

1. **System Architecture**: Overall component relationships and data flow
2. **Sequence Diagrams**: Step-by-step process flows for key operations
3. **Component Interaction**: Detailed technical component relationships
4. **Technology Stack**: Visual representation of technologies used
5. **Security Architecture**: Security layers and protection mechanisms

To include these in your README.md, use the following format:

```markdown
## System Architecture

```mermaid
[Copy any diagram from above]
```
```