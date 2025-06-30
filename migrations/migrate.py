#!/usr/bin/env python3
"""
Script wrapper simplificado para uso cotidiano
Comandos mais comuns do Migration Manager
"""

import sys
import subprocess
from pathlib import Path

def run_migration_manager(args):
    """Executa o migration manager com os argumentos fornecidos"""
    script_path = Path(__file__).parent / "migration_manager.py"
    cmd = [sys.executable, str(script_path)] + args
    return subprocess.run(cmd)

def main():
    if len(sys.argv) < 2:
        print("🛡️ SalasTech - Comandos Rápidos")
        print()
        print("Comandos disponíveis:")
        print("  migrate      - Aplica todas as migrações (upgrade head)")
        print("  new <msg>    - Cria nova migração")
        print("  rollback     - Volta uma migração (downgrade -1)")
        print("  status       - Mostra status atual")
        print("  backup       - Faz backup do banco")
        print("  reset        - Reset completo (cuidado!)")
        print("  check        - Verifica ambiente Alembic")
        print("  setup        - Configura ambiente Alembic")
        print("  stamp        - Marca migração como aplicada sem executá-la")
        print()
        print("Para comandos avançados, use: python migration_manager.py --help")
        return

    command = sys.argv[1]
    
    if command == "migrate":
        run_migration_manager(["upgrade"])
    
    elif command == "new":
        if len(sys.argv) < 3:
            print("❌ Informe a mensagem da migração")
            print("Exemplo: python migrate.py new 'Adicionar tabela de logs'")
            return
        message = " ".join(sys.argv[2:])
        run_migration_manager(["revision", "-m", message])
    
    elif command == "rollback":
        run_migration_manager(["downgrade", "-1"])
    
    elif command == "status":
        run_migration_manager(["status"])
    
    elif command == "backup":
        run_migration_manager(["backup"])
    
    elif command == "reset":
        run_migration_manager(["reset"])
        
    elif command == "check":
        # Importa e utiliza o módulo de verificação do ambiente Alembic
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from migrations.alembic_utils import check_alembic_environment
        if check_alembic_environment():
            print("✅ Ambiente Alembic está corretamente configurado!")
        else:
            print("❌ Ambiente Alembic não está corretamente configurado!")
            print("   Execute: python migrate.py setup")
            
    elif command == "setup":
        # Importa e utiliza o módulo de configuração do ambiente Alembic
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from migrations.alembic_utils import setup_alembic_environment
        if setup_alembic_environment():
            print("✅ Ambiente Alembic configurado com sucesso!")
        else:
            print("❌ Falha ao configurar ambiente Alembic!")
            
    elif command == "stamp":
        # Marca migração como aplicada sem executá-la
        revision = "head"
        if len(sys.argv) > 2:
            revision = sys.argv[2]
        
        # Importa e executa o módulo de stamp
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from migrations.stamp import stamp_revision
        stamp_revision(revision)
    
    else:
        print(f"❌ Comando '{command}' não reconhecido")
        print("Use sem argumentos para ver a ajuda")

if __name__ == "__main__":
    main()
