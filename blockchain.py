import hashlib
import json
import time
import uuid
from typing import List, Dict, Any, Optional


class Transaction:
    def __init__(self, text: str, tx_type: str = "TX", tx_id: str = None, 
                 replaces: str = None, origin_node: str = None):
        self.id = tx_id or str(uuid.uuid4())
        self.type = tx_type  # TX, UPDATE, ROOT
        self.text = text
        self.timestamp = int(time.time())
        self.replaces = replaces
        self.origin_node = origin_node or "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "text": self.text,
            "timestamp": self.timestamp,
            "replaces": self.replaces,
            "origin_node": self.origin_node
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        return cls(
            text=data["text"],
            tx_type=data["type"],
            tx_id=data["id"],
            replaces=data.get("replaces"),
            origin_node=data.get("origin_node")
        )


class Block:
    def __init__(self, index: int, transactions: List[Transaction], 
                 proof: int, previous_hash: str):
        self.index = index
        self.timestamp = int(time.time())
        self.transactions = transactions
        self.proof = proof
        self.previous_hash = previous_hash
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "proof": self.proof,
            "previous_hash": self.previous_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        transactions = [Transaction.from_dict(tx) for tx in data["transactions"]]
        return cls(
            index=data["index"],
            transactions=transactions,
            proof=data["proof"],
            previous_hash=data["previous_hash"]
        )
    
    def compute_hash(self) -> str:
        block_string = json.dumps(self.to_dict(), sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


class Blockchain:
    def __init__(self, node_id: str = None):
        self.chain: List[Block] = []
        self.mempool: List[Transaction] = []
        self.node_id = node_id or "unknown"
        self.create_genesis_block()
    
    def create_genesis_block(self):
        root_tx = Transaction(
            text="ROOT: rede inicializada",
            tx_type="ROOT",
            tx_id="root",
            origin_node=self.node_id
        )
        genesis_block = Block(
            index=1,
            transactions=[root_tx],
            proof=100,
            previous_hash="0"
        )
        self.chain.append(genesis_block)
    
    def get_last_block(self) -> Block:
        return self.chain[-1] if self.chain else None
    
    def add_transaction(self, text: str, tx_type: str = "TX", 
                       replaces: str = None) -> Transaction:
        transaction = Transaction(
            text=text,
            tx_type=tx_type,
            replaces=replaces,
            origin_node=self.node_id
        )
        self.mempool.append(transaction)
        return transaction
    
    def get_transaction_by_id(self, tx_id: str) -> Optional[Transaction]:
        # Search in mempool first
        for tx in self.mempool:
            if tx.id == tx_id:
                return tx
        
        # Search in chain
        for block in self.chain:
            for tx in block.transactions:
                if tx.id == tx_id:
                    return tx
        return None
    
    def update_transaction(self, tx_id: str, new_text: str) -> Optional[Transaction]:
        tx = self.get_transaction_by_id(tx_id)
        if not tx:
            return None
        
        # If transaction is still in mempool, update it directly
        if tx in self.mempool:
            tx.text = new_text
            return tx
        
        # If transaction is already mined, create UPDATE transaction
        update_tx = self.add_transaction(
            text=new_text,
            tx_type="UPDATE",
            replaces=tx_id
        )
        return update_tx
    
    def proof_of_work(self, last_proof: int) -> int:
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof
    
    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
    
    def mine_block(self) -> Optional[Block]:
        if not self.mempool:
            return None
        
        last_block = self.get_last_block()
        last_proof = last_block.proof
        proof = self.proof_of_work(last_proof)
        
        # Create new block with transactions from mempool
        new_block = Block(
            index=len(self.chain) + 1,
            transactions=self.mempool.copy(),
            proof=proof,
            previous_hash=last_block.compute_hash()
        )
        
        # Clear mempool and add block to chain
        self.mempool.clear()
        self.chain.append(new_block)
        
        return new_block
    
    def is_chain_valid(self, chain: List[Block] = None) -> bool:
        if chain is None:
            chain = self.chain
        
        # Check if chain has at least genesis block
        if len(chain) == 0:
            return False
        
        # Check genesis block
        genesis = chain[0]
        if genesis.index != 1 or genesis.previous_hash != "0":
            return False
        
        # Check if genesis has ROOT transaction
        if len(genesis.transactions) != 1 or genesis.transactions[0].type != "ROOT":
            return False
        
        # Check all blocks
        for i in range(1, len(chain)):
            current_block = chain[i]
            previous_block = chain[i - 1]
            
            # Check previous_hash
            if current_block.previous_hash != previous_block.compute_hash():
                return False
            
            # Check proof of work
            if not self.valid_proof(previous_block.proof, current_block.proof):
                return False
        
        return True
    
    def get_all_transactions(self) -> List[Transaction]:
        all_tx = []
        
        # Add transactions from chain
        for block in self.chain:
            all_tx.extend(block.transactions)
        
        # Add pending transactions
        all_tx.extend(self.mempool)
        
        return all_tx
    
    def replace_chain(self, new_chain: List[Block]) -> bool:
        if len(new_chain) <= len(self.chain):
            return False
        
        if not self.is_chain_valid(new_chain):
            return False
        
        self.chain = new_chain
        return True
    
    def get_chain_fingerprint(self) -> str:
        if not self.chain:
            return "empty"
        
        last_block = self.get_last_block()
        return f"{len(self.chain)}:{last_block.compute_hash()}"
