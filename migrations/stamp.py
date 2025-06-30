#!/usr/bin/env python3
"""
Script para marcar migrações como já aplicadas sem executá-las.
Útil para situações onde o banco já existe mas o Alembic não está ciente.
"""

import sys
import argparse
from pathlib import Path

# Adicionar diretório do projeto ao path para importações
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from alembic import command
from alembic.config import Config


def stamp_revision(revision='head', sql=False, tag=None):
    """
    Marca uma revisão como aplicada sem executar a migração.
    
    Args:
        revision: ID da revisão ou 'head' para a mais recente
        sql: Se True, apenas imprime o SQL que seria executado
        tag: Tag opcional para a operação
    """
    # Carregar configuração do Alembic
    alembic_cfg = Config(str(Path(__file__).parent / "alembic.ini"))
    
    print(f"🔖 Marcando migração '{revision}' como aplicada...")
    
    # Executar o comando stamp
    command.stamp(alembic_cfg, revision, sql=sql, tag=tag)
    
    print("✅ Migração marcada com sucesso!")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Marca migrações como aplicadas sem executá-las")
    parser.add_argument("revision", nargs="?", default="head", 
                      help="ID da revisão ou 'head' para a mais recente (padrão)")
    parser.add_argument("--sql", action="store_true", help="Apenas imprimir o SQL (não executar)")
    parser.add_argument("--tag", help="Tag opcional para a operação")
    
    args = parser.parse_args()
    
    stamp_revision(args.revision, args.sql, args.tag)


if __name__ == "__main__":
    main()
