# scripts/check_database.py
import sys
import os
from sqlalchemy import text, inspect

# Adiciona o diretório raiz ao path para permitir importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connect import db_connection


def check_tables():
    """Verifica as tabelas existentes no banco de dados"""
    print("Verificando tabelas existentes no banco de dados...")

    # Obter sessão do banco de dados
    db = next(db_connection.get_db())

    try:
        # Obter inspetor da conexão
        inspector = inspect(db_connection.engine)

        # Listar todas as tabelas
        tables = inspector.get_table_names()

        # Verificar se as novas tabelas existem
        new_tables = ["instruments", "datasets", "instrument_datasets"]
        old_tables = ["custom_tables", "table_columns", "table_rows", "cell_values",
                      "table_questionnaires", "questionnaire_responses"]

        print("\nStatus das tabelas:")
        print("-" * 50)

        # Verificar novas tabelas
        print("Novas tabelas:")
        for table in new_tables:
            status = "✓ Existe" if table in tables else "✗ Não existe"
            print(f"  {table}: {status}")

        # Verificar tabelas antigas
        print("\nTabelas antigas (devem ser removidas):")
        for table in old_tables:
            status = "✗ Ainda existe" if table in tables else "✓ Removida"
            print(f"  {table}: {status}")

        # Verificar estrutura das novas tabelas
        print("\nEstrutura das novas tabelas existentes:")
        for table in [t for t in new_tables if t in tables]:
            print(f"\nTabela: {table}")
            columns = inspector.get_columns(table)
            for column in columns:
                nullable = "NULL" if column['nullable'] else "NOT NULL"
                print(f"  {column['name']} {column['type']} {nullable}")

            # Verificar chaves estrangeiras
            foreign_keys = inspector.get_foreign_keys(table)
            if foreign_keys:
                print("  Chaves estrangeiras:")
                for fk in foreign_keys:
                    print(f"    {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

    except Exception as e:
        print(f"Erro ao verificar banco de dados: {str(e)}")

    finally:
        db.close()


if __name__ == "__main__":
    check_tables()