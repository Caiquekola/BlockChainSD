# Guia de Apresentação - BlockChainSD

## 📋 Roteiro Completo para Apresentação ao Professor

### 🎯 Objetivo da Apresentação
Demonstrar uma blockchain distribuída com 3 nós, consenso 50%+1, e simulação de falhas para o trabalho de Sistemas Distribuídos.

---

## 🚀 Passo 1 - Preparação (5 minutos)

### 1.1 Iniciar os Nós
```bash
# Abra 3 terminais ou execute o script
start_nodes.bat

# Ou manualmente:
# Terminal 1: python run_node.py 5000 NodeA
# Terminal 2: python run_node.py 5001 NodeB  
# Terminal 3: python run_node.py 5002 NodeC
```

### 1.2 Verificar Inicialização
- Abra os 3 navegadores:
  - Node A: http://localhost:5000
  - Node B: http://localhost:5001
  - Node C: http://localhost:5002

**Fale:** "Professor, iniciei os 3 nós da nossa blockchain. Cada nó está rodando em uma porta diferente (5000, 5001, 5002)."

---

## 🔗 Passo 2 - Configuração da Rede (3 minutos)

### 2.1 Registrar Nós
1. **No Node A (porta 5000):**
   - Vá em "Registrar Nós"
   - Digite:
     ```
     127.0.0.1:5001
     127.0.0.1:5002
     ```
   - Clique "Conectar Nós"

2. **Repita para os outros nós** (opcional, para rede completa)

### 2.2 Verificar Conexão
- Clique em "Nós" para ver os nós conectados
- Verifique se aparece 2 nós conectados

**Fale:** "Agora vou registrar os nós na rede P2P. Cada nó conhece os outros dois, formando uma rede totalmente conectada."

---

## 📝 Passo 3 - Transações e Mineração (5 minutos)

### 3.1 Criar Transação
1. **No Node A:**
   - Digite no campo "Nova Transação": "Primeira transação da rede"
   - Clique "Enviar"

2. **Verificar Transação Pendente:**
   - Clique "Pendentes" - deve aparecer a transação
   - **IMPORTANTE:** A transação aparece apenas no nó onde foi criada!

**Fale:** "Criei uma transação no nó A. Note que ela está apenas no mempool do nó A, ainda não foi minerada."

### 3.2 Mineração Automática
- **Aguarde 10 segundos** (mineração automática)
- Ou clique "Minerar" manualmente

### 3.3 Verificar Sincronização
1. **Após mineração:**
   - No Node A: Clique "Blockchain" - veja o novo bloco
   - Nos Nodes B e C: Clique "Blockchain" - deve estar vazio ainda

2. **Executar Consenso:**
   - Clique "Consenso" em qualquer nó
   - Aguarde 30 segundos (consenso automático) ou clique manualmente

3. **Verificar Sincronização Final:**
   - Todos os 3 nós devem ter o mesmo blockchain
   - A transação agora aparece em todos os nós

**Fale:** "Após minerar, o bloco foi criado no nó A. Agora vou executar o consenso para sincronizar a rede. Note que após o consenso, todos os nós têm a mesma blockchain."

---

## ⚡ Passo 4 - Consenso e Validação (4 minutos)

### 4.1 Demonstração do Consenso 50%+1
1. **Crie outra transação** no Node B
2. **Mine** no Node B
3. **Execute consenso** - mostre que a chain mais longa vence

**Fale:** "O consenso implementa democracia 50%+1. Com 3 nós, precisamos de 2 votos. A chain válida mais longa é escolhida."

### 4.2 Prova de Trabalho
- Mostre o hash começando com "0000"
- Explique: "Usamos Prova de Trabalho simplificada com 4 zeros para demonstração."

---

## 🚨 Passo 5 - Simulação de Falhas (5 minutos)

### 5.1 Falha STOP (Nó Parado)
1. **No Node C:**
   - Vá em "Simulação de Falhas"
   - Clique "Parar (STOP)"

