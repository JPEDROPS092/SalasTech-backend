#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de teste.
Este script é um wrapper para facilitar a execução do módulo de população do banco de dados.
"""

import os
import sys
import argparse
from sqlalchemy.orm import sessionmaker

# Adiciona o diretório src ao path do Python
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

# Importa as dependências necessárias
from SalasTech.app.core.db_context import engine, create_tables, recreate_tables
from SalasTech.app.utils.seed_database import seed_database


def main():
    """Função principal para execução do script."""
    parser = argparse.ArgumentParser(description="Popula o banco de dados com dados de teste.")
    parser.add_argument("--force", action="store_true", help="Força a recriação das tabelas antes de popular.")
    parser.add_argument("--check", action="store_true", help="Apenas verifica o banco de dados sem fazer alterações.")
    args = parser.parse_args()
    
    print("Sistema de Gerenciamento de Salas IFAM")
    print("======================================")
    print("Script de População do Banco de Dados")
    print("--------------------------------------")
    
    # Cria as tabelas se necessário ou se --force for especificado
    if args.force:
        from app.core.config import CONFIG
        import os
        
        # Se estiver usando SQLite, exclui o arquivo do banco de dados
        if CONFIG.DB_TYPE == "sqlite" and hasattr(CONFIG, "SQLITE_PATH"):
            sqlite_path = CONFIG.SQLITE_PATH
            if os.path.isabs(sqlite_path):
                db_file = sqlite_path
            else:
                # Se o caminho for relativo, considere-o relativo ao diretório do projeto
                db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), sqlite_path)
            
            if os.path.exists(db_file):
                print(f"\nRemovendo banco de dados SQLite existente: {db_file}")
                os.remove(db_file)
                print("Banco de dados removido com sucesso!")
        
        print("\nCriando novas tabelas do banco de dados...")
        recreate_tables()
        print("Tabelas criadas com sucesso!")
    else:
        # Apenas cria as tabelas se elas não existirem
        create_tables()
    
    # Se for apenas verificação, não prossegue com a população
    if args.check:
        print("\nVerificação concluída. Banco de dados está pronto.")
        return 0
    
    # Cria uma sessão
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Popula o banco de dados
        success = seed_database(session)
        if not success:
            return 1
    except Exception as e:
        session.rollback()
        print(f"\nErro ao popular o banco de dados: {e}")
        return 1
    finally:
        session.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
