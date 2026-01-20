import sys
from node import Node

def main():
    if len(sys.argv) != 3:
        print("Usage: python run_node.py <port> <node_id>")
        sys.exit(1)
    
    port = int(sys.argv[1])
    node_id = sys.argv[2]
    
    # Default peers for the other two nodes
    default_peers = []
    if port != 5000:
        default_peers.append("127.0.0.1:5000")
    if port != 5001:
        default_peers.append("127.0.0.1:5001")
    if port != 5002:
        default_peers.append("127.0.0.1:5002")
    
    node = Node(port, node_id, default_peers)
    print(f"Starting node {node_id} on port {port}")
    node.run()

if __name__ == "__main__":
    main()
