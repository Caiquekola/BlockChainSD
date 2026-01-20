# Developer Context — Trabalho de Sistemas Distribuídos: Blockchain (3 nós, CRUD, consenso 50%+1)

## 1) Objetivo (bem simples)

Construir uma **blockchain didática** com **3 nós** (3 processos/containers), onde cada nó expõe uma **API pública** para:

* **CRUD de “transações”** (transação é um **JSON com um texto**).
* **Consultar transações** (pendentes e já registradas).
* **Obter o blockchain completo em JSON**.
* **Nós conversarem entre si** (rede P2P via HTTP).
* Implementar **consenso por democracia (50% + 1)**.
* Rodar **validação/consenso periodicamente** (de tempos em tempos).
* Considerar “**nó mais confiável**” (menos falhas) como critério de desempate.
* Ter **Prova de Conceito PoW (hash com 4 zeros)**.
* Simular **falhas de PARADA** (nó não responde) e **falhas BIZANTINAS** (nó responde com comportamento inesperado).

Basear o esqueleto no tutorial do Medium (rotas `/mine`, `/transactions/new`, `/chain`, `/nodes/register`, `/nodes/resolve`, PoW com 4 zeros e “resolver conflitos” pegando cadeia válida) , mas adaptar para o que o trabalho pede.

---

## 2) Escopo (o que entra / o que não entra)

### Entra (MVP do trabalho)

* 3 nós (Node A/B/C).
* API REST + uma UI simples (páginas HTML) para acionar todas as rotas.
* PoW “4 zeros” (padrão PoC) .
* Consenso por maioria (2 de 3).
* Sincronização inicial (todos começam iguais).
* Falhas bizantinas e de parada (simuladas).

### Não entra (pra manter simples)

* Criptografia avançada, assinaturas, carteira real.
* PBFT completo (muito difícil de explicar).
* Persistência robusta em banco (pode ser só em memória + opcional JSON em arquivo).

---

## 3) Arquitetura (3 nós)

* **Mesma aplicação** rodando 3 vezes (porta diferente).
* Cada nó tem:

  * `Blockchain` (cadeia de blocos)
  * `mempool` (transações pendentes)
  * `peers` (lista de outros nós)
  * `reliability_score` por peer (sucesso/erro)

**Sugestão de portas:**

* Nó 1: `localhost:5000`
* Nó 2: `localhost:5001`
* Nó 3: `localhost:5002`

---

## 4) “Root transaction” + sincronização inicial (obrigatório)

### Regra simples

* Ao iniciar, cada nó cria um **Genesis Block** contendo UMA transação especial:

  * `type = "ROOT"`
  * `text = "ROOT: rede inicializada"`
  * `id` fixo (ex.: `"root"`), para todos terem exatamente a mesma raiz.

Isso garante que:

* Todos começam com a mesma base (mesmo bloco 1).
* Ao registrar peers, um nó só aceita peers cuja cadeia tenha o mesmo “ROOT/genesis”.

---

## 5) Modelos de dados (JSON simples)

### Transaction

```json
{
  "id": "uuid",
  "type": "TX | UPDATE | ROOT",
  "text": "string",
  "timestamp": 1700000000,
  "replaces": "uuid (opcional, só se type=UPDATE)",
  "origin_node": "node_id"
}
```

### Block

```json
{
  "index": 1,
  "timestamp": 1700000000,
  "transactions": [ ... ],
  "proof": 12345,
  "previous_hash": "abc123"
}
```

---

## 6) Regras do CRUD (sem quebrar a ideia de blockchain)

### Create

* Cria transação `type="TX"` (texto livre).
* Vai para o **mempool**.

### Read

* Listar pendentes (mempool) e também listar as que já estão na chain.

### Update (sem “editar bloco antigo”)

Para continuar “blockchain-like” e ainda cumprir “update das transações”:

* Se a transação **ainda está no mempool**: pode atualizar o `text` (simples).
* Se a transação **já foi minerada**: NÃO editar; criar uma nova transação `type="UPDATE"` com:

  * `replaces = <id da antiga>`
  * `text = <novo texto>`

Assim você explica fácil:

> “Na blockchain eu não altero o passado, eu registro uma correção como um novo evento.”

---

## 7) API REST (rotas) — compatível com o tutorial + extras

O tutorial base usa `/mine`, `/transactions/new`, `/chain`, `/nodes/register`, `/nodes/resolve` . Vamos manter e acrescentar CRUD/automação.

### (A) Blockchain / mineração

* `GET /chain` → retorna `{ chain, length }` (JSON).
* `GET /mine` → minera 1 bloco se houver transações pendentes.

  * PoW: encontrar proof cujo hash tenha **"0000"** no começo (PoC) .

### (B) Transações (CRUD)

* `POST /transactions/new`

  * Body:

    ```json
    { "text": "minha transacao" }
    ```
  * Response:

    ```json
    { "message": "...", "tx_id": "..." }
    ```
* `GET /transactions/pending` → mempool.
* `GET /transactions/all` → todas (mempool + chain).
* `PUT /transactions/<tx_id>`

  * Se pendente: atualiza texto.
  * Se minerada: cria `UPDATE`.

