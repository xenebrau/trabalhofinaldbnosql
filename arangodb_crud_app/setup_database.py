"""
setup_database.py
-------------------
Cria a estrutura do banco: coleções de documentos (clientes, pedidos),
a coleção de arestas (comprou) e o grafo (grafo_vendas).

Isso demonstra na prática o caráter MULTIMODELO do ArangoDB: as mesmas
coleções de documentos podem ser conectadas por um grafo nativo, sem
precisar de outro banco de dados separado.

Execute:
    python setup_database.py
"""

import config
from db_connection import get_database


def criar_colecoes(db):
    if not db.has_collection(config.COL_CLIENTES):
        db.create_collection(config.COL_CLIENTES)
        print(f"[setup] Coleção de documentos '{config.COL_CLIENTES}' criada.")
    else:
        print(f"[setup] Coleção '{config.COL_CLIENTES}' já existe.")

    if not db.has_collection(config.COL_PEDIDOS):
        db.create_collection(config.COL_PEDIDOS)
        print(f"[setup] Coleção de documentos '{config.COL_PEDIDOS}' criada.")
    else:
        print(f"[setup] Coleção '{config.COL_PEDIDOS}' já existe.")

    # Coleção de ARESTAS (edge collection) -> é isso que torna o ArangoDB
    # um banco também orientado a grafos, além de documental.
    if not db.has_collection(config.COL_COMPROU):
        db.create_collection(config.COL_COMPROU, edge=True)
        print(f"[setup] Coleção de arestas '{config.COL_COMPROU}' criada.")
    else:
        print(f"[setup] Coleção de arestas '{config.COL_COMPROU}' já existe.")


def criar_indices(db):
    clientes = db.collection(config.COL_CLIENTES)
    # Índice único de e-mail: garante integridade e acelera buscas por e-mail.
    clientes.add_index({"type": "persistent", "fields": ["email"], "unique": True})

    pedidos = db.collection(config.COL_PEDIDOS)
    # Índice para acelerar joins manuais (equivalente a $lookup) por cliente_id.
    pedidos.add_index({"type": "persistent", "fields": ["cliente_id"], "unique": False})
    print("[setup] Índices criados/confirmados.")


def criar_grafo(db):
    if db.has_graph(config.GRAFO_VENDAS):
        print(f"[setup] Grafo '{config.GRAFO_VENDAS}' já existe.")
        return

    db.create_graph(
        config.GRAFO_VENDAS,
        edge_definitions=[
            {
                "edge_collection": config.COL_COMPROU,
                "from_vertex_collections": [config.COL_CLIENTES],
                "to_vertex_collections": [config.COL_PEDIDOS],
            }
        ],
    )
    print(f"[setup] Grafo '{config.GRAFO_VENDAS}' criado (clientes -> comprou -> pedidos).")


def main():
    db = get_database()
    criar_colecoes(db)
    criar_indices(db)
    criar_grafo(db)
    print("[setup] Estrutura do banco pronta.")


if __name__ == "__main__":
    main()
