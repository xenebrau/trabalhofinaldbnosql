"""
main.py
--------
Roteiro de demonstração para a apresentação. Executa, em sequência:
  1. Criação da estrutura do banco (coleções, índices, grafo)
  2. Inserção dos dados de exemplo
  3. Demonstração de CRUD em 'clientes'
  4. Demonstração de CRUD em 'pedidos'
  5. Demonstração das consultas avançadas (find / $match / $project /
     $unwind / $group / $lookup / pipeline completo)

Execute:
    python main.py
"""

import setup_database
import seed_data
import crud_clientes
import crud_pedidos
import consultas_avancadas


def titulo(texto):
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


def main():
    titulo("1) SETUP DO BANCO")
    setup_database.main()

    titulo("2) CARGA DE DADOS DE EXEMPLO")
    seed_data.main()

    titulo("3) CRUD - CLIENTES")
    crud_clientes.demo()

    titulo("4) CRUD - PEDIDOS")
    crud_pedidos.demo()

    titulo("5) CONSULTAS AVANÇADAS (find / aggregate / match / project / lookup / unwind / group)")
    consultas_avancadas.demo()

    titulo("DEMONSTRAÇÃO CONCLUÍDA")


if __name__ == "__main__":
    main()
