"""
db_connection.py
------------------
Centraliza a criação da conexão com o ArangoDB usando o driver python-arango.

Uso típico:
    from db_connection import get_database
    db = get_database()
"""

from arango import ArangoClient
from arango.exceptions import ServerConnectionError

import config


def get_client() -> ArangoClient:
    """Cria o cliente HTTP que fala com o servidor ArangoDB."""
    return ArangoClient(hosts=config.ARANGO_HOST)


def get_sys_db(client: ArangoClient = None):
    """Retorna o handle do banco '_system', usado para criar/checar outros bancos."""
    client = client or get_client()
    return client.db("_system", username=config.ARANGO_ROOT_USER, password=config.ARANGO_ROOT_PASSWORD)


def ensure_database_exists() -> None:
    """Garante que o banco de aplicação (loja_db) exista antes de qualquer operação."""
    sys_db = get_sys_db()
    if not sys_db.has_database(config.ARANGO_DB_NAME):
        sys_db.create_database(config.ARANGO_DB_NAME)
        print(f"[setup] Banco '{config.ARANGO_DB_NAME}' criado.")
    else:
        print(f"[setup] Banco '{config.ARANGO_DB_NAME}' já existe.")


def get_database():
    """
    Ponto de entrada principal: garante que o banco existe e devolve
    o handle de conexão já autenticado para ele.
    """
    client = get_client()
    try:
        ensure_database_exists()
    except ServerConnectionError as exc:
        raise RuntimeError(
            "Não foi possível conectar ao ArangoDB. Verifique se o container "
            "está no ar (docker compose up -d) e se a porta 8529 está acessível."
        ) from exc

    return client.db(
        config.ARANGO_DB_NAME,
        username=config.ARANGO_ROOT_USER,
        password=config.ARANGO_ROOT_PASSWORD,
    )
