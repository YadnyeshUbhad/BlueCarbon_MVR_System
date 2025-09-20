// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title MRVRegistry
 * @dev Registry for Measurement, Reporting, and Verification (MRV) of blue carbon ecosystems
 * Stores validated ecosystem data, health assessments, and carbon calculations
 */
contract MRVRegistry is AccessControl, ReentrancyGuard, Pausable {
    using Counters for Counters.Counter;

    // Role definitions
    bytes32 public constant VERIFIER_ROLE = keccak256("VERIFIER_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");

    // Counter for unique MRV record IDs
    Counters.Counter private _recordIds;

    // Ecosystem types enum
    enum EcosystemType { MANGROVE, SEAGRASS, SALTMARSH, MIXED }
    
    // Data verification status
    enum VerificationStatus { PENDING, VERIFIED, REJECTED, UNDER_REVIEW }

    // MRV Data structure
    struct MRVData {
        uint256 id;
        address submitter;
        string projectId;
        EcosystemType ecosystemType;
        
        // Location data
        int256 latitude;  // Stored as fixed point (multiply by 1e6)
        int256 longitude; // Stored as fixed point (multiply by 1e6)
        uint256 areaM2;   // Area in square meters
        
        // Ecosystem data
        uint256 healthScore; // Health score (0-100, scaled by 1e2)
        uint256 carbonStockTons; // Carbon stock in tons (scaled by 1e3)
        uint256 sequestrationRate; // Annual sequestration rate (scaled by 1e3)
        
        // Metadata
        string dataHash; // IPFS hash of raw data
        string imageHash; // IPFS hash of drone images
        uint256 timestamp;
        VerificationStatus status;
        address verifier;
        string verificationNotes;
        
        // Confidence metrics
        uint256 confidenceScore; // AI model confidence (0-100, scaled by 1e2)
        uint256 uncertaintyRange; // Uncertainty percentage (scaled by 1e2)
    }

    // Project structure for organizing MRV data
    struct Project {
        string projectId;
        string name;
        string description;
        address owner;
        bool active;
        uint256 createdAt;
        uint256[] mrvRecords; // Array of MRV record IDs
    }

    // Storage mappings
    mapping(uint256 => MRVData) public mrvRecords;
    mapping(string => Project) public projects;
    mapping(address => string[]) public userProjects;
    mapping(string => bool) public projectExists;
    
    // Events
    event MRVDataSubmitted(
        uint256 indexed recordId,
        address indexed submitter,
        string indexed projectId,
        EcosystemType ecosystemType
    );
    
    event MRVDataVerified(
        uint256 indexed recordId,
        address indexed verifier,
        VerificationStatus status
    );
    
    event ProjectCreated(
        string indexed projectId,
        address indexed owner,
        string name
    );
    
    event ProjectStatusChanged(
        string indexed projectId,
        bool active
    );

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(VERIFIER_ROLE, msg.sender);
        _grantRole(OPERATOR_ROLE, msg.sender);
    }

    /**
     * @dev Create a new project for organizing MRV data
     * @param _projectId Unique project identifier
     * @param _name Human-readable project name
     * @param _description Project description
     */
    function createProject(
        string memory _projectId,
        string memory _name,
        string memory _description
    ) external whenNotPaused {
        require(!projectExists[_projectId], "Project already exists");
        require(bytes(_projectId).length > 0, "Project ID cannot be empty");
        require(bytes(_name).length > 0, "Project name cannot be empty");

        Project storage newProject = projects[_projectId];
        newProject.projectId = _projectId;
        newProject.name = _name;
        newProject.description = _description;
        newProject.owner = msg.sender;
        newProject.active = true;
        newProject.createdAt = block.timestamp;

        projectExists[_projectId] = true;
        userProjects[msg.sender].push(_projectId);

        emit ProjectCreated(_projectId, msg.sender, _name);
    }

    /**
     * @dev Submit MRV data for verification
     * @param _projectId Project ID this data belongs to
     * @param _ecosystemType Type of blue carbon ecosystem
     * @param _latitude Latitude in degrees (scaled by 1e6)
     * @param _longitude Longitude in degrees (scaled by 1e6)
     * @param _areaM2 Area in square meters
     * @param _healthScore Ecosystem health score (0-100, scaled by 1e2)
     * @param _carbonStockTons Carbon stock in tons (scaled by 1e3)
     * @param _sequestrationRate Annual sequestration rate (scaled by 1e3)
     * @param _dataHash IPFS hash of raw ML analysis data
     * @param _imageHash IPFS hash of drone images
     * @param _confidenceScore AI model confidence (0-100, scaled by 1e2)
     * @param _uncertaintyRange Uncertainty percentage (scaled by 1e2)
     */
    function submitMRVData(
        string memory _projectId,
        EcosystemType _ecosystemType,
        int256 _latitude,
        int256 _longitude,
        uint256 _areaM2,
        uint256 _healthScore,
        uint256 _carbonStockTons,
        uint256 _sequestrationRate,
        string memory _dataHash,
        string memory _imageHash,
        uint256 _confidenceScore,
        uint256 _uncertaintyRange
    ) external whenNotPaused returns (uint256) {
        require(projectExists[_projectId], "Project does not exist");
        require(projects[_projectId].active, "Project is not active");
        require(_areaM2 > 0, "Area must be greater than 0");
        require(_healthScore <= 10000, "Health score out of range"); // Max 100.00
        require(_confidenceScore <= 10000, "Confidence score out of range");
        require(bytes(_dataHash).length > 0, "Data hash cannot be empty");

        _recordIds.increment();
        uint256 newRecordId = _recordIds.current();

        MRVData storage newRecord = mrvRecords[newRecordId];
        newRecord.id = newRecordId;
        newRecord.submitter = msg.sender;
        newRecord.projectId = _projectId;
        newRecord.ecosystemType = _ecosystemType;
        newRecord.latitude = _latitude;
        newRecord.longitude = _longitude;
        newRecord.areaM2 = _areaM2;
        newRecord.healthScore = _healthScore;
        newRecord.carbonStockTons = _carbonStockTons;
        newRecord.sequestrationRate = _sequestrationRate;
        newRecord.dataHash = _dataHash;
        newRecord.imageHash = _imageHash;
        newRecord.timestamp = block.timestamp;
        newRecord.status = VerificationStatus.PENDING;
        newRecord.confidenceScore = _confidenceScore;
        newRecord.uncertaintyRange = _uncertaintyRange;

        // Add to project's MRV records
        projects[_projectId].mrvRecords.push(newRecordId);

        emit MRVDataSubmitted(newRecordId, msg.sender, _projectId, _ecosystemType);
        
        return newRecordId;
    }

    /**
     * @dev Verify submitted MRV data
     * @param _recordId MRV record ID to verify
     * @param _status Verification status
     * @param _notes Verification notes
     */
    function verifyMRVData(
        uint256 _recordId,
        VerificationStatus _status,
        string memory _notes
    ) external onlyRole(VERIFIER_ROLE) whenNotPaused {
        require(_recordId <= _recordIds.current() && _recordId > 0, "Invalid record ID");
        require(
            _status == VerificationStatus.VERIFIED || 
            _status == VerificationStatus.REJECTED || 
            _status == VerificationStatus.UNDER_REVIEW,
            "Invalid verification status"
        );

        MRVData storage record = mrvRecords[_recordId];
        require(record.status == VerificationStatus.PENDING || 
                record.status == VerificationStatus.UNDER_REVIEW, 
                "Record not pending verification");

        record.status = _status;
        record.verifier = msg.sender;
        record.verificationNotes = _notes;

        emit MRVDataVerified(_recordId, msg.sender, _status);
    }

    /**
     * @dev Get MRV data by record ID
     * @param _recordId Record ID to retrieve
     */
    function getMRVData(uint256 _recordId) 
        external 
        view 
        returns (MRVData memory) 
    {
        require(_recordId <= _recordIds.current() && _recordId > 0, "Invalid record ID");
        return mrvRecords[_recordId];
    }

    /**
     * @dev Get all MRV records for a project
     * @param _projectId Project ID
     */
    function getProjectMRVRecords(string memory _projectId) 
        external 
        view 
        returns (uint256[] memory) 
    {
        require(projectExists[_projectId], "Project does not exist");
        return projects[_projectId].mrvRecords;
    }

    /**
     * @dev Get project information
     * @param _projectId Project ID
     */
    function getProject(string memory _projectId) 
        external 
        view 
        returns (Project memory) 
    {
        require(projectExists[_projectId], "Project does not exist");
        return projects[_projectId];
    }

    /**
     * @dev Get all projects owned by an address
     * @param _owner Owner address
     */
    function getUserProjects(address _owner) 
        external 
        view 
        returns (string[] memory) 
    {
        return userProjects[_owner];
    }

    /**
     * @dev Get total number of MRV records
     */
    function getTotalRecords() external view returns (uint256) {
        return _recordIds.current();
    }

    /**
     * @dev Get records by verification status
     * @param _status Verification status to filter by
     * @param _limit Maximum number of records to return
     * @param _offset Offset for pagination
     */
    function getRecordsByStatus(
        VerificationStatus _status,
        uint256 _limit,
        uint256 _offset
    ) external view returns (uint256[] memory) {
        uint256 totalRecords = _recordIds.current();
        uint256[] memory filteredRecords = new uint256[](_limit);
        uint256 count = 0;
        uint256 currentOffset = 0;

        for (uint256 i = 1; i <= totalRecords && count < _limit; i++) {
            if (mrvRecords[i].status == _status) {
                if (currentOffset >= _offset) {
                    filteredRecords[count] = i;
                    count++;
                }
                currentOffset++;
            }
        }

        // Resize array to actual count
        uint256[] memory result = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = filteredRecords[i];
        }

        return result;
    }

    /**
     * @dev Calculate total verified carbon stock for a project
     * @param _projectId Project ID
     */
    function getProjectCarbonStats(string memory _projectId) 
        external 
        view 
        returns (
            uint256 totalCarbonStock,
            uint256 totalSequestration,
            uint256 totalArea,
            uint256 verifiedRecords
        ) 
    {
        require(projectExists[_projectId], "Project does not exist");
        
        uint256[] memory recordIds = projects[_projectId].mrvRecords;
        
        for (uint256 i = 0; i < recordIds.length; i++) {
            MRVData memory record = mrvRecords[recordIds[i]];
            if (record.status == VerificationStatus.VERIFIED) {
                totalCarbonStock += record.carbonStockTons;
                totalSequestration += record.sequestrationRate;
                totalArea += record.areaM2;
                verifiedRecords++;
            }
        }
    }

    /**
     * @dev Update project status (active/inactive)
     * @param _projectId Project ID
     * @param _active New status
     */
    function setProjectStatus(string memory _projectId, bool _active) 
        external 
        whenNotPaused 
    {
        require(projectExists[_projectId], "Project does not exist");
        Project storage project = projects[_projectId];
        require(
            project.owner == msg.sender || hasRole(ADMIN_ROLE, msg.sender),
            "Not authorized to modify project"
        );

        project.active = _active;
        emit ProjectStatusChanged(_projectId, _active);
    }

    /**
     * @dev Emergency pause function
     */
    function pause() external onlyRole(ADMIN_ROLE) {
        _pause();
    }

    /**
     * @dev Unpause function
     */
    function unpause() external onlyRole(ADMIN_ROLE) {
        _unpause();
    }

    /**
     * @dev Grant verifier role to an address
     * @param _verifier Address to grant verifier role
     */
    function grantVerifierRole(address _verifier) external onlyRole(ADMIN_ROLE) {
        _grantRole(VERIFIER_ROLE, _verifier);
    }

    /**
     * @dev Revoke verifier role from an address
     * @param _verifier Address to revoke verifier role
     */
    function revokeVerifierRole(address _verifier) external onlyRole(ADMIN_ROLE) {
        _revokeRole(VERIFIER_ROLE, _verifier);
    }
}
