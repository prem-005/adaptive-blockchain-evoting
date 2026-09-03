"""Web3.py Client for Blockchain Integration"""

from web3 import Web3
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class Web3Client:
    """Web3 client for blockchain interactions"""
    
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_RPC_URL))
        self.account = self.w3.eth.account.from_key(settings.BLOCKCHAIN_PRIVATE_KEY)
        
        if not self.w3.is_connected():
            logger.error("Failed to connect to blockchain")
            raise ConnectionError("Cannot connect to blockchain")
        
        logger.info(f"Connected to blockchain: {self.w3.eth.chain_id}")
        logger.info(f"Account: {self.account.address}")
    
    def get_balance(self) -> float:
        """Get account balance in ETH"""
        balance = self.w3.eth.get_balance(self.account.address)
        return self.w3.from_wei(balance, 'ether')
    
    def send_transaction(self, transaction):
        """Send a transaction"""
        try:
            tx_hash = self.w3.eth.send_raw_transaction(
                self.w3.eth.account.sign_transaction(transaction, self.account.key).rawTransaction
            )
            return tx_hash
        except Exception as e:
            logger.error(f"Error sending transaction: {e}")
            raise
    
    def wait_for_receipt(self, tx_hash, timeout=120):
        """Wait for transaction receipt"""
        try:
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            return receipt
        except Exception as e:
            logger.error(f"Error waiting for receipt: {e}")
            raise

# Global instance
web3_client = Web3Client()
