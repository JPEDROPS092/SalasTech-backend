"""Script de verificação de integridade das migrações

Este script compara o estado do banco de dados atual com as migrações aplicadas
e identifica possíveis discrepâncias.

Uso:
  python check_migrations.py

Saída:
  Relatório de integridade das migrações
"""

import sys
import sqlite3
from pathlib import Path
from sqlalchemy import create_engine, MetaData, inspect
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic import command

# Adicionar diretório do projeto ao path para importações
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from app.core.config import Config as AppConfig
    from app.models.db import Base
except ImportError:
    print("⚠️ Não foi possível importar os modelos da aplicação.")
    print("⚠️ O relatório pode não ser completo.")
    Base = None
    AppConfig = None


def get_db_url():
    """Obtém a URL do banco de dados"""
    try:
        if AppConfig:
            app_config = AppConfig.get_config()
            return app_config.DB_CONNECTION_STRING
    except Exception:
        pass
    
    # Fallback para SQLite padrão
    return "sqlite:///db.sqlite"


def check_alembic_table():
    """Verifica se a tabela de versões do alembic existe"""
    try:
        conn = sqlite3.connect("db.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] == 'alembic_version':
            return True, "A tabela de controle alembic_version existe."
        else:
            return False, "❌ Tabela alembic_version não encontrada. O Alembic não está inicializado."
    except Exception as e:
        return False, f"❌ Erro ao verificar tabela alembic_version: {e}"


def get_current_revision():
    """Obtém a revisão atual do Alembic"""
    try:
        conn = sqlite3.connect("db.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT version_num FROM alembic_version")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return True, f"Revisão atual: {result[0]}"
        else:
            return False, "❌ Nenhuma revisão encontrada na tabela alembic_version."
    except Exception as e:
        return False, f"❌ Erro ao verificar revisão atual: {e}"


def check_table_existence():
    """Verifica se as tabelas definidas nos modelos existem no banco"""
    if not Base:
        return None, "⚠️ Não foi possível verificar tabelas (modelos não importados)"
    
    try:
        engine = create_engine(get_db_url())
        inspector = inspect(engine)
        db_tables = inspector.get_table_names()
        
        model_tables = [table.name for table in Base.metadata.tables.values()]
        
        missing_tables = [t for t in model_tables if t not in db_tables]
        extra_tables = [t for t in db_tables if t not in model_tables and t != 'alembic_version']
        
        status = True
        messages = []
        
        if missing_tables:
            status = False
            messages.append(f"❌ Tabelas definidas nos modelos mas não encontradas no banco: {', '.join(missing_tables)}")
        
        if extra_tables:
            messages.append(f"⚠️ Tabelas encontradas no banco mas não definidas nos modelos: {', '.join(extra_tables)}")
        
        if not missing_tables and not extra_tables:
            messages.append("✅ Todas as tabelas dos modelos estão presentes no banco.")
        
        return status, "\n".join(messages)
    except Exception as e:
        return False, f"❌ Erro ao verificar tabelas: {e}"


def check_pending_migrations():
    """Verifica se há migrações pendentes"""
    try:
        engine = create_engine(get_db_url())
        connection = engine.connect()
        
        context = MigrationContext.configure(connection)
        alembic_cfg = Config(str(Path(__file__).parent / "alembic.ini"))
        
        with engine.begin() as conn:
            if Base:
                diff = compare_metadata(context, Base.metadata)
                if diff:
                    return False, f"❌ Há diferenças entre o banco e os modelos. {len(diff)} alterações pendentes."
                else:
                    return True, "✅ Não há diferenças entre o banco e os modelos."
            else:
                return None, "⚠️ Não foi possível verificar diferenças (modelos não importados)"
    except Exception as e:
        return False, f"❌ Erro ao verificar migrações pendentes: {e}"


def run_alembic_check():
    """Executa verificações do Alembic"""
    try:
        alembic_cfg = Config(str(Path(__file__).parent / "alembic.ini"))
        command.check(alembic_cfg)
        return True, "✅ Verificação do Alembic não encontrou problemas."
    except Exception as e:
        return False, f"❌ Verificação do Alembic encontrou problemas: {e}"


def main():
    """Função principal"""
    print("🔍 Verificação de Integridade das Migrações")
    print("===========================================")
    
    # Verifica tabela do Alembic
    status, message = check_alembic_table()
    print(f"\n📋 Tabela de controle Alembic: {'✅' if status else '❌'}")
    print(f"  {message}")
    
    # Verifica revisão atual
    status, message = get_current_revision()
    print(f"\n📋 Revisão Alembic: {'✅' if status else '❌'}")
    print(f"  {message}")
    
    # Verifica existência de tabelas
    status, message = check_table_existence()
    print(f"\n📋 Verificação de tabelas: {'✅' if status else '⚠️' if status is None else '❌'}")
    for line in message.split('\n'):
        print(f"  {line}")
    
    # Verifica migrações pendentes
    status, message = check_pending_migrations()
    print(f"\n📋 Migrações pendentes: {'✅' if status else '⚠️' if status is None else '❌'}")
    print(f"  {message}")
    
    # Executa verificação do Alembic
    status, message = run_alembic_check()
    print(f"\n📋 Verificação Alembic: {'✅' if status else '❌'}")
    print(f"  {message}")
    
    print("\n===========================================")
    print("🔍 Verificação concluída!")


if __name__ == "__main__":
    main()
