"""
Módulo de Administração SalasTech

Este módulo fornece um painel administrativo web completo
para gerenciar todas as funcionalidades do sistema SalasTech.
"""

from .config import setup_admin_routes, AdminAuth, AdminDashboard

__all__ = [
    "setup_admin_routes",
    "AdminAuth", 
    "AdminDashboard"
]
