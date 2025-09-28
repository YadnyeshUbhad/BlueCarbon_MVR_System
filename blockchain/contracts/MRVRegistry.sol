// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";

/**
 * @title MRVRegistry
 * @dev Registry for Measurement, Reporting, and Verification (MRV) of blue carbon ecosystems
 */
contract MRVRegistry is AccessControl, ReentrancyGuard, Pausable {
    // Role definitions
    bytes32 public constant VERIFIER_ROLE = keccak256("VERIFIER_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    
    // Record counter
    uint256 private _recordCounter;
    
    // MRV Data structure
    struct MRVRecord {
        uint256 id;
        address submitter;
        string projectName;
        string location;
        uint256 carbonAmount;
        uint256 timestamp;
        bool verified;
        address verifier;
    }
    
    // Storage
    mapping(uint256 => MRVRecord) public records;
    
    // Events
    event MRVRecordCreated(
        uint256 indexed recordId,
        address indexed submitter,
        string projectName,
        uint256 carbonAmount
    );
    
    event MRVRecordVerified(
        uint256 indexed recordId,
        address indexed verifier
    );
    
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(VERIFIER_ROLE, msg.sender);
    }
    
    /**
     * @dev Create a new MRV record
     */
    function createRecord(
        string memory _projectName,
        string memory _location,
        uint256 _carbonAmount
    ) external whenNotPaused returns (uint256) {
        require(bytes(_projectName).length > 0, "Project name required");
        require(_carbonAmount > 0, "Carbon amount must be greater than 0");
        
        _recordCounter++;
        uint256 recordId = _recordCounter;
        
        records[recordId] = MRVRecord({
            id: recordId,
            submitter: msg.sender,
            projectName: _projectName,
            location: _location,
            carbonAmount: _carbonAmount,
            timestamp: block.timestamp,
            verified: false,
            verifier: address(0)
        });
        
        emit MRVRecordCreated(recordId, msg.sender, _projectName, _carbonAmount);
        return recordId;
    }
    
    /**
     * @dev Verify an MRV record
     */
    function verifyRecord(uint256 _recordId) 
        external 
        onlyRole(VERIFIER_ROLE) 
        whenNotPaused 
    {
        require(_recordId > 0 && _recordId <= _recordCounter, "Invalid record ID");
        require(!records[_recordId].verified, "Record already verified");
        
        records[_recordId].verified = true;
        records[_recordId].verifier = msg.sender;
        
        emit MRVRecordVerified(_recordId, msg.sender);
    }
    
    /**
     * @dev Grant verifier role
     */
    function grantVerifierRole(address _verifier) external onlyRole(ADMIN_ROLE) {
        grantRole(VERIFIER_ROLE, _verifier);
    }
    
    /**
     * @dev Get total number of records
     */
    function getTotalRecords() external view returns (uint256) {
        return _recordCounter;
    }
    
    /**
     * @dev Get record by ID
     */
    function getRecord(uint256 _recordId) external view returns (MRVRecord memory) {
        require(_recordId > 0 && _recordId <= _recordCounter, "Invalid record ID");
        return records[_recordId];
    }
}