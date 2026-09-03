// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * Adaptive Risk-Aware Blockchain-Based E-Voting System
 * Smart Contract for Vote Recording and Election Management
 */

contract VotingSystem {
    
    // ============================================================================
    // DATA STRUCTURES
    // ============================================================================
    
    struct Election {
        uint256 id;
        string title;
        uint256 startTime;
        uint256 endTime;
        bool active;
        bool closed;
        address creator;
    }
    
    struct Candidate {
        uint256 id;
        uint256 electionId;
        string name;
        uint256 voteCount;
    }
    
    struct Vote {
        uint256 id;
        uint256 electionId;
        uint256 candidateId;
        bytes32 voterCommitment; // Anonymous voter hash
        uint256 timestamp;
    }
    
    // ============================================================================
    // STATE VARIABLES
    // ============================================================================
    
    mapping(uint256 => Election) public elections;
    mapping(uint256 => Candidate) public candidates;
    mapping(uint256 => Vote) public votes;
    mapping(uint256 => mapping(bytes32 => bool)) public hasVoted; // election => voter => voted
    mapping(uint256 => uint256[]) public electionCandidates; // election => candidate IDs
    mapping(uint256 => uint256[]) public electionVotes; // election => vote IDs
    mapping(uint256 => mapping(uint256 => uint256)) public candidateVoteCount; // election => candidate => count
    
    uint256 public electionCounter = 0;
    uint256 public candidateCounter = 0;
    uint256 public voteCounter = 0;
    
    address public admin;
    
    // ============================================================================
    // EVENTS
    // ============================================================================
    
    event ElectionCreated(
        uint256 indexed electionId,
        string title,
        uint256 startTime,
        uint256 endTime
    );
    
    event CandidateAdded(
        uint256 indexed electionId,
        uint256 indexed candidateId,
        string name
    );
    
    event VoterAuthorized(
        uint256 indexed electionId,
        bytes32 voterCommitment
    );
    
    event VoteRecorded(
        uint256 indexed electionId,
        uint256 indexed candidateId,
        bytes32 indexed voterCommitment,
        uint256 timestamp
    );
    
    event ElectionClosed(
        uint256 indexed electionId
    );
    
    event DuplicateVoteAttempt(
        uint256 indexed electionId,
        bytes32 voterCommitment,
        uint256 timestamp
    );
    
    // ============================================================================
    // MODIFIERS
    // ============================================================================
    
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }
    
    modifier electionExists(uint256 _electionId) {
        require(_electionId <= electionCounter, "Election does not exist");
        _;
    }
    
    modifier electionActive(uint256 _electionId) {
        require(elections[_electionId].active, "Election is not active");
        require(!elections[_electionId].closed, "Election is closed");
        require(block.timestamp >= elections[_electionId].startTime, "Election has not started");
        require(block.timestamp <= elections[_electionId].endTime, "Election has ended");
        _;
    }
    
    // ============================================================================
    // CONSTRUCTOR
    // ============================================================================
    
    constructor() {
        admin = msg.sender;
    }
    
    // ============================================================================
    // ELECTION MANAGEMENT
    // ============================================================================
    
    function createElection(
        string memory _title,
        uint256 _startTime,
        uint256 _endTime
    ) public onlyAdmin returns (uint256) {
        require(_endTime > _startTime, "End time must be after start time");
        
        electionCounter++;
        uint256 electionId = electionCounter;
        
        elections[electionId] = Election({
            id: electionId,
            title: _title,
            startTime: _startTime,
            endTime: _endTime,
            active: false,
            closed: false,
            creator: msg.sender
        });
        
        emit ElectionCreated(electionId, _title, _startTime, _endTime);
        return electionId;
    }
    
    function activateElection(uint256 _electionId) public onlyAdmin electionExists(_electionId) {
        require(!elections[_electionId].active, "Election is already active");
        elections[_electionId].active = true;
    }
    
    function closeElection(uint256 _electionId) public onlyAdmin electionExists(_electionId) {
        require(elections[_electionId].active, "Election is not active");
        elections[_electionId].closed = true;
        emit ElectionClosed(_electionId);
    }
    
    function getElectionStatus(uint256 _electionId) public view electionExists(_electionId) returns (string memory) {
        Election storage election = elections[_electionId];
        if (election.closed) return "closed";
        if (!election.active) return "inactive";
        if (block.timestamp < election.startTime) return "upcoming";
        if (block.timestamp <= election.endTime) return "active";
        return "ended";
    }
    
    // ============================================================================
    // CANDIDATE MANAGEMENT
    // ============================================================================
    
    function addCandidate(
        uint256 _electionId,
        string memory _name
    ) public onlyAdmin electionExists(_electionId) returns (uint256) {
        require(!elections[_electionId].active, "Cannot add candidates to active election");
        
        candidateCounter++;
        uint256 candidateId = candidateCounter;
        
        candidates[candidateId] = Candidate({
            id: candidateId,
            electionId: _electionId,
            name: _name,
            voteCount: 0
        });
        
        electionCandidates[_electionId].push(candidateId);
        
        emit CandidateAdded(_electionId, candidateId, _name);
        return candidateId;
    }
    
    function getCandidates(uint256 _electionId) public view electionExists(_electionId) returns (uint256[] memory) {
        return electionCandidates[_electionId];
    }
    
    // ============================================================================
    // VOTER AUTHORIZATION
    // ============================================================================
    
    function authorizeVoter(
        uint256 _electionId,
        bytes32 _voterCommitment
    ) public onlyAdmin electionExists(_electionId) {
        emit VoterAuthorized(_electionId, _voterCommitment);
    }
    
    // ============================================================================
    // VOTING
    // ============================================================================
    
    function castVote(
        uint256 _electionId,
        uint256 _candidateId,
        bytes32 _voterCommitment
    ) public electionActive(_electionId) returns (bool) {
        // Check voter hasn't voted
        if (hasVoted[_electionId][_voterCommitment]) {
            emit DuplicateVoteAttempt(_electionId, _voterCommitment, block.timestamp);
            revert("Voter has already voted in this election");
        }
        
        // Check candidate exists and belongs to election
        require(
            candidates[_candidateId].electionId == _electionId,
            "Candidate does not belong to this election"
        );
        
        // Record vote
        voteCounter++;
        uint256 voteId = voteCounter;
        
        votes[voteId] = Vote({
            id: voteId,
            electionId: _electionId,
            candidateId: _candidateId,
            voterCommitment: _voterCommitment,
            timestamp: block.timestamp
        });
        
        hasVoted[_electionId][_voterCommitment] = true;
        electionVotes[_electionId].push(voteId);
        candidateVoteCount[_electionId][_candidateId]++;
        candidates[_candidateId].voteCount++;
        
        emit VoteRecorded(_electionId, _candidateId, _voterCommitment, block.timestamp);
        return true;
    }
    
    // ============================================================================
    // VOTE VERIFICATION
    // ============================================================================
    
    function hasVoterVoted(
        uint256 _electionId,
        bytes32 _voterCommitment
    ) public view electionExists(_electionId) returns (bool) {
        return hasVoted[_electionId][_voterCommitment];
    }
    
    function getVoteCount(
        uint256 _electionId,
        uint256 _candidateId
    ) public view electionExists(_electionId) returns (uint256) {
        return candidateVoteCount[_electionId][_candidateId];
    }
    
    function getTotalVotes(uint256 _electionId) public view electionExists(_electionId) returns (uint256) {
        return electionVotes[_electionId].length;
    }
    
    function getElectionVotes(uint256 _electionId) public view electionExists(_electionId) returns (uint256[] memory) {
        return electionVotes[_electionId];
    }
    
    function getVote(uint256 _voteId) public view returns (
        uint256 electionId,
        uint256 candidateId,
        bytes32 voterCommitment,
        uint256 timestamp
    ) {
        Vote storage vote = votes[_voteId];
        return (vote.electionId, vote.candidateId, vote.voterCommitment, vote.timestamp);
    }
    
    // ============================================================================
    // VERIFICATION AND AUDITING
    // ============================================================================
    
    function verifyVote(
        uint256 _voteId,
        uint256 _electionId,
        uint256 _candidateId,
        bytes32 _voterCommitment
    ) public view returns (bool) {
        Vote storage vote = votes[_voteId];
        return (
            vote.electionId == _electionId &&
            vote.candidateId == _candidateId &&
            vote.voterCommitment == _voterCommitment
        );
    }
}
