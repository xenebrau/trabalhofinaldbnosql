"""
consultas_avancadas.py
-------------------------
Este módulo é o coração da demonstração pedida no trabalho: mostra como
cada operação clássica de "find / aggregate" (popularizada pelo MongoDB)
é expressa em AQL, a linguagem de consulta do ArangoDB.

Importante: no ArangoDB não existem comandos separados "find()" e
"aggregate()". Tudo -- filtro, projeção, junção, explosão de array e
agrupamento -- é expresso dentro de UMA ÚNICA linguagem de consulta (AQL),
combinando as cláusulas FOR / FILTER / LET / COLLECT / RETURN.

Tabela de equivalência (ver também o documento Word):

    MongoDB                         ArangoDB (AQL)
    ------------------------------  --------------------------------
    find({...})                     FOR doc IN colecao FILTER ... RETURN doc
    $match                          FILTER
    $project                        RETURN { campo: doc.campo, ... }
    $unwind                         FOR item IN doc.array
    $group / $sum / $avg / $count   COLLECT campo = ... AGGREGATE/WITH COUNT
    $lookup                         segundo FOR + FILTER (join manual)
                                     OU travessia nativa de grafo (FOR v IN 1..1 ...)
"""

from db_connection import get_database


# --------------------------------------------------------------- 1) FIND ---
def equivalente_find(db) -> list:
    """find() sem filtro: todos os documentos da coleção pedidos."""
    aql = "FOR p IN pedidos RETURN p"
    return list(db.aql.execute(aql))


# ------------------------------------------------------------- 2) $MATCH ---
def equivalente_match(db, idade_minima: int) -> list:
    """$match: { idade: { $gte: idade_minima } }"""
    aql = """
        FOR c IN clientes
            FILTER c.idade >= @idade_minima
            RETURN c
    """
    return list(db.aql.execute(aql, bind_vars={"idade_minima": idade_minima}))


# ----------------------------------------------------------- 3) $PROJECT ---
def equivalente_project(db) -> list:
    """
    $project: { nome: 1, cidade: "$endereco.cidade", _id: 0 }
    Também demonstra leitura de campo dentro de um SUBDOCUMENTO (endereco.cidade).
    """
    aql = """
        FOR c IN clientes
            RETURN { nome: c.nome, cidade: c.endereco.cidade, estado: c.endereco.estado }
    """
    return list(db.aql.execute(aql))


# ----------------------------------------------------------- 4) $UNWIND ----
def equivalente_unwind(db) -> list:
    """
    $unwind: "$itens"
    Para cada pedido, gera uma linha por item do ARRAY de subdocumentos.
    """
    aql = """
        FOR p IN pedidos
            FOR item IN p.itens
                RETURN {
                    pedido_id: p._key,
                    produto: item.produto,
                    quantidade: item.quantidade,
                    subtotal: item.quantidade * item.preco_unitario
                }
    """
    return list(db.aql.execute(aql))


# ------------------------------------------------------------- 5) $GROUP ---
def equivalente_group_contagem_por_status(db) -> list:
    """$group: { _id: "$status", total: { $sum: 1 } }"""
    aql = """
        FOR p IN pedidos
            COLLECT status = p.status WITH COUNT INTO total
            RETURN { status: status, total_pedidos: total }
    """
    return list(db.aql.execute(aql))


def equivalente_group_soma_por_cliente(db) -> list:
    """
    Combina $unwind + $group + $sum:
    soma o valor total gasto por cliente, abrindo o array de itens.
    """
    aql = """
        FOR p IN pedidos
            FOR item IN p.itens
                COLLECT cliente_id = p.cliente_id
                AGGREGATE total_gasto = SUM(item.quantidade * item.preco_unitario)
                RETURN { cliente_id: cliente_id, total_gasto: total_gasto }
    """
    return list(db.aql.execute(aql))


