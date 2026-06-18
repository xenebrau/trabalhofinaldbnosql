# Aplicação CRUD com ArangoDB (Python + python-arango)

Projeto de demonstração para o trabalho de Banco de Dados NoSQL. Implementa
um cenário de loja virtual (clientes e pedidos) usando o ArangoDB, cobrindo:

- CRUD completo (Create, Read, Update, Delete);
- Arrays (`interesses`, `itens`) e subdocumentos (`endereco`, itens do pedido);
- Equivalentes em AQL das operações `find`, `aggregate`, `$match`, `$project`,
  `$lookup`, `$unwind` e `$group`, populares no MongoDB;
- Uso do modelo de **grafo nativo** do ArangoDB (coleção de arestas `comprou`)
  como alternativa de alta performance ao `$lookup` manual.

## 1. Subir o ArangoDB com Docker

```bash
docker compose up -d
```

Isso baixa a imagem oficial `arangodb:3.12` e inicia um container expondo a
porta `8529`. A senha do usuário `root` é definida em `docker-compose.yml`
(variável `ARANGO_ROOT_PASSWORD`).

Verifique se o container está saudável:

```bash
docker ps
docker logs arangodb_crud --tail 50
```

Acesse a interface web (Web UI) em:

```
http://localhost:8529
```

Usuário: `root` | Senha: a definida em `docker-compose.yml` (`senha123`
por padrão — troque antes de usar em produção).

## 2. Instalar as dependências Python

Recomenda-se um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Rodar a demonstração completa

```bash
python main.py
```

O script é idempotente: pode ser executado várias vezes sem duplicar dados
(o setup e o seed verificam existência antes de criar/inserir).

## 4. Rodar partes isoladas (útil durante a apresentação)

```bash
python setup_database.py        # cria coleções, índices e o grafo
python seed_data.py             # popula clientes e pedidos de exemplo
python crud_clientes.py         # demo de CRUD em clientes
python crud_pedidos.py          # demo de CRUD em pedidos
python consultas_avancadas.py   # demo de find/match/project/unwind/group/lookup
```

## 5. Estrutura do projeto

| Arquivo                  | Responsabilidade                                              |
|---------------------------|----------------------------------------------------------------|
| `docker-compose.yml`      | Sobe o ArangoDB localmente                                     |
| `config.py`                | Configurações de conexão e nomes de coleções                  |
| `db_connection.py`         | Abre a conexão autenticada com o banco                        |
| `setup_database.py`        | Cria coleções, índices e o grafo `grafo_vendas`                |
| `seed_data.py`              | Insere dados de exemplo (clientes, pedidos, arestas)           |
| `crud_clientes.py`          | CRUD da coleção `clientes`                                     |
| `crud_pedidos.py`           | CRUD da coleção `pedidos`                                      |
| `consultas_avancadas.py`    | Equivalentes AQL de find/$match/$project/$unwind/$group/$lookup |
| `main.py`                   | Roteiro de demonstração ponta a ponta                         |

## 6. Mapeamento de conceitos (MongoDB → AQL/ArangoDB)

| Conceito (estilo MongoDB) | Equivalente em AQL (ArangoDB)                                   |
|----------------------------|--------------------------------------------------------------------|
| `find({...})`               | `FOR doc IN colecao FILTER ... RETURN doc`                        |
| `$match`                    | `FILTER`                                                            |
| `$project`                  | `RETURN { campo: doc.campo, ... }`                                 |
| `$unwind`                   | `FOR item IN doc.array`                                            |
| `$group` / `$sum` / `$count`| `COLLECT campo = ... AGGREGATE total = SUM(...)` ou `WITH COUNT INTO` |
| `$lookup` (join manual)     | segundo `FOR` + `FILTER` comparando chaves                         |
| `$lookup` (via relacionamento)| travessia nativa de grafo: `FOR v IN 1..1 OUTBOUND start edgeCol` |
| `aggregate([...])` (pipeline)| uma única consulta AQL combinando `FOR/FILTER/COLLECT/LET/RETURN` |

## 7. Encerrar o ambiente

```bash
docker compose down          # para o container, mantém os dados (volumes)
docker compose down -v       # para o container e remove os dados
```
