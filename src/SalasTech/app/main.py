from fastapi import FastAPI
import logging
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.middleware.cors import CORSMiddleware

from SalasTech.app.core import lifespan
from SalasTech.app.controllers.pages import page_controller
from SalasTech.app.controllers.api import (
    auth_controller,
    user_controller,
    room_controller,
    reservation_controller,
    department_controller,
    report_controller
)

from SalasTech.app.core.middlewares import cors_middleware
from SalasTech.app.core.middlewares import static_middleware
from SalasTech.app.core.security import rate_limiter
from SalasTech.app.core.security import csrf
from SalasTech.app.exceptions import handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def custom_openapi():
    """
    Customiza a documentação OpenAPI com informações específicas do projeto.
    Inclui descrições detalhadas, termos de serviço e informações de contato.
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="TechSalas API",
        version="1.0.0",
        description="""
        Sistema de Gerenciamento de Salas API .
        
        ## Funcionalidades
        
        * Autenticação e Autorização
        * Gerenciamento de Usuários
        * Gerenciamento de Salas
        * Reservas de Salas
        * Gerenciamento de Departamentos
        * Geração de Relatórios
        
        ## Autenticação
        
        A API utiliza autenticação JWT (JSON Web Token). Para acessar endpoints protegidos:
        1. Faça login através do endpoint `/api/auth/login`
        2. Use o token retornado no header `Authorization: Bearer <token>`
        """,
        routes=app.routes,
        terms_of_service="http://ifam.edu.br/terms/",
        contact={
            "name": "Suporte IFAM",
            "url": "http://ifam.edu.br/support",
            "email": "suporte@ifam.edu.br",
        },
        license_info={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        },
    )
    
    # Adiciona tags com descrições para melhor organização
    openapi_schema["tags"] = [
        {
            "name": "Autenticação",
            "description": "Operações relacionadas à autenticação e autorização",
        },
        {
            "name": "Usuários",
            "description": "Gerenciamento de usuários do sistema",
        },
        {
            "name": "Salas",
            "description": "Operações de gerenciamento de salas",
        },
        {
            "name": "Reservas",
            "description": "Agendamento e gerenciamento de reservas",
        },
        {
            "name": "Departamentos",
            "description": "Gerenciamento de departamentos",
        },
        {
            "name": "Relatórios",
            "description": "Geração e download de relatórios",
        },
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Configuração principal do FastAPI
app = FastAPI(
    title="IFAM Sistema de Gerenciamento",
    description="API para o Sistema de Gerenciamento de Salas do IFAM",
    version="1.0.0",
    lifespan=lifespan.lifespan,
    docs_url=None,  # Desabilita o Swagger UI padrão
    redoc_url=None  # Desabilita o ReDoc padrão
)

# Configuração da API
api = FastAPI(
    title="IFAM API",
    description="API para o Sistema de Gerenciamento de Salas do IFAM",
    version="1.0.0",
    lifespan=lifespan.lifespan,
    openapi_tags=[{
        "name": tag["name"],
        "description": tag["description"]
    } for tag in custom_openapi()["tags"]]
)

# Endpoints para documentação customizada
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Endpoint que serve a interface Swagger UI customizada
    """
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title="IFAM Sistema de Gerenciamento - API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="/static/favicon.ico"
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """
    Endpoint que serve a interface ReDoc
    """
    return get_redoc_html(
        openapi_url="/api/openapi.json",
        title="IFAM Sistema de Gerenciamento - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )

# Configuração dos handlers de exceção
handler.add_html(app)
handler.add_json(api)

# Configuração de middlewares de segurança
static_middleware.add(app)  # Arquivos estáticos
cors_middleware.add(app)    # Proteção CORS para app principal
cors_middleware.add(api)    # Proteção CORS para API
rate_limiter.apply_rate_limiting(app)  # Rate limiting
csrf.apply_csrf_middleware(app)  # Proteção CSRF

# Log de inicialização
logger.info("Starting IFAM Sistema de Gerenciamento with enhanced security features")
logger.info("Applied security: CORS, Rate Limiting, CSRF Protection, Secure Cookies")

# Registro dos routers de páginas
app.include_router(page_controller.router)

# Registro dos routers da API com tags apropriadas
api.include_router(
    auth_controller.router,
    prefix="/auth",
    tags=["Autenticação"]
)
api.include_router(
    user_controller.router,
    prefix="/users",
    tags=["Usuários"]
)
api.include_router(
    room_controller.router,
    prefix="/rooms",
    tags=["Salas"]
)
api.include_router(
    reservation_controller.router,
    prefix="/reservations",
    tags=["Reservas"]
)
api.include_router(
    department_controller.router,
    prefix="/departments",
    tags=["Departamentos"]
)
api.include_router(
    report_controller.router,
    prefix="/reports",
    tags=["Relatórios"]
)

# Montagem da API
app.mount("/api", api)

# Configuração do schema OpenAPI customizado
app.openapi = custom_openapi
