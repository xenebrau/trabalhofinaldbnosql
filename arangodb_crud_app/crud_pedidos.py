"""
crud_pedidos.py
------------------
Operações de CRUD (Create, Read, Update, Delete) para a coleção 'pedidos',
incluindo manipulação do array de subdocumentos 'itens'.
"""

import config
from db_connection import get_database


# ---------------------------------------------------------------- CREATE ---
def criar_pedido(db, dados: dict) -> dict:
    """Insere um novo pedido. 'dados' deve conter o array de subdocumentos 'itens'."""
    colecao = db.collection(config.COL_PEDIDOS)
    novo = colecao.insert(dados, return_new=True)["new"]

    # mantém o grafo coerente: cria também a aresta cliente -> pedido
    comprou = db.collection(config.COL_COMPROU)
    aresta_key = f"{dados['cliente_id'].split('/')[1]}-{novo['_key']}"
    if not comprou.has(aresta_key):
        comprou.insert({"_key": aresta_key, "_from": dados["cliente_id"], "_to": f"{config.COL_PEDIDOS}/{novo['_key']}"})

    return novo


# ------------------------------------------------------------------ READ ---
def buscar_pedido_por_key(db, key: str) -> dict:
    return db.collection(config.COL_PEDIDOS).get(key)


def listar_pedidos_por_status(db, status: str) -> list:
    """Equivalente a find({status: status}) / $match: { status: status }."""
    cursor = db.collection(config.COL_PEDIDOS).find({"status": status})
    return list(cursor)


# ---------------------------------------------------------------- UPDATE ---
def atualizar_status_pedido(db, key: str, novo_status: str) -> dict:
    colecao = db.collection(config.COL_PEDIDOS)
    return colecao.update({"_key": key, "status": novo_status}, return_new=True)["new"]


def adicionar_item_pedido(db, key: str, item: dict) -> dict:
    """
    Demonstra atualização de ARRAY DE SUBDOCUMENTOS: adiciona um novo item
    (produto/quantidade/preco_unitario) ao array 'itens' de um pedido existente.
    """
    aql = """
        FOR p IN pedidos
            FILTER p._key == @key
            UPDATE p WITH { itens: APPEND(p.itens, [@item]) } IN pedidos
            RETURN NEW
    """
    cursor = db.aql.execute(aql, bind_vars={"key": key, "item": item})
    return list(cursor)[0]


# ---------------------------------------------------------------- DELETE ---
def remover_pedido(db, key: str) -> None:
    db.collection(config.COL_PEDIDOS).delete(key, ignore_missing=True)
    # remove também a(s) aresta(s) ligadas a esse pedido
    aql = """
        FOR a IN comprou
            FILTER a._to == CONCAT('pedidos/', @key)
            REMOVE a IN comprou
    """
    db.aql.execute(aql, bind_vars={"key": key})


# ---------------------------------------------------------------- DEMO -----
def demo():
    db = get_database()

    print("\n=== CREATE ===")
    novo = criar_pedido(
        db,
        {
            "cliente_id": "clientes/cliente2",
            "data_pedido": "2026-06-15",
            "status": "pendente",
            "itens": [{"produto": "Teclado mecânico", "quantidade": 1, "preco_unitario": 350.00}],
        },
    )
    print(novo)

    print("\n=== READ (by key) ===")
    print(buscar_pedido_por_key(db, novo["_key"]))

    print("\n=== READ (find por status) ===")
    print(listar_pedidos_por_status(db, "pendente"))

    print("\n=== UPDATE (status) ===")
    print(atualizar_status_pedido(db, novo["_key"], "concluido"))

    print("\n=== UPDATE (array de subdocumentos) ===")
    print(adicionar_item_pedido(db, novo["_key"], {"produto": "Mousepad", "quantidade": 1, "preco_unitario": 30.00}))

    print("\n=== DELETE ===")
    remover_pedido(db, novo["_key"])
    print(f"Pedido {novo['_key']} removido.")


if __name__ == "__main__":
    demo()
