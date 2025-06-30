#!/usr/bin/env python3
"""
Migration Manager - Script de Recuperação e Sincronização

Este script identifica e resolve inconsistências entre o banco de dados
e as migrações do Alembic, permitindo sincronizar uma base de dados
existente com o sistema de controle de migrações.
"""

import os
import sys
import sqlite3
import argparse
import datetime
import shutil
from pathlib import Path

# Importar configurações
from migration_config import DATABASE_CONFIG, DIRECTORIES, SECURITY_CONFIG


def get_db_tables(db_path):
    """Obtém a lista de tabelas existentes no banco SQLite"""
    if not os.path.exists(db_path):
        return []
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Consulta para obter todas as tabelas (exceto sqlite_sequence)
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        return tables
    except sqlite3.Error as e:
        print(f"❌ Erro ao consultar banco de dados: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_alembic_version():
    """Verifica se a tabela alembic_version existe e obtém a versão"""
    db_path = DATABASE_CONFIG['sqlite']['file']
    if not os.path.exists(db_path):
        return None
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a tabela alembic_version existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='alembic_version'
        """)
        
        if not cursor.fetchone():
            return None
            
        # Obter a versão atual
        cursor.execute("SELECT version_num FROM alembic_version")
        row = cursor.fetchone()
        return row[0] if row else None
    except sqlite3.Error as e:
        print(f"❌ Erro ao consultar versão do Alembic: {e}")
        return None
    finally:
        if conn:
            conn.close()


def create_alembic_version_table(version_id):
    """Cria a tabela alembic_version e define a versão atual"""
    db_path = DATABASE_CONFIG['sqlite']['file']
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Criar tabela alembic_version se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alembic_version (
                version_num VARCHAR(32) NOT NULL
            )
        """)
        
        # Verificar se já existe um registro
        cursor.execute("SELECT COUNT(*) FROM alembic_version")
        count = cursor.fetchone()[0]
        
        if count > 0:
            # Atualizar versão existente
            cursor.execute("UPDATE alembic_version SET version_num = ?", (version_id,))
        else:
            # Inserir nova versão
            cursor.execute("INSERT INTO alembic_version (version_num) VALUES (?)", (version_id,))
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"❌ Erro ao criar tabela alembic_version: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def backup_database():
    """Cria um backup do banco de dados atual"""
    db_path = DATABASE_CONFIG['sqlite']['file']
    if not os.path.exists(db_path):
        print(f"⚠️ Banco de dados não encontrado para backup: {db_path}")
        return None
    
    # Criar diretório de backups se não existir
    backup_dir = DIRECTORIES['backups']
    os.makedirs(backup_dir, exist_ok=True)
    
    # Gerar nome do arquivo de backup com timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_prefix = DATABASE_CONFIG['sqlite']['backup_prefix']
    backup_file = os.path.join(backup_dir, f"{backup_prefix}{timestamp}.sqlite")
    
    # Copiar o arquivo do banco para o backup
    try:
        shutil.copy2(db_path, backup_file)
        print(f"✅ Backup criado: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return None


def sync_database_with_migrations():
    """Sincroniza o banco de dados existente com o sistema de migrações"""
    # Verificar se o banco existe e tem tabelas
    db_path = DATABASE_CONFIG['sqlite']['file']
    if not os.path.exists(db_path):
        print(f"⚠️ Banco de dados não encontrado: {db_path}")
        return False
    
    # Obter tabelas existentes
    tables = get_db_tables(db_path)
    if not tables:
        print("⚠️ Banco de dados vazio ou inacessível")
        return False
    
    print(f"📊 Tabelas encontradas no banco: {', '.join(tables)}")
    
    # Verificar se já existe controle de versão do Alembic
    current_version = get_alembic_version()
    if current_version:
        print(f"✅ Controle de versão do Alembic já existe: {current_version}")
        return True
    
    # Se tem tabelas mas não tem controle de versão, precisamos sincronizar
    print("🔄 Banco de dados existente sem controle de versão do Alembic")
    
    # Verificar as migrações disponíveis
    versions_dir = os.path.join(DIRECTORIES['migrations'], 'versions')
    if not os.path.exists(versions_dir):
        print(f"❌ Diretório de versões não encontrado: {versions_dir}")
        return False
    
    # Encontrar a migração mais recente (assumindo que o arquivo com 'initial' é o inicial)
    migration_files = [f for f in os.listdir(versions_dir) if f.endswith('.py') and not f.startswith('__')]
    
    if not migration_files:
        print("❌ Nenhum arquivo de migração encontrado")
        return False
    
    # Procurar a migração inicial
    initial_migration = None
    for file in migration_files:
        if 'initial' in file.lower():
            with open(os.path.join(versions_dir, file), 'r') as f:
                content = f.read()
                # Extrair a revision ID
                for line in content.split('\n'):
                    if line.startswith('revision = '):
                        initial_migration = line.split('=')[1].strip().strip("'\"")
                        break
            if initial_migration:
                break
    
    if not initial_migration:
        print("❌ Não foi possível identificar a migração inicial")
        return False
    
    # Criar backup antes de modificar
    backup = backup_database()
    if not backup:
        print("⚠️ Não foi possível criar backup, operação cancelada")
        return False
    
    # Criar a tabela alembic_version e definir a versão
    if create_alembic_version_table(initial_migration):
        print(f"✅ Banco sincronizado com a migração inicial: {initial_migration}")
        return True
    else:
        print("❌ Falha ao sincronizar banco com migrações")
        return False


def main():
    parser = argparse.ArgumentParser(description="🛡️ SalasTech Migration Recovery")
    parser.add_argument('--sync', action='store_true', help="Sincronizar banco existente com migrações")
    parser.add_argument('--force', action='store_true', help="Forçar operação sem confirmação")
    parser.add_argument('--version', type=str, help="Versão específica para definir")
    args = parser.parse_args()
    
    print("🛡️ ===============================================")
    print("   SalasTech - Migration Recovery v1.0")
    print("   Recuperação e Sincronização de Migrações")
    print("🛡️ ===============================================")
    print()
    
    if args.sync:
        if not args.force:
            confirm = input("⚠️ Esta operação vai modificar o banco. Continuar? (s/N): ")
            if confirm.lower() != 's':
                print("❌ Operação cancelada pelo usuário")
                return
                
        if sync_database_with_migrations():
            print("✅ Banco de dados sincronizado com o sistema de migrações")
            print("\n🔍 Agora você pode executar normalmente:")
            print("  python migration_manager.py status")
            print("  python migration_manager.py revision -m \"Nova migração\"")
        else:
            print("❌ Falha ao sincronizar banco de dados")
    elif args.version:
        if not args.force:
            confirm = input(f"⚠️ Definir versão para '{args.version}'. Continuar? (s/N): ")
            if confirm.lower() != 's':
                print("❌ Operação cancelada pelo usuário")
                return
                
        backup_database()
        if create_alembic_version_table(args.version):
            print(f"✅ Versão do banco definida para: {args.version}")
        else:
            print("❌ Falha ao definir versão do banco")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
