"""
config.py
----------
Configurações centrais de conexão com o ArangoDB.

Todas as configurações podem ser sobrescritas por variáveis de ambiente,
o que facilita rodar o mesmo código localmente, em CI ou em produção.
"""

import os

# Endereço do servidor ArangoDB (o container Docker expõe a porta 8529)
ARANGO_HOST = os.getenv("ARANGO_HOST", "http://localhost:8529")

# Credenciais do usuário root (definidas no docker-compose.yml)
ARANGO_ROOT_USER = os.getenv("ARANGO_ROOT_USER", "root")
ARANGO_ROOT_PASSWORD = os.getenv("ARANGO_ROOT_PASSWORD", "senha123")

# Nome do banco de dados de aplicação que será criado
ARANGO_DB_NAME = os.getenv("ARANGO_DB_NAME", "loja_db")

# Nomes das coleções utilizadas na aplicação
COL_CLIENTES = "clientes"
COL_PEDIDOS = "pedidos"
COL_COMPROU = "comprou"  # coleção de arestas (edge collection) -> demonstra o modelo de grafo
GRAFO_VENDAS = "grafo_vendas"
