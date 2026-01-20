# Project Context — Sistemas Distribuídos: Blockchain (3 nós, CRUD, Consenso 50%+1)

Este projeto implementa uma **blockchain didática** com **3 nós** (processos/containers) que se comunicam via **HTTP**. Cada nó expõe uma **API pública** para criar/consultar/atualizar transações, minerar blocos (PoW com “4 zeros”), sincronizar a cadeia e rodar **consenso por maioria (50% + 1)**. Inclui também uma **interface web simples** e **simulação de falhas** (PARADA e BIZANTINA).

---

## 1) Objetivos do trabalho (o que precisa existir)

* **3 nós** executando o mesmo serviço em portas diferentes.
* **CRUD de transações** onde transação é um **JSON com um texto**.
* **Consulta de transações** (pendentes + registradas).
* **Blockchain completo em JSON**.
* **Nós conversando entre si** (P2P simples via HTTP).
* **Consenso 50% + 1** (com 3 nós = 2 votos).
* **Validação/consenso periódico** (automático).
* **Seleção do nó mais confiável** (menos falhas) como desempate.
* **Transação ROOT** antes de tudo (genesis sincronizado).
* **Prova de conceito PoW**: hash iniciando com **"0000"**.
* **Falhas**:

  * **PARADA** (nó não responde / erro)
  * **BIZANTINA** (nó se comporta de forma inesperada: responde com dados inválidos)

---

## 2) Visão geral da arquitetura

### Nós

* Nó A: `localhost:5000`
* Nó B: `localhost:5001`
* Nó C: `localhost:5002`

Cada nó possui:

* **chain**: lista de blocos
* **mempool**: lista de transações pendentes
* **peers**: lista de nós conhecidos (`host:port`)
* **reliability_score** por peer:

  * `ok_count`
  * `fail_count` (timeout, erro HTTP, chain inválida)

### Comunicação

* P2P via HTTP: cada nó consulta `/chain` dos peers e registra peers via `/nodes/register`.

---

## 3) Inicialização obrigatória: ROOT + Genesis Block

Ao iniciar o serviço, o nó cria o **Genesis Block** contendo uma transação especial:

* `type = "ROOT"`
* `text = "ROOT: rede inicializada"`
* `id = "root"` (fixo)

Isso garante que os **3 nós começam iguais** e podem validar se pertencem à mesma rede (mesma raiz).

---

## 4) Modelos de dados (JSON simples)

### Transaction

```json
{
  "id": "uuid",
  "type": "TX | UPDATE | ROOT",
  "text": "string",
  "timestamp": 1700000000,
  "replaces": "uuid (opcional, se type=UPDATE)",
  "origin_node": "node_id"
}
```

### Block

```json
{
  "index": 1,
  "timestamp": 1700000000,
  "transactions": [],
  "proof": 12345,
  "previous_hash": "abc123"
}
```

---

## 5) Regras do CRUD (sem “alterar o passado”)

### Create

* Cria `type="TX"` com `text`.
* Vai para o **mempool**.

### Read

* Consultar mempool (pendentes).
* Consultar todas (pendentes + registradas na chain).

### Update (duas regras simples)

* Se a transação **ainda está pendente (mempool)**: atualizar o `text` diretamente.
* Se a transação **já está minerada**: não editar bloco antigo; criar nova transação `type="UPDATE"`:

  * `replaces = <id da transação antiga>`
  * `text = <novo texto>`

---

## 6) Prova de Trabalho (PoW) — “4 zeros”

Para minerar um bloco, o nó encontra um `proof` tal que o hash do “desafio” comece com:

* `"0000"`

Isso é apenas uma **prova de conceito**, fácil de demonstrar e explicar.

---

## 7) Consenso: Democracia 50% + 1

### Definição

* Com **3 nós**, maioria = **2 votos**.

### Como funciona o `/nodes/resolve`

1. Nó consulta `/chain` de todos os peers (timeout curto).
2. Valida a chain recebida:

   * `previous_hash` correto entre blocos
   * PoW válido (4 zeros)
