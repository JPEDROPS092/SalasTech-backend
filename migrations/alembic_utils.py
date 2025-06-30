"""
Utilidades para verificação de ambiente do Alembic.
Este arquivo auxilia na configuração e verificação do ambiente de migrações.
"""

import os
import sys
from pathlib import Path


def check_alembic_environment():
    """
    Verifica se o ambiente do Alembic está corretamente configurado.
    
    Retorna:
        bool: True se o ambiente está ok, False caso contrário
    """
    try:
        from alembic import command
        from alembic.config import Config
        
        # Verifica se o arquivo alembic.ini existe
        migrations_dir = Path(__file__).parent
        alembic_ini = migrations_dir / "alembic.ini"
        if not alembic_ini.exists():
            print("❌ Arquivo alembic.ini não encontrado!")
            return False
        
        # Verifica se o diretório versions existe
        versions_dir = migrations_dir / "versions"
        if not versions_dir.exists():
            print("❌ Diretório versions não encontrado!")
            return False
        
        # Tenta carregar a configuração
        alembic_cfg = Config(str(alembic_ini))
        
        # Tudo ok
        return True
    
    except ImportError:
        print("❌ Alembic não está instalado! Execute: pip install alembic")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar ambiente Alembic: {e}")
        return False


def setup_alembic_environment():
    """
    Configura o ambiente do Alembic se necessário.
    
    Retorna:
        bool: True se a configuração foi bem sucedida, False caso contrário
    """
    migrations_dir = Path(__file__).parent
    
    # Verifica se o diretório versions existe, se não, cria
    versions_dir = migrations_dir / "versions"
    if not versions_dir.exists():
        print("📁 Criando diretório versions...")
        versions_dir.mkdir(exist_ok=True)
    
    # Verifica se o arquivo __init__.py existe em versions
    init_file = versions_dir / "__init__.py"
    if not init_file.exists():
        print("📄 Criando arquivo __init__.py em versions...")
        init_file.touch()
    
    return True


if __name__ == "__main__":
    # Se executado diretamente, verifica e configura o ambiente
    if check_alembic_environment():
        print("✅ Ambiente Alembic está corretamente configurado!")
    else:
        print("⚙️ Configurando ambiente Alembic...")
        if setup_alembic_environment():
            print("✅ Ambiente Alembic configurado com sucesso!")
        else:
            print("❌ Falha ao configurar ambiente Alembic!")
            sys.exit(1)
