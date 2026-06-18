"""
seed_data.py
-------------
Insere dados de exemplo demonstrando:
  - SUBDOCUMENTOS  -> campo "endereco" dentro de cada cliente
  - ARRAYS         -> campo "interesses" (lista de strings) e "itens" (lista de subdocumentos)
  - RELACIONAMENTO -> campo "cliente_id" em pedidos + aresta na coleção "comprou"

Execute:
    python seed_data.py
"""

import config
from db_connection import get_database

CLIENTES_EXEMPLO = [
    {
        "_key": "cliente1",
        "nome": "Maria Silva",
        "email": "maria.silva@email.com",
        "idade": 29,
        "endereco": {  # subdocumento
            "rua": "Av. Brasil",
            "numero": 100,
            "cidade": "Juiz de Fora",
            "estado": "MG",
            "cep": "36000-000",
        },
        "interesses": ["livros", "tecnologia", "viagens"],  # array
    },
    {
        "_key": "cliente2",
        "nome": "João Pereira",
        "email": "joao.pereira@email.com",
        "idade": 41,
        "endereco": {
            "rua": "Rua das Flores",
            "numero": 55,
            "cidade": "Belo Horizonte",
            "estado": "MG",
            "cep": "30100-000",
        },
        "interesses": ["esportes", "tecnologia"],
    },
    {
        "_key": "cliente3",
        "nome": "Ana Costa",
        "email": "ana.costa@email.com",
        "idade": 34,
        "endereco": {
            "rua": "Rua Sete de Setembro",
            "numero": 12,
            "cidade": "Rio de Janeiro",
            "estado": "RJ",
            "cep": "20000-000",
        },
        "interesses": ["moda", "viagens", "gastronomia"],
    },
]

PEDIDOS_EXEMPLO = [
    {
        "_key": "pedido1",
        "cliente_id": "clientes/cliente1",
        "data_pedido": "2026-05-10",
        "status": "concluido",
        "itens": [  # array de subdocumentos
            {"produto": "Notebook", "quantidade": 1, "preco_unitario": 3500.00},
            {"produto": "Mouse sem fio", "quantidade": 2, "preco_unitario": 50.00},
        ],
    },
    {
        "_key": "pedido2",
        "cliente_id": "clientes/cliente1",
        "data_pedido": "2026-06-01",
        "status": "pendente",
        "itens": [
            {"produto": "Livro AQL na prática", "quantidade": 1, "preco_unitario": 89.90},
        ],
    },
    {
        "_key": "pedido3",
        "cliente_id": "clientes/cliente2",
        "data_pedido": "2026-05-20",
        "status": "concluido",
        "itens": [
            {"produto": "Tênis de corrida", "quantidade": 1, "preco_unitario": 420.00},
            {"produto": "Garrafa térmica", "quantidade": 1, "preco_unitario": 75.00},
        ],
    },
    {
        "_key": "pedido4",
        "cliente_id": "clientes/cliente3",
        "data_pedido": "2026-06-05",
        "status": "concluido",
        "itens": [
            {"produto": "Mala de viagem", "quantidade": 1, "preco_unitario": 650.00},
            {"produto": "Adaptador de tomada", "quantidade": 3, "preco_unitario": 25.00},
        ],
    },
]


def inserir_documentos(colecao, documentos):
    inseridos = 0
    for doc in documentos:
        if colecao.has(doc["_key"]):
            continue
        colecao.insert(doc)
        inseridos += 1
    return inseridos


def inserir_arestas(db):
    """Cria a aresta cliente -> pedido na coleção 'comprou' para cada pedido."""
    comprou = db.collection(config.COL_COMPROU)
    inseridas = 0
    for pedido in PEDIDOS_EXEMPLO:
        aresta_key = f"{pedido['cliente_id'].split('/')[1]}-{pedido['_key']}"
        if comprou.has(aresta_key):
            continue
        comprou.insert(
            {
                "_key": aresta_key,
                "_from": pedido["cliente_id"],
                "_to": f"{config.COL_PEDIDOS}/{pedido['_key']}",
            }
        )
        inseridas += 1
    return inseridas


def main():
    db = get_database()

    n_clientes = inserir_documentos(db.collection(config.COL_CLIENTES), CLIENTES_EXEMPLO)
    print(f"[seed] {n_clientes} cliente(s) inserido(s).")

    n_pedidos = inserir_documentos(db.collection(config.COL_PEDIDOS), PEDIDOS_EXEMPLO)
    print(f"[seed] {n_pedidos} pedido(s) inserido(s).")

    n_arestas = inserir_arestas(db)
    print(f"[seed] {n_arestas} relação(ões) cliente->pedido inserida(s) no grafo.")


if __name__ == "__main__":
    main()