3. Gera um “fingerprint” simples da chain (ex.: `length + hash(último bloco)`).
4. **Votação**:

   * se algum fingerprint tiver **>= 2 votos**, essa chain vence.
5. Se **não houver maioria**:

   * escolher a **cadeia válida mais longa**
   * se empatar, escolher a chain do **peer mais confiável** (menor `fail_count`)

---

## 8) Rotas da API (REST)

### Blockchain / Mineração

* `GET /chain`

  * Retorna `{ "chain": [...], "length": N }`
* `GET /mine`

  * Mina 1 bloco com as transações do mempool (se existir)

### Transações (CRUD)

* `POST /transactions/new`

  * Body:

    ```json
    { "text": "minha transacao" }
    ```
* `GET /transactions/pending`

  * Retorna mempool
* `GET /transactions/all`

  * Retorna todas as transações (mempool + chain)
* `PUT /transactions/<tx_id>`

  * Se pendente: atualiza
  * Se minerada: cria `UPDATE`

### Rede P2P

* `POST /nodes/register`

  * Body:

    ```json
    { "nodes": ["127.0.0.1:5001", "127.0.0.1:5002"] }
    ```
* `GET /nodes`

  * Lista peers conhecidos
* `GET /nodes/resolve`

  * Executa consenso (maioria + validação)

### Falhas (somente para demonstração)

* `POST /faults`

  * Body:

    ```json
    { "mode": "NORMAL | STOP | BYZANTINE" }
    ```
  * Efeito:

    * `STOP`: simula nó parado (erro/timeout)
    * `BYZANTINE`: responde com chain inválida ou dados inconsistentes

---

## 9) Automações (sem depender de ação manual)

### Auto-register (início)

* Ao subir, o nó lê `PEERS` (env/config) e chama o mesmo fluxo de `/nodes/register`.

### Auto-mine (periódico)

* A cada **X segundos**:

  * se mempool não estiver vazio → minera.

### Auto-consensus (periódico)

* A cada **Y segundos**:

  * roda `/nodes/resolve` internamente.

Implementação simples: `threading.Thread + time.sleep()`.

---

## 10) Interface Web (UI)

Uma página `GET /ui` (HTML simples) para acionar tudo:

* Criar transação (campo texto)
* Botões:

  * Minerar
  * Rodar consenso
  * Ver chain
  * Ver pendentes
  * Ver peers
* Form para registrar peers (1 por linha)

Objetivo: demonstrar o trabalho sem Postman.

---

## 11) Cenários de teste / demonstração (roteiro)

1. Subir os 3 nós.
2. Confirmar que todos têm Genesis + ROOT.
3. Registrar peers (auto ou UI).
4. Criar transação no nó A.
5. Auto-mine gera bloco com PoW (hash “0000”).
6. Auto-consensus sincroniza os 3 nós.
7. Ativar `STOP` no nó C: A e B seguem (maioria).
8. Ativar `BYZANTINE` no nó C: A e B ignoram por validação e maioria.
9. Update:

   * atualizar pendente (edita)
   * atualizar minerada (gera `UPDATE`)

---

## 12) Definition of Done (aceite)

* [ ] 3 nós rodando e comunicando via HTTP.
* [ ] CRUD de transações funcionando (com regra de UPDATE).
* [ ] `/chain` retorna blockchain completo em JSON.
* [ ] Consenso 50%+1 implementado e rodando periodicamente.
* [ ] Nó mais confiável como desempate.
* [ ] Transação ROOT + sincronização inicial.
* [ ] PoW com 4 zeros funcionando.
* [ ] UI simples para todas as rotas.
* [ ] Simulação de falhas STOP e BYZANTINE.

---

## 13) Referência base (tutorial)

A implementação parte do modelo clássico didático (rotas `/mine`, `/transactions/new`, `/chain`, `/nodes/register`, `/nodes/resolve`, PoW 4 zeros e resolução de conflitos) do tutorial “Build your own blockchain in Python” (Medium).