# ------------------------------------------------------------ 6) $LOOKUP ---
def equivalente_lookup_join_manual(db) -> list:
    """
    $lookup clássico: junta 'pedidos' com 'clientes' casando cliente_id == _id.
    Esta é a forma "manual" (igual ao que se faria em qualquer outro NoSQL
    sem grafo nativo): um segundo FOR + FILTER funcionando como join.
    """
    aql = """
        FOR p IN pedidos
            FOR c IN clientes
                FILTER p.cliente_id == c._id
                RETURN MERGE(p, { cliente: KEEP(c, "nome", "email") })
    """
    return list(db.aql.execute(aql))


def equivalente_lookup_via_grafo(db) -> list:
    """
    $lookup nativo via GRAFO: em vez de um join manual por igualdade de campos,
    percorre a aresta 'comprou' (cliente -> pedido). Isso é uma vantagem do
    modelo multimodelo do ArangoDB: relacionamentos N:N ficam mais eficientes
    e expressivos do que um $lookup tradicional, especialmente em travessias
    de múltiplos saltos (ex.: cliente -> pedido -> produto -> fornecedor).
    """
    aql = """
        FOR pedido, aresta IN 1..1 OUTBOUND CONCAT('clientes/', @cliente_key) comprou
            RETURN { pedido: pedido._key, status: pedido.status, data: pedido.data_pedido }
    """
    # A travessia parte do vértice clientes/<cliente_key> e segue arestas "comprou"
    # no sentido OUTBOUND (cliente -> pedido), retornando diretamente os pedidos
    # conectados -- sem precisar comparar campos manualmente como no $lookup.
    return list(db.aql.execute(aql, bind_vars={"cliente_key": "cliente1"}))


# --------------------------------------------------------- 7) PIPELINE  ----
def pipeline_completo(db) -> list:
    """
    Replica um pipeline típico de agregação:
        $match (status concluído) -> $unwind (itens) ->
        $group (soma por cliente) -> $lookup (nome do cliente) -> $project

    Tudo em UMA ÚNICA consulta AQL.
    """
    aql = """
        FOR p IN pedidos
            FILTER p.status == "concluido"                         // $match
            FOR item IN p.itens                                     // $unwind
                COLLECT cliente_id = p.cliente_id
                AGGREGATE total_gasto = SUM(item.quantidade * item.preco_unitario)  // $group
                LET cliente = DOCUMENT(cliente_id)                  // $lookup
                RETURN {                                            // $project
                    cliente: cliente.nome,
                    cidade: cliente.endereco.cidade,
                    total_gasto: total_gasto
                }
    """
    return list(db.aql.execute(aql))


# ---------------------------------------------------------------- DEMO -----
def demo():
    db = get_database()

    print("\n=== 1) find() -> todos os pedidos ===")
    for doc in equivalente_find(db):
        print(doc)

    print("\n=== 2) $match -> clientes com idade >= 30 ===")
    for doc in equivalente_match(db, 30):
        print(doc)

    print("\n=== 3) $project -> nome e cidade (subdocumento) ===")
    for doc in equivalente_project(db):
        print(doc)

    print("\n=== 4) $unwind -> um item de pedido por linha ===")
    for doc in equivalente_unwind(db):
        print(doc)

    print("\n=== 5a) $group -> contagem de pedidos por status ===")
    for doc in equivalente_group_contagem_por_status(db):
        print(doc)

    print("\n=== 5b) $unwind + $group -> total gasto por cliente ===")
    for doc in equivalente_group_soma_por_cliente(db):
        print(doc)

    print("\n=== 6a) $lookup manual -> pedidos com dados do cliente ===")
    for doc in equivalente_lookup_join_manual(db):
        print(doc)

    print("\n=== 6b) $lookup via grafo -> pedidos do cliente1 via aresta 'comprou' ===")
    for doc in equivalente_lookup_via_grafo(db):
        print(doc)

    print("\n=== 7) Pipeline completo: match + unwind + group + lookup + project ===")
    for doc in pipeline_completo(db):
        print(doc)


if __name__ == "__main__":
    demo()
