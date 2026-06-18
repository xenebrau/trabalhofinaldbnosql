"""
crud_clientes.py
------------------
Operações de CRUD (Create, Read, Update, Delete) para a coleção 'clientes'.

Usa tanto os métodos nativos do driver (insert/get/update/delete/find)
quanto AQL puro, para mostrar as duas formas de trabalhar com o ArangoDB.
"""

import config
from db_connection import get_database


# ---------------------------------------------------------------- CREATE ---
def criar_cliente(db, dados: dict) -> dict:
    """Insere um novo cliente. 'dados' pode conter subdocumento 'endereco' e array 'interesses'."""
    colecao = db.collection(config.COL_CLIENTES)
    return colecao.insert(dados, return_new=True)["new"]


# ------------------------------------------------------------------ READ ---
def buscar_cliente_por_key(db, key: str) -> dict:
    """Leitura simples por chave primária (equivalente a um find by id)."""
    return db.collection(config.COL_CLIENTES).get(key)


def listar_todos_clientes(db) -> list:
    """
    Equivalente a um 'find()' sem filtro: retorna todos os documentos da coleção.
    Usa o método find() nativo do driver, que existe especificamente para
    espelhar a semântica de busca por igualdade de campos, como no MongoDB.
    """
    cursor = db.collection(config.COL_CLIENTES).find({})
    return list(cursor)


def buscar_clientes_por_campo(db, campo: str, valor) -> list:
    """
    Equivalente direto ao find({campo: valor}) do MongoDB,
    usando o método find() do próprio driver python-arango.
    """
    cursor = db.collection(config.COL_CLIENTES).find({campo: valor})
    return list(cursor)


# ---------------------------------------------------------------- UPDATE ---
def atualizar_cliente(db, key: str, novos_dados: dict) -> dict:
    """Atualiza parcialmente um cliente (merge dos campos informados)."""
    colecao = db.collection(config.COL_CLIENTES)
    novos_dados["_key"] = key
    return colecao.update(novos_dados, return_new=True)["new"]


def adicionar_interesse(db, key: str, novo_interesse: str) -> dict:
    """
    Demonstra atualização de ARRAY: adiciona um item ao array 'interesses'
    sem duplicar, usando AQL com a função PUSH + UNIQUE.
    """
    aql = """
        FOR c IN clientes
            FILTER c._key == @key
            UPDATE c WITH { interesses: UNIQUE(APPEND(c.interesses, [@novo_interesse])) } IN clientes
            RETURN NEW
    """
    cursor = db.aql.execute(aql, bind_vars={"key": key, "novo_interesse": novo_interesse})
    return list(cursor)[0]


# ---------------------------------------------------------------- DELETE ---
def remover_cliente(db, key: str) -> None:
    db.collection(config.COL_CLIENTES).delete(key, ignore_missing=True)


# ---------------------------------------------------------------- DEMO -----
def demo():
    db = get_database()

    print("\n=== CREATE ===")
    novo = criar_cliente(
        db,
        {
            "nome": "Carlos Souza",
            "email": "carlos.souza@email.com",
            "idade": 25,
            "endereco": {"rua": "Rua Nova", "numero": 7, "cidade": "Juiz de Fora", "estado": "MG", "cep": "36010-000"},
            "interesses": ["games"],
        },
    )
    print(novo)

    print("\n=== READ (find by key) ===")
    print(buscar_cliente_por_key(db, novo["_key"]))

    print("\n=== READ (find por campo, equivalente ao find() do Mongo) ===")
    print(buscar_clientes_por_campo(db, "idade", 25))

    print("\n=== UPDATE ===")
    print(atualizar_cliente(db, novo["_key"], {"idade": 26}))

    print("\n=== UPDATE (array) ===")
    print(adicionar_interesse(db, novo["_key"], "tecnologia"))

    print("\n=== DELETE ===")
    remover_cliente(db, novo["_key"])
    print(f"Cliente {novo['_key']} removido.")


if __name__ == "__main__":
    demo()
