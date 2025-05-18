# scripts/update_database_fixed.py
import sys
import os
import argparse
import json  # Adicionado para serialização JSON adequada
from sqlalchemy import text

# Adiciona o diretório raiz ao path para permitir importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connect import db_connection, Base
from database.models.instrument import Instrument
from database.models.dataset import Dataset, InstrumentDataset
from utils.instrument_plugins import InstrumentRegistry, DASS21Processor


def confirm_action(message):
    """Solicita confirmação do usuário"""
    response = input(f"{message} (s/n): ").lower()
    return response == 's'


def drop_custom_tables(db):
    """Remove tabelas relacionadas ao modelo antigo de tabelas customizadas"""
    print("Removendo tabelas do modelo antigo de tabelas customizadas...")

    # Lista de tabelas a serem removidas
    tables_to_drop = [
        "cell_values",
        "questionnaire_responses",
        "table_rows",
        "table_columns",
        "table_questionnaires",
        "custom_tables"
    ]

    for table in tables_to_drop:
        try:
            db.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
            print(f"    Tabela '{table}' removida com sucesso.")
        except Exception as e:
            print(f"    Erro ao remover tabela '{table}': {str(e)}")

    db.commit()
    print("Remoção de tabelas antigas concluída.")


def create_new_tables(db):
    """Cria as novas tabelas para o modelo de instrumentos e datasets"""
    print("Criando novas tabelas para instrumentos e datasets...")

    try:
        # Cria as tabelas definidas nos modelos
        Base.metadata.create_all(bind=db_connection.engine,
                                 tables=[Instrument.__table__,
                                         Dataset.__table__,
                                         InstrumentDataset.__table__])

        print("    Novas tabelas criadas com sucesso.")
    except Exception as e:
        print(f"    Erro ao criar novas tabelas: {str(e)}")
        return False

    return True


def seed_instruments(db):
    """Popula a tabela de instrumentos com os instrumentos disponíveis"""
    print("Populando tabela de instrumentos...")

    try:
        # Registrar o DASS-21 como instrumento padrão
        processor = DASS21Processor()

        # Verificar se o instrumento já existe
        existing = db.execute(
            text("SELECT * FROM instruments WHERE code = :code"),
            {"code": processor.code}
        ).fetchone()

        if not existing:
            stmt = text("""
                INSERT INTO instruments (code, name, description, structure, version, is_active, created_at)
                VALUES (:code, :name, :description, :structure, :version, TRUE, CURRENT_TIMESTAMP)
            """)

            # Usar json.dumps para formatar corretamente a estrutura como JSON
            db.execute(stmt, {
                "code": processor.code,
                "name": processor.name,
                "description": processor.description,
                "structure": json.dumps(processor.structure),  # ALTERAÇÃO AQUI
                "version": processor.version
            })

            db.commit()
            print(f"    Instrumento '{processor.name}' adicionado com sucesso.")
        else:
            print(f"    Instrumento '{processor.name}' já existe.")

    except Exception as e:
        print(f"    Erro ao popular instrumentos: {str(e)}")
        return False

    return True


def update_database(drop_tables=False):
    """
    Atualiza o banco de dados com a nova estrutura de tabelas

    Args:
        drop_tables: Se True, remove as tabelas antigas antes de criar as novas
    """
    print("Iniciando atualização do banco de dados...")

    # Obter sessão do banco de dados
    db = next(db_connection.get_db())

    try:
        # Remover tabelas antigas se solicitado
        if drop_tables:
            drop_custom_tables(db)

        # Criar novas tabelas
        if not create_new_tables(db):
            print("Falha ao criar novas tabelas. Abortando.")
            return False

        # Popular tabela de instrumentos
        if not seed_instruments(db):
            print("Falha ao popular instrumentos. Atualização parcial.")
            return False

        print("Atualização do banco de dados concluída com sucesso!")
        return True

    except Exception as e:
        print(f"Erro durante a atualização do banco de dados: {str(e)}")
        return False

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Atualiza o banco de dados com a nova estrutura de tabelas.")
    parser.add_argument("--drop", action="store_true", help="Remove as tabelas antigas antes de criar as novas.")
    parser.add_argument("--force", action="store_true", help="Executa sem solicitar confirmação.")

    args = parser.parse_args()

    if args.drop and not args.force:
        print("ATENÇÃO: Esta operação removerá as tabelas do modelo antigo de tabelas customizadas.")
        print("         Todos os dados armazenados nessas tabelas serão perdidos.")

        if not confirm_action("Tem certeza que deseja continuar?"):
            print("Operação cancelada pelo usuário.")
            sys.exit(0)

    success = update_database(drop_tables=args.drop)

    if success:
        print("\nBanco de dados atualizado com sucesso!")
        print("\nPróximos passos:")
        print("1. Atualize os arquivos __init__.py conforme a nova estrutura")
        print("2. Atualize as rotas para usar os novos controllers de datasets e instrumentos")
        print("3. Implemente novos processadores de instrumentos conforme necessário")
    else:
        print("\nHouve problemas na atualização do banco de dados.")
        print("Verifique os erros acima e tente novamente.")

    sys.exit(0 if success else 1)