### (C) Rede P2P

* `POST /nodes/register`

  * Body:

    ```json
    { "nodes": ["127.0.0.1:5001", "127.0.0.1:5002"] }
    ```
* `GET /nodes` → lista peers conhecidos.
* `GET /nodes/resolve` → roda consenso.

---

## 8) Consenso “Democracia 50% + 1” (bem explicado)

### Ideia

Com **3 nós**, “50%+1” = **2 votos**.

### O que cada nó faz no `/nodes/resolve`

1. Busca `/chain` de cada peer (com timeout curto, ex.: 1s).
2. Valida cada chain recebida:

   * hashes encadeados (`previous_hash`)
   * prova de trabalho válida (4 zeros) 
3. Cria um “resumo” para votação:

   * `chain_fingerprint = hash(último_bloco) + ":" + length` (simples)
4. **Votação (maioria):**

   * Conta quantos peers reportaram o mesmo `chain_fingerprint`.
   * Se algum fingerprint tiver **>=2 votos**, essa é a chain escolhida.
5. **Desempate / sem maioria:**

   * Se não houver maioria (ex.: partição), usar a “cadeia válida mais longa” (igual ideia do tutorial) .
   * Se empate de tamanho: escolher a chain vinda do **peer mais confiável** (menos falhas registradas).

### Confiabilidade (“nó mais confiável”)

Manter por peer:

* `ok_count` (respostas válidas)
* `fail_count` (timeout, erro HTTP, chain inválida)

Critério simples:

* “mais confiável” = menor `fail_count`.
* Use isso apenas para **desempate**, pra não complicar.

---

## 9) Automação (sem “clicar na mão”)

Você pediu para tornar rotas como `/mine`, `/nodes/resolve`, `/nodes/register` automáticas.

### Auto-register

* No startup (ao subir o nó), ler uma lista de peers do `.env` ou `config.json` e chamar internamente o mesmo fluxo do `/nodes/register`.

### Auto-mine

* Um loop em background (thread) roda a cada X segundos:

  * Se mempool não vazio → minerar (`/mine` internamente).

### Auto-consensus

* Outro loop em background roda a cada Y segundos:

  * chama `resolve` (`/nodes/resolve` internamente).

> Importante: para “não inventar coisa difícil”, dá pra fazer com `threading.Thread + time.sleep()` (sem libs extras).

---

## 10) Interface (UI) simples para todas as rotas

Criar uma página `GET /ui` (HTML) com:

* Form para `POST /transactions/new` (campo texto)
* Botões/links para:

  * `GET /mine`
  * `GET /nodes/resolve`
  * `GET /chain`
  * `GET /transactions/pending`
  * `GET /nodes`
* Form para `POST /nodes/register` (textarea com 1 nó por linha)

Objetivo da UI:

* Conseguir demonstrar tudo no browser rápido, sem Postman.

---

## 11) Simulação de falhas (PARADA e BIZANTINA)

Criar um endpoint de controle (só para demo):

### `POST /faults`

Body:

```json
{ "mode": "NORMAL | STOP | BYZANTINE" }
```

Comportamento:

* **STOP**: o nó responde `503` (ou dorme 5s) em todas as rotas → simula “parou / rede caiu”.
* **BYZANTINE**: o nó:

  * devolve `/chain` corrompida (ex.: altera `previous_hash` de um bloco), ou
  * devolve um `length` errado,
  * ou “vota” numa chain inválida.

Como os outros nós validam chain, eles devem:

* marcar esse peer como falho (aumentar `fail_count`)
* ignorar sua chain na votação

---

## 12) Fluxo de demonstração (roteiro da apresentação)

1. Subir os 3 nós.
2. Verificar que todos têm Genesis com `ROOT`.
3. Registrar peers (auto-register ou via UI).
4. Criar transação em um nó e verificar propagação (ou pelo menos que entra no mempool daquele nó).
5. Esperar auto-mine → aparece novo bloco com PoW “0000”.
6. Rodar auto-consensus → outros nós convergem para a mesma chain.
7. Ativar falha STOP em 1 nó → sistema continua com 2 nós (maioria).
8. Ativar falha BYZANTINE em 1 nó → maioria ignora (2 honestos ganham).
9. Fazer “UPDATE”:

   * atualizar pendente (edita)
   * atualizar minerada (cria `UPDATE`)

---

## 13) Critérios de aceitação (Definition of Done)

* [ ] 3 nós rodando e se comunicando via HTTP.
* [ ] Rotas principais do tutorial funcionando (`/mine`, `/transactions/new`, `/chain`, `/nodes/register`, `/nodes/resolve`) .
* [ ] Transação é JSON com campo `text`.
* [ ] CRUD implementado (update conforme regra: pendente edita; minerada vira UPDATE).
* [ ] Consenso “50% + 1” implementado (com 3 nós = 2 votos).
* [ ] Consenso roda periodicamente (automático).
* [ ] UI simples para acionar todas as rotas.
* [ ] Simulação de falhas STOP e BYZANTINE.
* [ ] PoW com 4 zeros (prova de conceito) .
