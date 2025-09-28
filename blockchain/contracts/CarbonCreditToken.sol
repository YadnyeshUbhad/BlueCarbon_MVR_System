// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";

/**
 * @title CarbonCreditToken
 * @dev ERC-1155 multi-token contract for Blue Carbon Credits
 */
contract CarbonCreditToken is ERC1155, AccessControl, ReentrancyGuard, Pausable {
    // Role definitions
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    
    // Token counter
    uint256 private _tokenCounter;
    
    // Registry contract reference
    address public registryContract;
    
    // Token info
    struct TokenBatch {
        uint256 id;
        uint256 projectId;
        address ngo;
        string projectName;
        uint256 amount;
        uint256 mintTimestamp;
    }
    
    // Storage
    mapping(uint256 => TokenBatch) public tokenBatches;
    
    // Statistics
    uint256 public totalBatches;
    uint256 public totalCreditsIssued;
    
    // Events
    event CreditsMinted(
        uint256 indexed tokenId,
        uint256 indexed projectId,
        address indexed ngo,
        uint256 amount
    );
    
    constructor(
        address _registryContract,
        address _admin
    ) ERC1155("https://api.bluecarbon.mrv/tokens/{id}.json") {
        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(ADMIN_ROLE, _admin);
        _grantRole(MINTER_ROLE, _admin);
        
        registryContract = _registryContract;
    }
    
    /**
     * @dev Mint carbon credits
     */
    function mintCredits(
        address _ngo,
        uint256 _projectId,
        string memory _projectName,
        uint256 _amount
    ) external onlyRole(MINTER_ROLE) whenNotPaused returns (uint256) {
        require(_ngo != address(0), "Invalid NGO address");
        require(_amount > 0, "Amount must be greater than 0");
        require(bytes(_projectName).length > 0, "Project name required");
        
        _tokenCounter++;
        uint256 tokenId = _tokenCounter;
        
        tokenBatches[tokenId] = TokenBatch({
            id: tokenId,
            projectId: _projectId,
            ngo: _ngo,
            projectName: _projectName,
            amount: _amount,
            mintTimestamp: block.timestamp
        });
        
        // Mint tokens to NGO
        _mint(_ngo, tokenId, _amount, "");
        
        // Update statistics
        totalBatches++;
        totalCreditsIssued += _amount;
        
        emit CreditsMinted(tokenId, _projectId, _ngo, _amount);
        return tokenId;
    }
    
    /**
     * @dev Grant minter role
     */
    function grantMinterRole(address _minter) external onlyRole(ADMIN_ROLE) {
        grantRole(MINTER_ROLE, _minter);
    }
    
    /**
     * @dev Get total number of token batches
     */
    function getTotalBatches() external view returns (uint256) {
        return totalBatches;
    }
    
    /**
     * @dev Get token name
     */
    function name() external pure returns (string memory) {
        return "Blue Carbon Credits";
    }
    
    /**
     * @dev Get token symbol
     */
    function symbol() external pure returns (string memory) {
        return "BCC";
    }
    
    /**
     * @dev Get token decimals (for display purposes)
     */
    function decimals() external pure returns (uint8) {
        return 18;
    }
    
    /**
     * @dev Override required by Solidity
     */
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC1155, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}