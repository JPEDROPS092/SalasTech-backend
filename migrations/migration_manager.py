#!/usr/bin/env python3
"""
🛡️ SalasTech Migration Manager
Script para gerenciar migrações de banco de dados com Alembic
Versão Python com recursos avançados
"""

import os
import sys
import shutil
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List


class Colors:
    """Cores para output no terminal"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color


class MigrationManager:
    """Gerenciador de migrações para SalasTech"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.migrations_dir = self.project_root / "migrations"
        self.alembic_ini = self.migrations_dir / "alembic.ini"
        self.db_file = self.project_root / "db.sqlite"
        self.backup_dir = self.project_root / "backups"
        
    def show_header(self):
        """Mostra header do aplicativo"""
        print(f"{Colors.BLUE}🛡️ ==============================================={Colors.NC}")
        print(f"{Colors.BLUE}   SalasTech - Migration Manager v2.0 (Python){Colors.NC}")
        print(f"{Colors.BLUE}   Gerenciador de Migrações de Banco de Dados{Colors.NC}")
        print(f"{Colors.BLUE}🛡️ ==============================================={Colors.NC}")
        print()
    
    def check_dependencies(self):
        """Verifica se as dependências estão instaladas"""
        try:
            import alembic
            print(f"{Colors.GREEN}✅ Alembic encontrado: {alembic.__version__}{Colors.NC}")
        except ImportError:
            print(f"{Colors.RED}❌ Alembic não instalado!{Colors.NC}")
            print(f"{Colors.YELLOW}💡 Execute: pip install alembic{Colors.NC}")
            sys.exit(1)
    
    def check_directory(self):
        """Verifica se estamos no diretório correto"""
        if not self.alembic_ini.exists():
            print(f"{Colors.RED}❌ Execute este script da raiz do projeto SalasTech!{Colors.NC}")
            print(f"{Colors.YELLOW}💡 Diretório atual: {self.project_root}{Colors.NC}")
            print(f"{Colors.YELLOW}💡 Procurando por: {self.alembic_ini}{Colors.NC}")
            sys.exit(1)
        
        print(f"{Colors.GREEN}✅ Diretório correto encontrado{Colors.NC}")
    
    def backup_database(self) -> Optional[Path]:
        """Faz backup do banco de dados"""
        if not self.db_file.exists():
            print(f"{Colors.YELLOW}⚠️  Arquivo db.sqlite não encontrado{Colors.NC}")
            return None
        
        self.backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"db_backup_{timestamp}.sqlite"
        
        try:
            shutil.copy2(self.db_file, backup_file)
            print(f"{Colors.GREEN}✅ Backup criado: {backup_file}{Colors.NC}")
            return backup_file
        except Exception as e:
            print(f"{Colors.RED}❌ Erro ao criar backup: {e}{Colors.NC}")
            return None
    
    def run_alembic(self, command: str, args: Optional[List[str]] = None) -> bool:
        """Executa comandos do alembic"""
        if args is None:
            args = []
        
        cmd = ["alembic", "-c", str(self.alembic_ini), command] + args
        print(f"{Colors.BLUE}🔄 Executando: {' '.join(cmd)}{Colors.NC}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=False)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}❌ Erro ao executar comando: {e}{Colors.NC}")
            return False
        except FileNotFoundError:
            print(f"{Colors.RED}❌ Alembic não encontrado no PATH{Colors.NC}")
            return False
    
    def init_alembic(self):
        """Inicializa o Alembic"""
        print(f"{Colors.BLUE}🚀 Inicializando Alembic...{Colors.NC}")
        
        versions_dir = self.migrations_dir / "versions"
        if versions_dir.exists() and list(versions_dir.glob("*.py")):
            print(f"{Colors.YELLOW}⚠️  Migrações já existem!{Colors.NC}")
            response = input("Deseja continuar? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print(f"{Colors.YELLOW}❌ Operação cancelada{Colors.NC}")
                return
        
        if self.run_alembic("init", [str(self.migrations_dir)]):
            print(f"{Colors.GREEN}✅ Alembic inicializado!{Colors.NC}")
        else:
            print(f"{Colors.RED}❌ Falha ao inicializar Alembic{Colors.NC}")
    
    def create_revision(self, message: str, autogenerate: bool = True):
        """Cria nova migração"""
        print(f"{Colors.BLUE}📝 Criando nova migração...{Colors.NC}")
        
        if not message:
            print(f"{Colors.RED}❌ Mensagem da migração é obrigatória{Colors.NC}")
            return
        
        self.backup_database()
        
        args = ["--autogenerate"] if autogenerate else []
        args.extend(["-m", message])
        
        if self.run_alembic("revision", args):
            print(f"{Colors.GREEN}✅ Migração criada!{Colors.NC}")
        else:
            print(f"{Colors.RED}❌ Falha ao criar migração{Colors.NC}")
    
    def upgrade(self, target: str = "head"):
        """Aplica migrações"""
        print(f"{Colors.BLUE}⬆️  Aplicando migrações até: {target}{Colors.NC}")
        
        self.backup_database()
        
        if self.run_alembic("upgrade", [target]):
            print(f"{Colors.GREEN}✅ Migrações aplicadas!{Colors.NC}")
        else:
            print(f"{Colors.RED}❌ Falha ao aplicar migrações{Colors.NC}")
    
    def downgrade(self, target: str = "-1"):
        """Reverte migrações"""
        print(f"{Colors.BLUE}⬇️  Revertendo migrações para: {target}{Colors.NC}")
        
        self.backup_database()
        
        if self.run_alembic("downgrade", [target]):
            print(f"{Colors.GREEN}✅ Migrações revertidas!{Colors.NC}")
        else:
            print(f"{Colors.RED}❌ Falha ao reverter migrações{Colors.NC}")
    
    def show_current(self):
        """Mostra migração atual"""
        print(f"{Colors.BLUE}📍 Migração atual:{Colors.NC}")
        self.run_alembic("current")
    
    def show_history(self):
        """Mostra histórico de migrações"""
        print(f"{Colors.BLUE}📜 Histórico de migrações:{Colors.NC}")
        self.run_alembic("history", ["--verbose"])
    
    def show_status(self):
        """Mostra status das migrações"""
        print(f"{Colors.BLUE}📊 Status das migrações:{Colors.NC}")
        self.run_alembic("show", ["head"])
        print()
        print(f"{Colors.BLUE}📍 Migração atual:{Colors.NC}")
        self.run_alembic("current")
    
    def reset_database(self):
        """Reset completo do banco"""
        print(f"{Colors.RED}⚠️  ATENÇÃO: Isso vai resetar TODAS as migrações!{Colors.NC}")
        print(f"{Colors.RED}⚠️  O banco de dados será recriado do zero!{Colors.NC}")
        
        confirm = input("Tem certeza? Digite 'RESET' para confirmar: ").strip()
        if confirm != "RESET":
            print(f"{Colors.YELLOW}❌ Reset cancelado{Colors.NC}")
            return
        
        self.backup_database()
        print(f"{Colors.BLUE}🔄 Fazendo reset completo...{Colors.NC}")
        
        # Downgrade para base
        if self.run_alembic("downgrade", ["base"]):
            # Remove banco
            if self.db_file.exists():
                self.db_file.unlink()
            
            # Upgrade para head
            if self.run_alembic("upgrade", ["head"]):
                print(f"{Colors.GREEN}✅ Reset completo realizado!{Colors.NC}")
            else:
                print(f"{Colors.RED}❌ Falha no upgrade após reset{Colors.NC}")
        else:
            print(f"{Colors.RED}❌ Falha no downgrade{Colors.NC}")
    
    def list_backups(self):
        """Lista backups disponíveis"""
        if not self.backup_dir.exists():
            print(f"{Colors.YELLOW}📁 Nenhum backup encontrado{Colors.NC}")
            return
        
        backups = list(self.backup_dir.glob("db_backup_*.sqlite"))
        if not backups:
            print(f"{Colors.YELLOW}📁 Nenhum backup encontrado{Colors.NC}")
            return
        
        print(f"{Colors.BLUE}📁 Backups disponíveis:{Colors.NC}")
        for backup in sorted(backups, reverse=True):
            size = backup.stat().st_size / 1024  # KB
            mtime = datetime.fromtimestamp(backup.stat().st_mtime)
            print(f"  {Colors.GREEN}•{Colors.NC} {backup.name} ({size:.1f}KB) - {mtime.strftime('%d/%m/%Y %H:%M:%S')}")
    
    def restore_backup(self, backup_name: Optional[str] = None):
        """Restaura backup específico"""
        if not backup_name:
            self.list_backups()
            backup_name = input(f"\n{Colors.YELLOW}Digite o nome do backup para restaurar: {Colors.NC}").strip()
        
        backup_file = self.backup_dir / backup_name
        if not backup_file.exists():
            print(f"{Colors.RED}❌ Backup não encontrado: {backup_name}{Colors.NC}")
            return
        
        print(f"{Colors.YELLOW}⚠️  Isso vai sobrescrever o banco atual!{Colors.NC}")
        confirm = input("Continuar? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print(f"{Colors.YELLOW}❌ Restauração cancelada{Colors.NC}")
            return
        
        try:
            shutil.copy2(backup_file, self.db_file)
            print(f"{Colors.GREEN}✅ Backup restaurado: {backup_name}{Colors.NC}")
        except Exception as e:
            print(f"{Colors.RED}❌ Erro ao restaurar backup: {e}{Colors.NC}")


def create_parser():
    """Cria parser de argumentos"""
    parser = argparse.ArgumentParser(
        description="🛡️ SalasTech Migration Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.GREEN}Exemplos de uso:{Colors.NC}
  {Colors.BLUE}python migration_manager.py revision -m "Adicionar tabela de logs"{Colors.NC}
  {Colors.BLUE}python migration_manager.py upgrade{Colors.NC}
  {Colors.BLUE}python migration_manager.py downgrade -1{Colors.NC}
  {Colors.BLUE}python migration_manager.py backup{Colors.NC}
  {Colors.BLUE}python migration_manager.py status{Colors.NC}
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Init
    subparsers.add_parser('init', help='Inicializar Alembic (primeira vez)')
    
    # Revision
    revision_parser = subparsers.add_parser('revision', help='Criar nova migração')
    revision_parser.add_argument('-m', '--message', required=True, help='Mensagem da migração')
    revision_parser.add_argument('--no-autogenerate', action='store_true', help='Não gerar automaticamente')
    
    # Upgrade
    upgrade_parser = subparsers.add_parser('upgrade', help='Aplicar migrações')
    upgrade_parser.add_argument('target', nargs='?', default='head', help='Target da migração (padrão: head)')
    
    # Downgrade
    downgrade_parser = subparsers.add_parser('downgrade', help='Reverter migrações')
    downgrade_parser.add_argument('target', nargs='?', default='-1', help='Target da migração (padrão: -1)')
    
    # Status commands
    subparsers.add_parser('current', help='Mostrar migração atual')
    subparsers.add_parser('history', help='Mostrar histórico de migrações')
    subparsers.add_parser('status', help='Status do banco vs migrações')
    
    # Backup commands
    subparsers.add_parser('backup', help='Fazer backup do banco')
    subparsers.add_parser('list-backups', help='Listar backups disponíveis')
    restore_parser = subparsers.add_parser('restore', help='Restaurar backup')
    restore_parser.add_argument('backup_name', nargs='?', help='Nome do backup para restaurar')
    
    # Reset
    subparsers.add_parser('reset', help='Reset completo (CUIDADO!)')
    
    return parser


def main():
    """Função principal"""
    parser = create_parser()
    args = parser.parse_args()
    
    manager = MigrationManager()
    manager.show_header()
    manager.check_dependencies()
    manager.check_directory()
    
    if not args.command:
        parser.print_help()
        return
    
    command = args.command
    
    if command == 'init':
        manager.init_alembic()
    
    elif command == 'revision':
        autogenerate = not args.no_autogenerate
        manager.create_revision(args.message, autogenerate)
    
    elif command == 'upgrade':
        manager.upgrade(args.target)
    
    elif command == 'downgrade':
        manager.downgrade(args.target)
    
    elif command == 'current':
        manager.show_current()
    
    elif command == 'history':
        manager.show_history()
    
    elif command == 'status':
        manager.show_status()
    
    elif command == 'backup':
        manager.backup_database()
    
    elif command == 'list-backups':
        manager.list_backups()
    
    elif command == 'restore':
        manager.restore_backup(args.backup_name)
    
    elif command == 'reset':
        manager.reset_database()
    
    else:
        print(f"{Colors.RED}❌ Comando '{command}' não reconhecido{Colors.NC}")
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}❌ Operação cancelada pelo usuário{Colors.NC}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}❌ Erro inesperado: {e}{Colors.NC}")
        sys.exit(1)
