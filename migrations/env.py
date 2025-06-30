"""
Arquivo de configuração do ambiente Alembic para migrações de banco de dados.

Este arquivo é responsável por:
- Configurar a conexão com o banco de dados
- Importar os modelos para auto-geração de migrações
- Definir o contexto de execução das migrações
"""

import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path
import sys

from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context

# Adicionar o diretório do projeto ao path para importar os modelos
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Importar configuração e modelos
from app.core.config import Config
from app.models.db import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_database_url():
    """
    Obtém a URL do banco de dados a partir da configuração da aplicação.
    """
    try:
        app_config = Config.get_config()
        return app_config.DB_CONNECTION_STRING
    except Exception as e:
        # Fallback para SQLite se não conseguir carregar a configuração
        print(f"⚠️  Aviso: Não foi possível carregar configuração do banco ({e})")
        print("📂 Usando SQLite padrão: sqlite:///db.sqlite")
        return "sqlite:///db.sqlite"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Sobrescrever a URL no arquivo de configuração
    config.set_main_option("sqlalchemy.url", get_database_url())
    
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            # Opções específicas para melhor detecção de mudanças
            include_object=include_object,
            render_as_batch=True,  # Necessário para SQLite
        )

        with context.begin_transaction():
            context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    """
    Função para controlar quais objetos devem ser incluídos nas migrações.
    
    Útil para filtrar tabelas, índices ou constraints específicos.
    """
    # Se for uma tabela que não está no modelo, não incluí-la na migração
    if type_ == "table" and reflected and name not in Base.metadata.tables:
        return False
    
    # Incluir todos os outros objetos
    return True


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
