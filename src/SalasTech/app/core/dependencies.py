from typing import Annotated

from fastapi import Depends

from SalasTech.app.models import dto
from SalasTech.app.services import user_service


# Service dependencies
def get_user_service():
    """Dependency to provide user service"""
    return user_service

# Legacy dependencies (deprecated - use new middleware)
# Para compatibilidade com código antigo
token_dependency = None  # Deprecated
user_dependency = None   # Deprecated  
admin_dependency = None  # Deprecated