const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("MRVRegistry", function () {
  let mrvRegistry;
  let carbonToken;
  let owner;
  let verifier;
  let user;
  let addrs;

  beforeEach(async function () {
    [owner, verifier, user, ...addrs] = await ethers.getSigners();

    // Deploy MRV Registry
    const MRVRegistry = await ethers.getContractFactory("MRVRegistry");
    mrvRegistry = await MRVRegistry.deploy();
    await mrvRegistry.deployed();

    // Deploy Carbon Credit Token
    const CarbonCreditToken = await ethers.getContractFactory("CarbonCreditToken");
    carbonToken = await CarbonCreditToken.deploy(
      mrvRegistry.address,
      owner.address
    );
    await carbonToken.deployed();

    // Grant verifier role
    await mrvRegistry.grantVerifierRole(verifier.address);
  });

  describe("Project Management", function () {
    it("Should create a project", async function () {
      const projectId = "TEST_PROJECT_001";
      const name = "Test Mangrove Project";
      const description = "A test project for mangrove restoration";

      await mrvRegistry.connect(user).createProject(projectId, name, description);

      const project = await mrvRegistry.getProject(projectId);
      expect(project.projectId).to.equal(projectId);
      expect(project.name).to.equal(name);
      expect(project.description).to.equal(description);
      expect(project.owner).to.equal(user.address);
      expect(project.active).to.be.true;
    });

    it("Should not allow duplicate project IDs", async function () {
      const projectId = "DUPLICATE_PROJECT";
      const name = "Test Project";
      const description = "Test description";

      await mrvRegistry.connect(user).createProject(projectId, name, description);
      
      await expect(
        mrvRegistry.connect(user).createProject(projectId, name, description)
      ).to.be.revertedWith("Project already exists");
    });

    it("Should track user projects", async function () {
      const projectId1 = "USER_PROJECT_001";
      const projectId2 = "USER_PROJECT_002";
      const name = "User Project";
      const description = "User project description";

      await mrvRegistry.connect(user).createProject(projectId1, name, description);
      await mrvRegistry.connect(user).createProject(projectId2, name, description);

      const userProjects = await mrvRegistry.getUserProjects(user.address);
      expect(userProjects).to.have.lengthOf(2);
      expect(userProjects[0]).to.equal(projectId1);
      expect(userProjects[1]).to.equal(projectId2);
    });
  });

  describe("MRV Data Submission", function () {
    let projectId;

    beforeEach(async function () {
      projectId = "MRV_TEST_PROJECT";
      await mrvRegistry.connect(user).createProject(
        projectId, 
        "MRV Test Project", 
        "Project for testing MRV data"
      );
    });

    it("Should submit MRV data successfully", async function () {
      const mrvData = {
        projectId: projectId,
        ecosystemType: 0, // MANGROVE
        latitude: 12345600, // 12.3456 degrees * 1e6
        longitude: 98765400, // 98.7654 degrees * 1e6
        areaM2: 10000, // 10,000 m²
        healthScore: 8500, // 85.00 scaled by 1e2
        carbonStockTons: 125000, // 125 tons scaled by 1e3
        sequestrationRate: 4800, // 4.8 tons/year scaled by 1e3
        dataHash: "QmTestDataHash123",
        imageHash: "QmTestImageHash456",
        confidenceScore: 9200, // 92.00 scaled by 1e2
        uncertaintyRange: 500 // 5.00% scaled by 1e2
      };

      await mrvRegistry.connect(user).submitMRVData(
        mrvData.projectId,
        mrvData.ecosystemType,
        mrvData.latitude,
        mrvData.longitude,
        mrvData.areaM2,
        mrvData.healthScore,
        mrvData.carbonStockTons,
        mrvData.sequestrationRate,
        mrvData.dataHash,
        mrvData.imageHash,
        mrvData.confidenceScore,
        mrvData.uncertaintyRange
      );

      const recordId = 1;
      const record = await mrvRegistry.getMRVData(recordId);
      
      expect(record.id).to.equal(recordId);
      expect(record.submitter).to.equal(user.address);
      expect(record.projectId).to.equal(projectId);
      expect(record.ecosystemType).to.equal(mrvData.ecosystemType);
      expect(record.areaM2).to.equal(mrvData.areaM2);
      expect(record.healthScore).to.equal(mrvData.healthScore);
      expect(record.status).to.equal(0); // PENDING
    });

    it("Should not allow submission to inactive project", async function () {
      // Deactivate project
      await mrvRegistry.connect(user).setProjectStatus(projectId, false);

      const mrvData = {
        projectId: projectId,
        ecosystemType: 0,
        latitude: 12345600,
        longitude: 98765400,
        areaM2: 10000,
        healthScore: 8500,
        carbonStockTons: 125000,
        sequestrationRate: 4800,
        dataHash: "QmTestDataHash123",
        imageHash: "QmTestImageHash456",
        confidenceScore: 9200,
        uncertaintyRange: 500
      };

      await expect(
        mrvRegistry.connect(user).submitMRVData(
          mrvData.projectId,
          mrvData.ecosystemType,
          mrvData.latitude,
          mrvData.longitude,
          mrvData.areaM2,
          mrvData.healthScore,
          mrvData.carbonStockTons,
          mrvData.sequestrationRate,
          mrvData.dataHash,
          mrvData.imageHash,
          mrvData.confidenceScore,
          mrvData.uncertaintyRange
        )
      ).to.be.revertedWith("Project is not active");
    });

    it("Should validate health score range", async function () {
      const mrvData = {
        projectId: projectId,
        ecosystemType: 0,
        latitude: 12345600,
        longitude: 98765400,
        areaM2: 10000,
        healthScore: 15000, // Invalid: > 10000 (100.00)
        carbonStockTons: 125000,
        sequestrationRate: 4800,
        dataHash: "QmTestDataHash123",
        imageHash: "QmTestImageHash456",
        confidenceScore: 9200,
        uncertaintyRange: 500
      };

      await expect(
        mrvRegistry.connect(user).submitMRVData(
          mrvData.projectId,
          mrvData.ecosystemType,
          mrvData.latitude,
          mrvData.longitude,
          mrvData.areaM2,
          mrvData.healthScore,
          mrvData.carbonStockTons,
          mrvData.sequestrationRate,
          mrvData.dataHash,
          mrvData.imageHash,
          mrvData.confidenceScore,
          mrvData.uncertaintyRange
        )
      ).to.be.revertedWith("Health score out of range");
    });
  });

  describe("MRV Data Verification", function () {
    let projectId;
    let recordId;

    beforeEach(async function () {
      projectId = "VERIFICATION_TEST_PROJECT";
      await mrvRegistry.connect(user).createProject(
        projectId, 
        "Verification Test Project", 
        "Project for testing verification"
      );

      // Submit MRV data
      await mrvRegistry.connect(user).submitMRVData(
        projectId,
        0, // MANGROVE
        12345600,
        98765400,
        10000,
        8500,
        125000,
        4800,
        "QmTestDataHash123",
        "QmTestImageHash456",
        9200,
        500
      );

      recordId = 1;
    });

    it("Should verify MRV data successfully", async function () {
      const notes = "Data verified through satellite imagery and field validation";
      
      await mrvRegistry.connect(verifier).verifyMRVData(
        recordId,
        1, // VERIFIED
        notes
      );

      const record = await mrvRegistry.getMRVData(recordId);
      expect(record.status).to.equal(1); // VERIFIED
      expect(record.verifier).to.equal(verifier.address);
      expect(record.verificationNotes).to.equal(notes);
    });

    it("Should reject MRV data with notes", async function () {
      const notes = "Data quality insufficient for verification";
      
      await mrvRegistry.connect(verifier).verifyMRVData(
        recordId,
        2, // REJECTED
        notes
      );

      const record = await mrvRegistry.getMRVData(recordId);
      expect(record.status).to.equal(2); // REJECTED
      expect(record.verifier).to.equal(verifier.address);
      expect(record.verificationNotes).to.equal(notes);
    });

    it("Should not allow non-verifiers to verify data", async function () {
      await expect(
        mrvRegistry.connect(user).verifyMRVData(
          recordId,
          1, // VERIFIED
          "Unauthorized verification attempt"
        )
      ).to.be.revertedWith(`AccessControl: account ${user.address.toLowerCase()} is missing role`);
    });
  });

  describe("Carbon Statistics", function () {
    let projectId;

    beforeEach(async function () {
      projectId = "STATS_TEST_PROJECT";
      await mrvRegistry.connect(user).createProject(
        projectId,
        "Stats Test Project",
        "Project for testing carbon statistics"
      );

      // Submit and verify multiple records
      for (let i = 0; i < 3; i++) {
        await mrvRegistry.connect(user).submitMRVData(
          projectId,
          0, // MANGROVE
          12345600 + i,
          98765400 + i,
          10000 + i * 1000,
          8500,
          125000 + i * 10000,
          4800,
          `QmTestDataHash${i}`,
          `QmTestImageHash${i}`,
          9200,
          500
        );

        // Verify the record
        await mrvRegistry.connect(verifier).verifyMRVData(
          i + 1,
          1, // VERIFIED
          "Verified for testing"
        );
      }
    });

    it("Should calculate project carbon statistics correctly", async function () {
      const stats = await mrvRegistry.getProjectCarbonStats(projectId);
      
      // Expected values: 125000 + 135000 + 145000 = 405000 (scaled by 1e3)
      expect(stats.totalCarbonStock).to.equal(405000);
      
      // Expected sequestration: 4800 * 3 = 14400 (scaled by 1e3)
      expect(stats.totalSequestration).to.equal(14400);
      
      // Expected area: 10000 + 11000 + 12000 = 33000
      expect(stats.totalArea).to.equal(33000);
      
      // Expected verified records: 3
      expect(stats.verifiedRecords).to.equal(3);
    });

    it("Should return project MRV records", async function () {
      const records = await mrvRegistry.getProjectMRVRecords(projectId);
      expect(records).to.have.lengthOf(3);
      expect(records[0]).to.equal(1);
      expect(records[1]).to.equal(2);
      expect(records[2]).to.equal(3);
    });
  });

  describe("Access Control", function () {
    it("Should grant and revoke verifier roles", async function () {
      const newVerifier = addrs[0];
      
      // Grant verifier role
      await mrvRegistry.connect(owner).grantVerifierRole(newVerifier.address);
      
      // Check if role was granted (by attempting verification)
      const projectId = "ACCESS_TEST_PROJECT";
      await mrvRegistry.connect(user).createProject(
        projectId,
        "Access Test Project",
        "Testing access control"
      );
      
      await mrvRegistry.connect(user).submitMRVData(
        projectId, 0, 12345600, 98765400, 10000, 8500, 125000, 4800,
        "QmTestHash", "QmTestImage", 9200, 500
      );
      
      // New verifier should be able to verify
      await expect(
        mrvRegistry.connect(newVerifier).verifyMRVData(1, 1, "Verified by new verifier")
      ).to.not.be.reverted;
      
      // Revoke role
      await mrvRegistry.connect(owner).revokeVerifierRole(newVerifier.address);
      
      // Submit another record
      await mrvRegistry.connect(user).submitMRVData(
        projectId, 0, 12345601, 98765401, 10001, 8501, 125001, 4801,
        "QmTestHash2", "QmTestImage2", 9201, 501
      );
      
      // New verifier should no longer be able to verify
      await expect(
        mrvRegistry.connect(newVerifier).verifyMRVData(2, 1, "Should fail")
      ).to.be.revertedWith(`AccessControl: account ${newVerifier.address.toLowerCase()} is missing role`);
    });

    it("Should pause and unpause contract", async function () {
      await mrvRegistry.connect(owner).pause();
      
      // Should not be able to create project when paused
      await expect(
        mrvRegistry.connect(user).createProject("PAUSED_TEST", "Test", "Description")
      ).to.be.revertedWith("Pausable: paused");
      
      // Unpause
      await mrvRegistry.connect(owner).unpause();
      
      // Should work again
      await expect(
        mrvRegistry.connect(user).createProject("UNPAUSED_TEST", "Test", "Description")
      ).to.not.be.reverted;
    });
  });
});