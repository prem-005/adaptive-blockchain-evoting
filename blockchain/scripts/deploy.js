const hre = require("hardhat");

async function main() {
  console.log("Deploying Voting System contract...");

  const VotingSystem = await hre.ethers.getContractFactory("VotingSystem");
  const votingSystem = await VotingSystem.deploy();

  await votingSystem.deployed();

  console.log("VotingSystem deployed to:", votingSystem.address);
  console.log("\n📋 Update your backend .env with:");
  console.log(`VOTING_CONTRACT_ADDRESS=${votingSystem.address}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
