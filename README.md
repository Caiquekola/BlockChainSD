# BlockChainSD - Trabalho de Sistemas Distribuídos

Implementação de uma blockchain didática com 3 nós para o trabalho de Sistemas Distribuídos.

## Características

- **3 nós** comunicando via HTTP (portas 5000, 5001, 5002)
- **CRUD de transações** com texto livre
- **Prova de Trabalho (PoW)** com 4 zeros
- **Consenso por maioria** (50% + 1 = 2 votos)
- **Automação**: mineração e consenso periódicos
- **Simulação de falhas**: PARADA e BIZANTINA
- **Interface web** para demonstração

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Execução

### Iniciar os 3 nós automaticamente (Windows):
```bash
start_nodes.bat
```

### Iniciar manualmente:

**Terminal 1:**
```bash
python run_node.py 5000 NodeA
```

**Terminal 2:**
```bash
python run_node.py 5001 NodeB
```

**Terminal 3:**
```bash
python run_node.py 5002 NodeC
```

## Interface Web

Acesse os nós no navegador:
- Node A: http://localhost:5000
- Node B: http://localhost:5001
- Node C: http://localhost:5002

## API REST

### Blockchain e Mineração
- `GET /chain` - Retorna a blockchain completa
- `GET /mine` - Minera um novo bloco

### Transações (CRUD)
- `POST /transactions/new` - Cria nova transação
  ```json
  {"text": "minha transação"}
  ```
- `GET /transactions/pending` - Lista transações pendentes
- `GET /transactions/all` - Lista todas as transações
- `PUT /transactions/<tx_id>` - Atualiza transação
  ```json
  {"text": "novo texto"}
  ```

### Rede P2P
- `POST /nodes/register` - Registra nós
  ```json
  {"nodes": ["127.0.0.1:5001", "127.0.0.1:5002"]}
  ```
- `GET /nodes` - Lista nós conhecidos
- `GET /nodes/resolve` - Executa consenso

### Simulação de Falhas
- `POST /faults` - Define modo de falha
  ```json
  {"mode": "NORMAL|STOP|BYZANTINE"}
  ```

## Roteiro de Demonstração

1. **Iniciar os nós**: Execute os 3 nós
2. **Verificar Genesis**: Todos devem ter o bloco genesis com transação ROOT
3. **Registrar peers**: Use a interface web para registrar os outros nós
4. **Criar transação**: Adicione uma transação em qualquer nó
5. **Mineração automática**: Aguarde 10 segundos para mineração automática
6. **Consenso automático**: Aguarde 30 segundos para sincronização
7. **Simular falha STOP**: Ative modo STOP em um nó e verifique continuidade
8. **Simular falha BIZANTINA**: Ative modo BYZANTINE e veja a validação
9. **Testar UPDATE**: Atualize transações pendentes e mineradas

## Estrutura do Projeto

```
BlockChainSD/
├── blockchain.py          # Classes principais (Block, Transaction, Blockchain)
├── node.py               # Node Flask com API e backend
├── run_node.py           # Script para iniciar um nó individual
├── start_nodes.bat       # Script para iniciar os 3 nós (Windows)
├── requirements.txt      # Dependências Python
├── templates/
│   └── index.html       # Frontend moderno com TailwindCSS
├── static/
│   └── styles.css       # Estilos customizados
└── README.md            # Este arquivo
```

## Tecnologias

- **Python 3.x**
- **Flask** - API REST e backend
- **TailwindCSS** - Framework CSS moderno para frontend
- **Font Awesome** - Ícones profissionais
- **Requests** - Comunicação HTTP entre nós
- **Threading** - Automação em background
- **Hashlib** - Prova de trabalho

## Critérios de Aceite

- [x] 3 nós rodando e comunicando via HTTP
- [x] CRUD de transações funcionando
- [x] `/chain` retorna blockchain completo em JSON
- [x] Consenso 50%+1 implementado e automático
- [x] Nó mais confiável como desempate
- [x] Transação ROOT sincronizada
- [x] PoW com 4 zeros funcionando
- [x] UI simples para todas as rotas
- [x] Simulação de falhas STOP e BYZANTINA
