#!/usr/bin/env python3
"""
Configurações para o Migration Manager
"""

import os
from pathlib import Path

# Configurações de banco de dados
DATABASE_CONFIG = {
    'sqlite': {
        'file': 'db.sqlite',
        'backup_prefix': 'db_backup_',
        'supports_transactions': True
    },
    'postgresql': {
        'file': None,
        'backup_prefix': 'pg_backup_',
        'supports_transactions': True
    },
    'mysql': {
        'file': None,
        'backup_prefix': 'mysql_backup_',
        'supports_transactions': True
    }
}

# Configurações de diretórios
DIRECTORIES = {
    'migrations': 'migrations',
    'backups': 'backups',
    'logs': 'logs'
}

# Configurações de logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/migration_manager.log'
}

# Configurações de segurança
SECURITY_CONFIG = {
    'require_confirmation_for_reset': True,
    'auto_backup_before_operations': True,
    'max_backups_to_keep': 10
}

# Configurações específicas do SalasTech
SALASTECH_CONFIG = {
    'app_name': 'SalasTech',
    'version': '2.0',
    'author': 'SalasTech Team',
    'description': 'Sistema de Reserva de Salas'
}
