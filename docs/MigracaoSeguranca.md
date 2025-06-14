# Guia de Migração - Segurança Simplificada para React

Este guia explica como migrar da arquitetura de segurança baseada em cookies/sessões para a nova arquitetura JWT otimizada para React SPA.

## 🔄 Mudanças Principais

### ❌ **Removido (Arquitetura Antiga)**
- **Cookies de sessão**: `session.py` com gerenciamento de cookies
- **CSRF Protection**: `csrf.py` - desnecessário com JWT
- **SHA256 Hashing**: `sha256_hashing.py` - menos seguro
- **Sessões server-side**: Estado mantido no servidor

### ✅ **Adicionado (Nova Arquitetura)**
- **JWT Bearer Tokens**: Stateless authentication
- **Refresh Tokens**: Renovação automática de acesso
- **PasswordManager Unificado**: Apenas bcrypt
- **CORS Otimizado**: Configurado para React dev/prod
- **Middleware Simplificado**: Apenas Bearer tokens

## 📋 Checklist de Migração

### 1. **Atualize as Importações**

```python
# ❌ Antes (Cookies/Sessão)
from SalasTech.app.core.security.session import get_user, get_admin
from SalasTech.app.core.dependencies import user_dependency, admin_dependency

# ✅ Agora (JWT Bearer)
from SalasTech.app.core.security.middleware import get_current_user, get_admin_user
```

### 2. **Atualize os Endpoints**

```python
# ❌ Antes
@router.get("/protected")
def protected_route(user: dto.UserDTO = Depends(get_user)):
    return {"user_id": user.id}

# ✅ Agora  
@router.get("/protected")
async def protected_route(user: Dict[str, Any] = Depends(get_current_user)):
    return {"user_id": user["user_id"]}
```

### 3. **Atualize Autenticação**

```python
# ❌ Antes (Cookies)
@router.post("/login")
async def login(credentials: LoginDTO, response: Response):
    token = await session.login(credentials, response)
    return {"message": "Logged in"}

# ✅ Agora (JWT)
@router.post("/login")
async def login(credentials: LoginRequest):
    tokens = JWTManager.create_tokens(user_id, user_role)
    return TokenResponse(**tokens)
```

### 4. **Configure CORS**

```python
# main.py
from SalasTech.app.core.middlewares.cors import setup_cors

app = FastAPI()
setup_cors(app)  # Configuração automática para React
```

### 5. **Atualize Frontend (React)**

```javascript
// Configuração do Axios
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// Interceptor para adicionar token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para refresh automático
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await api.post('/auth/refresh', {
            refresh_token: refreshToken
          });
          
          localStorage.setItem('access_token', response.data.access_token);
          localStorage.setItem('refresh_token', response.data.refresh_token);
          
          // Retry original request
          error.config.headers.Authorization = `Bearer ${response.data.access_token}`;
          return api.request(error.config);
        } catch (refreshError) {
          localStorage.clear();
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);
```

## 🚀 Endpoints de Autenticação

### **POST /api/auth/login**
```json
{
  "email": "user@example.com",
  "password": "senha123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### **POST /api/auth/refresh**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### **GET /api/auth/me**
```javascript
// Headers: Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": "123",
  "email": "user@example.com", 
  "name": "João Silva",
  "role": "admin"
}
```

## 🔧 Configuração de Ambiente

```bash
# .env
JWT_SECRET_KEY=your-super-secret-key-here
FRONTEND_URL=https://yourapp.com
CORS_ORIGINS=https://app1.com,https://app2.com

# Para desenvolvimento
DB_TYPE=sqlite
SQLITE_PATH=db.sqlite
```

## ⚠️ Pontos de Atenção

### **Segurança**
- ✅ Access tokens curtos (15 min)
- ✅ Refresh tokens longos (7 dias)
- ✅ Tokens invalidados no logout (client-side)
- ✅ HTTPS obrigatório em produção

### **Performance**
- ✅ Stateless (não mantém sessão no servidor)
- ✅ Menor overhead de verificação
- ✅ Escalabilidade horizontal

### **Experiência do Usuário**
- ✅ Refresh automático transparente
- ✅ Sem redirects por expiração
- ✅ Estado mantido no frontend

## 🧪 Testando a Migração

### 1. **Teste de Login**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com", "password": "admin123"}'
```

### 2. **Teste de Acesso Protegido**
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. **Teste de Refresh**
```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

## 📚 Próximos Passos

1. **Migrar controladores existentes** para usar `get_current_user`
2. **Atualizar testes** para usar Bearer tokens
3. **Implementar rate limiting** se necessário
4. **Configurar monitoramento** de tokens inválidos/expirados
5. **Documentar API** com exemplos React

---

**🎉 Parabéns!** Sua aplicação agora tem uma arquitetura de segurança moderna e otimizada para SPAs React!
