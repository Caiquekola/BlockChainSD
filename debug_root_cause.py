import requests
import json
import hashlib
from blockchain import Blockchain, Block, Transaction

def debug_root_cause():
    print("=== DEBUG RAIZ DO PROBLEMA ===")
    
    # 1. Verificar se todos os nós estão online
    print("\n1. VERIFICANDO NÓS ONLINE:")
    nodes_status = {}
    for port, name in [(5000, "A"), (5001, "B"), (5002, "C")]:
        try:
            response = requests.get(f'http://127.0.0.1:{port}/chain', timeout=3)
            if response.status_code == 200:
                data = response.json()
                nodes_status[port] = {
                    'name': name,
                    'online': True,
                    'blocks': data['length'],
                    'chain_data': data['chain']
                }
                print(f"   ✅ Node {name} ({port}): {data['length']} blocos")
            else:
                print(f"   ❌ Node {name} ({port}): ERRO {response.status_code}")
                nodes_status[port] = {'name': name, 'online': False}
        except Exception as e:
            print(f"   ❌ Node {name} ({port}): OFFLINE - {e}")
            nodes_status[port] = {'name': name, 'online': False}
    
    if len([n for n in nodes_status.values() if n['online']]) < 2:
        print("❌ Menos de 2 nós online")
        return
    
    # 2. Criar blockchain do zero para comparação
    print("\n2. CRIANDO BLOCKCHAIN DO ZERO:")
    clean_blockchain = Blockchain('test')
    print(f"   Genesis hash: {clean_blockchain.chain[0].compute_hash()}")
    
    # 3. Comparar genesis blocks
    print("\n3. COMPARANDO GENESIS BLOCKS:")
    genesis_hashes = {}
    for port, node_info in nodes_status.items():
        if node_info['online']:
            try:
                genesis_block = Block.from_dict(node_info['chain_data'][0])
                genesis_hash = genesis_block.compute_hash()
                genesis_hashes[port] = genesis_hash
                print(f"   Node {node_info['name']} ({port}): {genesis_hash}")
                
                # Verificar detalhes do genesis
                print(f"     Index: {genesis_block.index}")
                print(f"     Previous Hash: {genesis_block.previous_hash}")
                print(f"     Proof: {genesis_block.proof}")
                print(f"     Timestamp: {genesis_block.timestamp}")
                print(f"     Transactions: {len(genesis_block.transactions)}")
                
                if genesis_block.transactions:
                    tx = genesis_block.transactions[0]
                    print(f"     TX Type: {tx.type}")
                    print(f"     TX Text: {tx.text}")
                    print(f"     TX Origin: {tx.origin_node}")
                    print(f"     TX ID: {tx.id}")
                    
                    # Verificar se a transação está correta
                    expected_tx = Transaction(
                        text="ROOT: rede inicializada",
                        tx_type="ROOT",
                        tx_id="root",
                        origin_node="genesis"
                    )
                    
                    print(f"     TX esperada: {expected_tx.to_dict()}")
                    print(f"     TX recebida: {tx.to_dict()}")
                    print(f"     TX iguais: {tx.to_dict() == expected_tx.to_dict()}")
                    
                    # Verificar hash da transação
                    tx_hash = json.dumps(tx.to_dict(), sort_keys=True).encode()
                    tx_hash_calculated = hashlib.sha256(tx_hash).hexdigest()
                    print(f"     TX hash: {tx_hash_calculated}")
                    
            except Exception as e:
                print(f"   ❌ Erro ao processar genesis do Node {node_info['name']}: {e}")
    
    # 4. Verificar se genesis blocks são iguais
    print("\n4. VERIFICANDO SE GENESIS BLOCKS SÃO IGUAIS:")
    genesis_hash_values = list(genesis_hashes.values())
    if len(set(genesis_hash_values)) == 1:
        print("   ✅ Todos os genesis blocks são IDÊNTICOS!")
    else:
        print("   ❌ Genesis blocks são DIFERENTES!")
        print("   Este é o problema raiz!")
        
        # Mostrar diferenças
        for port, hash_val in genesis_hashes.items():
            name = nodes_status[port]['name']
            print(f"   Node {name} ({port}): {hash_val}")
    
    # 5. Testar criação de bloco manualmente
    print("\n5. TESTANDO CRIAÇÃO DE BLOCO MANUALMENTE:")
    
    # Criar bloco manualmente
    test_tx = Transaction("TEST MANUAL", "TX")
    manual_block = Block(
        index=2,
        transactions=[test_tx],
        proof=100,  # Proof fixo
        previous_hash=clean_blockchain.chain[0].compute_hash()
    )
    
    manual_hash = manual_block.compute_hash()
    print(f"   Bloco manual hash: {manual_hash}")
    print(f"   Previous hash: {manual_block.previous_hash}")
    print(f"   Previous hash correto: {manual_block.previous_hash == clean_blockchain.chain[0].compute_hash()}")
    
    # 6. Testar serialização/desserialização
    print("\n6. TESTANDO SERIALIZAÇÃO/DESSERIALIZAÇÃO:")
    
    block_dict = manual_block.to_dict()
    print(f"   Block dict: {json.dumps(block_dict, sort_keys=True)}")
    
    deserialized_block = Block.from_dict(block_dict)
    deserialized_hash = deserialized_block.compute_hash()
    
    print(f"   Desserialized hash: {deserialized_hash}")
    print(f"   Hashes iguais: {manual_hash == deserialized_hash}")
    
    if manual_hash != deserialized_hash:
        print("   ❌ PROBLEMA NA SERIALIZAÇÃO!")
        print("   Este é o bug real!")
        
        # Verificar diferenças
        print(f"   Original timestamp: {manual_block.timestamp}")
        print(f"   Desserialized timestamp: {deserialized_block.timestamp}")
        print(f"   Timestamps iguais: {manual_block.timestamp == deserialized_block.timestamp}")
    
    # 7. Testar validação
    print("\n7. TESTANDO VALIDAÇÃO:")
    
    test_chain = [clean_blockchain.chain[0], manual_block]
    is_valid = clean_blockchain.is_chain_valid(test_chain)
    print(f"   Chain manual válida: {'✅ SIM' if is_valid else '❌ NÃO'}")
    
    if not is_valid:
        print("   Detalhes da invalidação:")
        for i in range(1, len(test_chain)):
            current = test_chain[i]
            previous = test_chain[i-1]
            
            expected_hash = previous.compute_hash()
            actual_hash = current.previous_hash
            
            print(f"     Bloco {i+1}:")
            print(f"       Hash anterior esperado: {expected_hash}")
            print(f"       Hash anterior recebido: {actual_hash}")
            print(f"       Correto: {actual_hash == expected_hash}")
    
    # 8. Comparar com nós existentes
    print("\n8. COMPARANDO COM NÓS EXISTENTES:")
    
    for port, node_info in nodes_status.items():
        if node_info['online'] and len(node_info['chain_data']) > 1:
            try:
                block_2 = Block.from_dict(node_info['chain_data'][1])
                node_hash = block_2.compute_hash()
                
                print(f"   Node {node_info['name']} ({port}) Bloco 2:")
                print(f"     Hash: {node_hash}")
                print(f"     Previous hash: {block_2.previous_hash}")
                print(f"     Previous hash correto: {block_2.previous_hash == clean_blockchain.chain[0].compute_hash()}")
                
                # Validar chain do nó
                node_blocks = [Block.from_dict(b) for b in node_info['chain_data']]
                node_valid = clean_blockchain.is_chain_valid(node_blocks)
                print(f"     Chain válida: {'✅ SIM' if node_valid else '❌ NÃO'}")
                
            except Exception as e:
                print(f"   ❌ Erro ao analisar Node {node_info['name']}: {e}")

if __name__ == "__main__":
    debug_root_cause()
