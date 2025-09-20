// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "./MRVRegistry.sol";

/**
 * @title CarbonCreditToken
 * @dev ERC20 token representing verified blue carbon credits
 * Integrates with MRV registry for verified data-backed minting
 */
contract CarbonCreditToken is ERC20, AccessControl, Pausable {
    using Counters for Counters.Counter;

    // Role definitions
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant BURNER_ROLE = keccak256("BURNER_ROLE");

    // MRV Registry integration
    MRVRegistry public mrvRegistry;
    
    // Credit batch tracking
    Counters.Counter private _batchIds;
    
    // Credit batch structure
    struct CreditBatch {
        uint256 batchId;
        uint256 mrvRecordId; // Link to MRV data
        string projectId;
        uint256 totalCredits;
        uint256 issuanceDate;
        uint256 vintageYear;
        string methodology; // Carbon methodology used
        bool retired; // Whether credits are retired
        address issuer;
        string serialNumber; // Unique serial for this batch
    }
    
    // Storage mappings
    mapping(uint256 => CreditBatch) public creditBatches;
    mapping(uint256 => uint256) public mrvRecordToBatch; // MRV record ID to batch ID
    mapping(address => uint256[]) public userBatches;
    mapping(string => uint256[]) public projectBatches;
    
    // Retirement tracking
    mapping(address => uint256) public totalRetired;
    uint256 public globalRetiredCredits;
    
    // Events
    event CreditsIssued(
        uint256 indexed batchId,
        uint256 indexed mrvRecordId,
        string indexed projectId,
        address to,
        uint256 amount,
        string serialNumber
    );
    
    event CreditsRetired(
        uint256 indexed batchId,
        address indexed retiree,
        uint256 amount,
        string reason
    );
    
    event BatchCreated(
        uint256 indexed batchId,
        string indexed projectId,
        uint256 totalCredits,
        uint256 vintageYear
    );
    
    event MRVRegistryUpdated(
        address indexed oldRegistry,
        address indexed newRegistry
    );

    constructor(
        address _mrvRegistry,
        address _admin
    ) ERC20("Blue Carbon Credit", "BCC") {
        require(_mrvRegistry != address(0), "MRV Registry address cannot be zero");
        require(_admin != address(0), "Admin address cannot be zero");
        
        mrvRegistry = MRVRegistry(_mrvRegistry);
        
        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(ADMIN_ROLE, _admin);
        _grantRole(MINTER_ROLE, _admin);
    }

    /**
     * @dev Issue carbon credits based on verified MRV data
     * @param _mrvRecordId MRV record ID from registry
     * @param _recipient Address to receive credits
     * @param _creditAmount Amount of credits to issue
     * @param _vintageYear Year the carbon sequestration occurred
     * @param _methodology Carbon accounting methodology used
     * @param _serialNumber Unique serial number for this batch
     */
    function issueCredits(
        uint256 _mrvRecordId,
        address _recipient,
        uint256 _creditAmount,
        uint256 _vintageYear,
        string memory _methodology,
        string memory _serialNumber
    ) external onlyRole(MINTER_ROLE) whenNotPaused returns (uint256) {
        require(_recipient != address(0), "Recipient cannot be zero address");
        require(_creditAmount > 0, "Credit amount must be greater than 0");
        require(_vintageYear <= getCurrentYear(), "Vintage year cannot be in future");
        require(bytes(_serialNumber).length > 0, "Serial number cannot be empty");
        require(mrvRecordToBatch[_mrvRecordId] == 0, "Credits already issued for this MRV record");
        
        // Verify MRV data exists and is verified
        MRVRegistry.MRVData memory mrvData = mrvRegistry.getMRVData(_mrvRecordId);
        require(
            mrvData.status == MRVRegistry.VerificationStatus.VERIFIED,
            "MRV data must be verified"
        );
        
        // Create new credit batch
        _batchIds.increment();
        uint256 newBatchId = _batchIds.current();
        
        CreditBatch storage newBatch = creditBatches[newBatchId];
        newBatch.batchId = newBatchId;
        newBatch.mrvRecordId = _mrvRecordId;
        newBatch.projectId = mrvData.projectId;
        newBatch.totalCredits = _creditAmount;
        newBatch.issuanceDate = block.timestamp;
        newBatch.vintageYear = _vintageYear;
        newBatch.methodology = _methodology;
        newBatch.retired = false;
        newBatch.issuer = msg.sender;
        newBatch.serialNumber = _serialNumber;
        
        // Update tracking mappings
        mrvRecordToBatch[_mrvRecordId] = newBatchId;
        userBatches[_recipient].push(newBatchId);
        projectBatches[mrvData.projectId].push(newBatchId);
        
        // Mint tokens to recipient
        _mint(_recipient, _creditAmount * 10 ** decimals());
        
        emit BatchCreated(newBatchId, mrvData.projectId, _creditAmount, _vintageYear);
        emit CreditsIssued(
            newBatchId,
            _mrvRecordId,
            mrvData.projectId,
            _recipient,
            _creditAmount,
            _serialNumber
        );
        
        return newBatchId;
    }

    /**
     * @dev Retire carbon credits (remove from circulation)
     * @param _batchId Batch ID to retire credits from
     * @param _amount Amount of credits to retire
     * @param _reason Reason for retirement
     */
    function retireCredits(
        uint256 _batchId,
        uint256 _amount,
        string memory _reason
    ) external whenNotPaused {
        require(_batchId <= _batchIds.current() && _batchId > 0, "Invalid batch ID");
        require(_amount > 0, "Amount must be greater than 0");
        require(bytes(_reason).length > 0, "Retirement reason required");
        
        CreditBatch storage batch = creditBatches[_batchId];
        require(!batch.retired, "Batch already fully retired");
        
        uint256 tokenAmount = _amount * 10 ** decimals();
        require(balanceOf(msg.sender) >= tokenAmount, "Insufficient balance");
        
        // Burn tokens
        _burn(msg.sender, tokenAmount);
        
        // Update retirement tracking
        totalRetired[msg.sender] += _amount;
        globalRetiredCredits += _amount;
        
        // If all credits in batch are retired, mark batch as retired
        if (totalSupply() == 0 || _amount >= batch.totalCredits) {
            batch.retired = true;
        }
        
        emit CreditsRetired(_batchId, msg.sender, _amount, _reason);
    }

    /**
     * @dev Get credit batch information
     * @param _batchId Batch ID to query
     */
    function getCreditBatch(uint256 _batchId) 
        external 
        view 
        returns (CreditBatch memory) 
    {
        require(_batchId <= _batchIds.current() && _batchId > 0, "Invalid batch ID");
        return creditBatches[_batchId];
    }

    /**
     * @dev Get all batches for a project
     * @param _projectId Project ID
     */
    function getProjectBatches(string memory _projectId) 
        external 
        view 
        returns (uint256[] memory) 
    {
        return projectBatches[_projectId];
    }

    /**
     * @dev Get all batches owned by a user
     * @param _user User address
     */
    function getUserBatches(address _user) 
        external 
        view 
        returns (uint256[] memory) 
    {
        return userBatches[_user];
    }

    /**
     * @dev Get total number of batches
     */
    function getTotalBatches() external view returns (uint256) {
        return _batchIds.current();
    }

    /**
     * @dev Calculate project statistics
     * @param _projectId Project ID
     */
    function getProjectStats(string memory _projectId)
        external
        view
        returns (
            uint256 totalIssued,
            uint256 totalRetired,
            uint256 totalActive,
            uint256 batchCount
        )
    {
        uint256[] memory batches = projectBatches[_projectId];
        batchCount = batches.length;
        
        for (uint256 i = 0; i < batches.length; i++) {
            CreditBatch memory batch = creditBatches[batches[i]];
            totalIssued += batch.totalCredits;
            if (batch.retired) {
                totalRetired += batch.totalCredits;
            }
        }
        
        totalActive = totalIssued - totalRetired;
    }

    /**
     * @dev Get current year for vintage validation
     */
    function getCurrentYear() public view returns (uint256) {
        return (block.timestamp / 365 days) + 1970;
    }

    /**
     * @dev Update MRV Registry address
     * @param _newRegistry New MRV Registry address
     */
    function updateMRVRegistry(address _newRegistry) 
        external 
        onlyRole(ADMIN_ROLE) 
    {
        require(_newRegistry != address(0), "Registry address cannot be zero");
        address oldRegistry = address(mrvRegistry);
        mrvRegistry = MRVRegistry(_newRegistry);
        emit MRVRegistryUpdated(oldRegistry, _newRegistry);
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
     * @dev Grant minter role
     * @param _minter Address to grant minter role
     */
    function grantMinterRole(address _minter) external onlyRole(ADMIN_ROLE) {
        _grantRole(MINTER_ROLE, _minter);
    }

    /**
     * @dev Revoke minter role
     * @param _minter Address to revoke minter role from
     */
    function revokeMinterRole(address _minter) external onlyRole(ADMIN_ROLE) {
        _revokeRole(MINTER_ROLE, _minter);
    }

    /**
     * @dev Override transfer to include pause functionality
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override whenNotPaused {
        super._beforeTokenTransfer(from, to, amount);
    }

    /**
     * @dev Returns the number of decimals used for token amounts
     * Blue carbon credits typically use 3 decimals (kilograms)
     */
    function decimals() public pure override returns (uint8) {
        return 3; // 1 token = 1 kg CO2e, with 3 decimals for grams
    }
}
