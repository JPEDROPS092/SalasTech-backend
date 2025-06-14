"""
Módulo de Segurança Simplificado para React SPA

Este módulo fornece uma arquitetura de segurança simplificada e otimizada
para aplicações React Single Page Application (SPA).

Componentes principais:
- PasswordManager: Hash de senhas com bcrypt
- JWTManager: Gerenciamento de tokens JWT (access + refresh)
- Middleware: Autenticação e autorização para FastAPI
- CORS: Configuração para desenvolvimento e produção React

Benefícios da simplificação:
- Stateless authentication (ideal para SPA)
- Refresh token automático
- Sem dependência de cookies/sessões
- Sem CSRF (protegido por design JWT)
- Configuração CORS otimizada para React

Exemplo de uso:

```python
from SalasTech.app.core.security import PasswordManager, JWTManager
from SalasTech.app.core.security.middleware import get_current_user

# Hash de senha
hashed = PasswordManager.hash_password("senha123")

# Criar tokens
tokens = JWTManager.create_tokens("user_id", "admin")

# Usar em endpoints FastAPI
@router.get("/protected")
async def protected_route(user = Depends(get_current_user)):
    return {"user": user}
```
"""

# Principais componentes exportados
from .password import PasswordManager
from .auth import JWTManager
from .middleware import get_current_user, get_admin_user, get_optional_user

# Componentes legados (deprecated)
from . import bcrypt_hashing  # Para migração gradual
from SalasTech.app.core.security.auth import JWTManager
from SalasTech.app.core.security.password import PasswordManager


__all__ = [
    # Nova arquitetura (recomendado)
    "PasswordManager",
    "JWTManager", 
    "get_current_user",
    "get_admin_user",
    "get_optional_user",
    
    # Legado (deprecated)
    "bcrypt_hashing",
    "jwt_legacy",
]