2. **Teste Resiliência:**
   - Crie transação no Node A
   - Mine e execute consenso
   - **Resultado:** Sistema continua funcionando com 2 nós

**Fale:** "Vou simular uma falha de parada no nó C. Note que o sistema continua operando com os 2 nós restantes, demonstrando tolerância a falhas."

### 5.2 Falha BYZANTINA (Nó Malicioso)
1. **Restaure o Node C:** Clique "Normal"
2. **Ative BYZANTINE:** Clique "Bizantino (BYZANTINE)"
3. **Teste Validação:**
   - Tente executar consenso
   - Mostre que o nó bizantino é ignorado

**Fale:** "Agora simulo uma falha bizantina, onde o nó se comporta mal. O sistema detecta e ignora o nó malicioso através da validação."

---

## 🔄 Passo 6 - Operações CRUD (3 minutos)

### 6.1 UPDATE de Transação Pendente
1. **Crie uma transação:** "Texto original"
2. **Antes de minerar:** Atualize com "Texto modificado"
3. **Mostre:** A transação foi editada diretamente

### 6.2 UPDATE de Transação Minerada
1. **Crie e mine uma transação:** "Texto para atualizar"
2. **Depois de minerada:** Crie UPDATE com "Novo texto"
3. **Mostre:** Foi criada uma nova transação tipo UPDATE

**Fale:** "Demonstro as operações CRUD. Transações pendentes podem ser editadas, mas mineradas requerem novas transações UPDATE para manter a integridade."

---

## 📊 Passo 7 - Status e Monitoramento (2 minutos)

### 7.1 Painel de Status
- Mostre o "Status da Rede" em tempo real
- Nós conectados, blocos, transações pendentes

### 7.2 Interface Visual
- Mostre o carrossel de blocos
- Navegue entre os blocos
- Explique as informações de cada bloco

**Fale:** "A interface oferece monitoramento em tempo real e visualização interativa da blockchain."

---

## ❓ Perguntas Frequentes e Respostas

### P: "Por que a transação não aparece nos outros nós imediatamente?"
R: "Isso está correto! Transações ficam no mempool local até serem mineradas. O consenso sincroniza apenas blocos minerados, não transações pendentes."

### P: "Como funciona o consenso exatamente?"
R: "Cada nó consulta os outros, valida as chains recebidas, e vota. Com 3 nós, 2 votos formam maioria (50%+1)."

### P: "O que acontece em caso de empate?"
R: "Usamos critérios de desempate: chain mais longa primeiro, depois nó mais confiável (menos falhas)."

---

## 🎯 Pontos-Chave para Destacar

1. **Distribuição:** 3 nós independentes comunicando via HTTP
2. **Consenso:** Democracia 50%+1 com validação
3. **Tolerância a Falhas:** Sistema funciona com falhas
4. **Integridade:** Imutabilidade com UPDATE em vez de edição
5. **Prova de Trabalho:** Hash com 4 zeros como demonstração
6. **Interface:** Monitoramento em tempo real

---

## ⏱️ Tempo Total Estimado: 25-30 minutos

**Dica Final:** Tenha os navegadores abertos lado a lado para mostrar sincronização em tempo real. Pratique uma vez antes da apresentação!

---

## 🔧 Solução de Problemas

### Se um nó não iniciar:
- Verifique se a porta está livre
- Use `netstat -ano | findstr :5000` no Windows

### Se o consenso não funcionar:
- Verifique se todos os nós estão registrados
- Confirme que não há modo de falha ativo

### Se a interface não carregar:
- Verifique se o Flask está instalado
- Recarregue a página (F5)

---

## 📝 Resumo Técnico

- **Arquitetura:** 3 nós P2P via HTTP
- **Consenso:** Maioria simples (50%+1)
- **Persistência:** Em memória (para demonstração)
- **Prova de Trabalho:** SHA256 com 4 zeros
- **Falhas:** STOP e BYZANTINE simuladas
- **CRUD:** Create, Read, Update (com regras específicas)

Boa apresentação! 🚀
