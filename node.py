from flask import Flask, request, jsonify, render_template
import requests
import threading
import time
import os
from blockchain import Blockchain, Block, Transaction
from typing import Dict, List, Set, Optional


class Node:
    def __init__(self, port: int, node_id: str, peers: List[str] = None):
        self.app = Flask(__name__)
        self.port = port
        self.node_id = node_id
        self.blockchain = Blockchain(node_id)
        self.peers: Set[str] = set(peers or [])
        self.reliability_scores: Dict[str, Dict[str, int]] = {}
        self.fault_mode = "NORMAL"  # NORMAL, STOP, BYZANTINE
        
        # Initialize reliability scores for peers
        for peer in self.peers:
            self.reliability_scores[peer] = {"ok_count": 0, "fail_count": 0}
        
        self.setup_routes()
        self.start_background_tasks()
    
    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html', node_id=self.node_id, port=self.port)
        
        @self.app.route('/chain')
        def get_chain():
            if self.fault_mode == "STOP":
                return jsonify({"error": "Node stopped"}), 503
            
            if self.fault_mode == "BYZANTINE":
                # Return corrupted chain
                corrupted_chain = [block.to_dict() for block in self.blockchain.chain]
                if len(corrupted_chain) > 1:
                    corrupted_chain[1]["previous_hash"] = "corrupted_hash"
                return jsonify({
                    "chain": corrupted_chain,
                    "length": len(corrupted_chain)
                })
            
            return jsonify({
                "chain": [block.to_dict() for block in self.blockchain.chain],
                "length": len(self.blockchain.chain)
            })
        
        @self.app.route('/mine')
        def mine():
            if self.fault_mode == "STOP":
                return jsonify({"error": "Node stopped"}), 503
            
            block = self.blockchain.mine_block()
            if block:
                return jsonify({
                    "message": "New Block Forged",
                    "index": block.index,
                    "transactions": [tx.to_dict() for tx in block.transactions],
                    "proof": block.proof,
                    "previous_hash": block.previous_hash
                })
            else:
                return jsonify({"message": "No transactions to mine"})
        
        @self.app.route('/transactions/new', methods=['POST'])
        def new_transaction():
            if self.fault_mode == "STOP":
                return jsonify({"error": "Node stopped"}), 503
            
            values = request.get_json()
            if not values or 'text' not in values:
                return jsonify({"error": "Missing text field"}), 400
            
            text = values['text']
            transaction = self.blockchain.add_transaction(text)
            
            return jsonify({
                "message": "Transaction added to mempool",
                "tx_id": transaction.id
            }), 201
        
        @self.app.route('/transactions/pending')
        def get_pending_transactions():
            if self.fault_mode == "STOP":
                return jsonify({"error": "Node stopped"}), 503
            
            return jsonify({
                "transactions": [tx.to_dict() for tx in self.blockchain.mempool],
                "count": len(self.blockchain.mempool)
            })
        
        @self.app.route('/transactions/all')
        def get_all_transactions():
            if self.fault_mode == "STOP":
                return jsonify({"error": "Node stopped"}), 503
            
            all_tx = self.blockchain.get_all_transactions()
            return jsonify({
                "transactions": [tx.to_dict() for tx in all_tx],
                "count": len(all_tx)
            })
        
        @self.app.route('/transactions/<tx_id>', methods=['PUT'])
        def update_transaction(tx_id):
            if self.fault_mode == "STOP":
                return jsonify({"error": "Node stopped"}), 503
            
            values = request.get_json()
            if not values or 'text' not in values:
                return jsonify({"error": "Missing text field"}), 400
            
            new_text = values['text']
            updated_tx = self.blockchain.update_transaction(tx_id, new_text)
            
            if updated_tx:
                return jsonify({
                    "message": "Transaction updated",
                    "transaction": updated_tx.to_dict()
                })
            else:
                return jsonify({"error": "Transaction not found"}), 404
        
        @self.app.route('/nodes/register', methods=['POST'])
        def register_nodes():
            if self.fault_mode == "STOP":
                return jsonify({"error": "Node stopped"}), 503
            
            values = request.get_json()
            if not values or 'nodes' not in values:
                return jsonify({"error": "Missing nodes field"}), 400
            
            nodes = values['nodes']
            for node in nodes:
                if node not in self.peers:
                    self.peers.add(node)
                    self.reliability_scores[node] = {"ok_count": 0, "fail_count": 0}
            
            return jsonify({
                "message": "New nodes have been added",
                "total_nodes": list(self.peers)
            }), 201
        
        @self.app.route('/nodes')
        def get_nodes():
            if self.fault_mode == "STOP":
                return jsonify({"error": "Node stopped"}), 503
            
            return jsonify({
                "nodes": list(self.peers),
                "reliability_scores": self.reliability_scores
            })
        
        @self.app.route('/nodes/resolve')
        def resolve_conflicts():
            if self.fault_mode == "STOP":
                return jsonify({"error": "Node stopped"}), 503
            
            replaced = self.resolve_conflicts_internal()
            
            if replaced:
                return jsonify({
                    "message": "Our chain was replaced",
                    "new_chain": [block.to_dict() for block in self.blockchain.chain]
                })
            else:
                return jsonify({
                    "message": "Our chain is authoritative",
                    "chain": [block.to_dict() for block in self.blockchain.chain]
                })
        
        @self.app.route('/faults', methods=['POST'])
        def set_fault_mode():
            values = request.get_json()
            if not values or 'mode' not in values:
                return jsonify({"error": "Missing mode field"}), 400
            
            mode = values['mode']
            if mode not in ["NORMAL", "STOP", "BYZANTINE"]:
                return jsonify({"error": "Invalid mode"}), 400
            
            self.fault_mode = mode
            return jsonify({"message": f"Fault mode set to {mode}"})
    
    def resolve_conflicts_internal(self) -> bool:
        # Collect chains from all peers
        peer_chains = {}
        peer_fingerprints = {}
        
        for peer in self.peers:
            try:
                response = requests.get(f'http://{peer}/chain', timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    chain_data = data['chain']
                    
                    # Convert to Block objects
                    chain = []
                    for block_data in chain_data:
                        block = Block.from_dict(block_data)
                        chain.append(block)
                    
                    # Validate chain
                    if self.blockchain.is_chain_valid(chain):
                        peer_chains[peer] = chain
                        fingerprint = f"{len(chain)}:{chain[-1].compute_hash()}"
                        peer_fingerprints[peer] = fingerprint
                        
                        # Update reliability score
                        self.reliability_scores[peer]["ok_count"] += 1
                    else:
                        # Invalid chain
                        self.reliability_scores[peer]["fail_count"] += 1
                else:
                    self.reliability_scores[peer]["fail_count"] += 1
                    
            except Exception:
                self.reliability_scores[peer]["fail_count"] += 1
        
        # Count votes for each fingerprint
        fingerprint_votes = {}
        for peer, fingerprint in peer_fingerprints.items():
            if fingerprint not in fingerprint_votes:
                fingerprint_votes[fingerprint] = []
            fingerprint_votes[fingerprint].append(peer)
        
        # Find majority (50% + 1 = 2 votes for 3 nodes)
        majority_threshold = 2
        winning_fingerprint = None
        winning_peers = []
        
        for fingerprint, voters in fingerprint_votes.items():
            if len(voters) >= majority_threshold:
                winning_fingerprint = fingerprint
                winning_peers = voters
                break
        
        if winning_fingerprint:
            # Use majority chain
            peer = winning_peers[0]
            new_chain = peer_chains[peer]
            return self.blockchain.replace_chain(new_chain)
        
        # No majority - choose longest valid chain
        if peer_chains:
            longest_chain = max(peer_chains.values(), key=len)
            
            # If multiple chains have same length, choose from most reliable peer
            same_length_chains = [chain for chain in peer_chains.values() if len(chain) == len(longest_chain)]
            if len(same_length_chains) > 1:
                # Find most reliable peer
                most_reliable_peer = min(
                    peer_chains.keys(),
                    key=lambda p: self.reliability_scores[p]["fail_count"]
                )
                longest_chain = peer_chains[most_reliable_peer]
            
            return self.blockchain.replace_chain(longest_chain)
        
        return False
    
    def auto_register_peers(self):
        # Auto-register peers from environment or config
        peer_env = os.getenv('PEERS', '')
        if peer_env:
            peers = [p.strip() for p in peer_env.split(',') if p.strip()]
            for peer in peers:
                if peer not in self.peers:
                    self.peers.add(peer)
                    self.reliability_scores[peer] = {"ok_count": 0, "fail_count": 0}
    
    def auto_mine(self):
        while True:
            time.sleep(10)  # Mine every 10 seconds
            if self.fault_mode != "STOP" and self.blockchain.mempool:
                try:
                    self.blockchain.mine_block()
                except Exception:
                    pass
    
    def auto_consensus(self):
        while True:
            time.sleep(30)  # Run consensus every 30 seconds
            if self.fault_mode != "STOP":
                try:
                    self.resolve_conflicts_internal()
                except Exception:
                    pass
    
    def start_background_tasks(self):
        # Start auto-mine thread
        auto_mine_thread = threading.Thread(target=self.auto_mine, daemon=True)
        auto_mine_thread.start()
        
        # Start auto-consensus thread
        auto_consensus_thread = threading.Thread(target=self.auto_consensus, daemon=True)
        auto_consensus_thread.start()
    
    def run(self):
        self.auto_register_peers()
        self.app.run(host='0.0.0.0', port=self.port, debug=False)
