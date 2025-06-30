# -*- coding: utf-8 -*-
"""
Módulo Principal da Aplicação SalasTech

Este é o ponto de entrada principal para a aplicação SalasTech, um sistema de gerenciamento 
de salas para o IFAM. O módulo configura a aplicação FastAPI com todas as dependências,
middlewares de segurança, controladores de API e documentação personalizada.

Características principais:
- Configuração de autenticação JWT
- Middleware de segurança (CORS, Rate Limiting, CSRF)
- Documentação OpenAPI personalizada
- Integração com controladores de API
- Sistema de logs estruturado

Autor: Equipe SalasTech
Data: Junho 2025
Versão: 1.0.0
"""

import os
import logging
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

# Importações do núcleo da aplicação
from app.core.lifespan import lifespan

# Importação do painel administrativo
from app.admin.config import setup_admin_routes

# Importações dos controladores da API
from app.controllers.api import (
    user_controller,           # Controlador de usuários
    room_controller,           # Controlador de salas
    reservation_controller,    # Controlador de reservas
    department_controller,     # Controlador de departamentos
    report_controller          # Controlador de relatórios
)

# Controlador de autenticação
from app.controllers.api.auth import router as auth_router

# Configuração do sistema de logs
os.makedirs("logs", exist_ok=True)  # Criar diretório de logs se não existir

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/salastech.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def custom_openapi():
    """
    Personaliza a documentação OpenAPI com informações específicas do projeto.
    
    Esta função cria um esquema OpenAPI customizado que inclui:
    - Informações detalhadas sobre a API
    - Termos de serviço e informações de contato
    - Tags organizacionais para os endpoints
    - Descrições das funcionalidades principais
    
    Returns:
        dict: Esquema OpenAPI personalizado
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="SalasTech API - Sistema de Gerenciamento de Salas IFAM",
        version="1.0.0",
        description="""
        ## Sistema de Gerenciamento de Salas - Instituto Federal do Amazonas
        
        API RESTful completa para o gerenciamento de salas e reservas do IFAM.
        Desenvolvida com FastAPI, oferece alta performance e documentação automática.
        
        ### Funcionalidades Principais
        
        * **Autenticação e Autorização**: Sistema JWT com controle de acesso baseado em papéis
        * **Gerenciamento de Usuários**: CRUD completo para usuários do sistema
        * **Administração de Salas**: Controle de salas, capacidades e recursos disponíveis
        * **Sistema de Reservas**: Agendamento inteligente com validação de conflitos
        * **Gestão de Departamentos**: Organização hierárquica dos departamentos
        * **Relatórios Avançados**: Geração de relatórios em múltiplos formatos
        
        ### Autenticação
        
        A API utiliza autenticação JWT (JSON Web Token). Para acessar endpoints protegidos:
        
        1. Faça login através do endpoint `/auth/login`
        2. Use o token retornado no header `Authorization: Bearer <seu_token>`
        3. O token é válido por 24 horas por padrão
        
        ### Códigos de Status HTTP
        
        * `200` - Sucesso
        * `201` - Criado com sucesso
        * `400` - Erro na requisição (dados inválidos)
        * `401` - Não autorizado (token inválido/expirado)
        * `403` - Acesso negado (permissões insuficientes)
        * `404` - Recurso não encontrado
        * `409` - Conflito (dados duplicados)
        * `422` - Erro de validação
        * `500` - Erro interno do servidor
        """,
        routes=app.routes,
        terms_of_service="https://portal.ifam.edu.br/termos-de-uso/",
        contact={
            "name": "Suporte Técnico IFAM - SalasTech",
            "url": "https://portal.ifam.edu.br/suporte",
            "email": "salastech@ifam.edu.br",
        },
        license_info={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        },
    )
    
    # Adiciona tags organizacionais com descrições detalhadas para melhor navegação na documentação
    openapi_schema["tags"] = [
        {
            "name": "Sistema",
            "description": "Endpoints de monitoramento e saúde do sistema. "
                          "Inclui verificação de status e informações da aplicação.",
        },
        {
            "name": "Autenticação",
            "description": "Operações de login, logout e gerenciamento de tokens JWT. "
                          "Inclui endpoints para autenticação, renovação de tokens e validação de permissões.",
        },
        {
            "name": "Usuários",
            "description": "Gerenciamento completo de usuários do sistema. "
                          "Inclui operações CRUD, controle de papéis e gerenciamento de perfis.",
        },
        {
            "name": "Salas",
            "description": "Administração de salas e seus recursos. "
                          "Controle de capacidade, equipamentos disponíveis e status das salas.",
        },
        {
            "name": "Reservas",
            "description": "Sistema de agendamento e gerenciamento de reservas. "
                          "Inclui validação de conflitos, aprovações e cancelamentos.",
        },
        {
            "name": "Departamentos",
            "description": "Gestão organizacional dos departamentos. "
                          "Controle hierárquico e atribuição de responsabilidades.",
        },
        {
            "name": "Relatórios",
            "description": "Geração de relatórios analíticos e estatísticos. "
                          "Exportação em múltiplos formatos (PDF, Excel, CSV).",
        },
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Configuração principal da aplicação FastAPI
app = FastAPI(
    title="SalasTech - Sistema de Gerenciamento de Salas IFAM",
    description="API para o Sistema de Gerenciamento de Salas do Instituto Federal do Amazonas",
    version="1.0.0",
    lifespan=lifespan,
    openapi_url="/openapi.json",  # URL padrão para o esquema OpenAPI
    docs_url="/docs",             # URL padrão para a documentação Swagger
    redoc_url="/redoc"           # URL padrão para a documentação ReDoc
)

# Configuração do middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicionar middleware de sessão para o painel administrativo
from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "salastech-admin-secret-key-change-in-production"),
    max_age=3600 * 24,  # 24 horas
    same_site="lax",
    https_only=False,  # Mudar para True em produção com HTTPS
)

# Endpoint de health check
@app.get("/health", tags=["Sistema"])
async def health_check():
    """
    Endpoint de verificação de saúde da aplicação
    
    Returns:
        dict: Status da aplicação e informações básicas
    """
    return {
        "status": "healthy",
        "service": "SalasTech API",
        "version": "1.0.0",
        "message": "Sistema funcionando corretamente"
    }

# Endpoint da raiz da aplicação
@app.get("/", tags=["Sistema"])
async def root():
    """
    Endpoint raiz da aplicação
    
    Returns:
        dict: Informações básicas da API
    """
    return {
        "message": "SalasTech API - Sistema de Gerenciamento de Salas IFAM",
        "version": "1.0.0",
        "docs": "/docs",
        "admin": "/admin",
        "health": "/health"
    }

# Log de inicialização com informações de segurança
logger.info("Iniciando SalasTech - Sistema de Gerenciamento de Salas IFAM")
logger.info("Segurança aplicada: CORS, JWT Authentication, Bearer Tokens")
logger.info("Documentação disponível em: /docs (Swagger) e /redoc (ReDoc)")

# Configurar painel administrativo PRIMEIRO
setup_admin_routes(app)

# Registro dos routers da API com prefixos e tags apropriadas
app.include_router(
    auth_router,
    tags=["Autenticação"]
)
app.include_router(
    user_controller.router,
    tags=["Usuários"]
)
app.include_router(
    room_controller.router,
    tags=["Salas"]
)
app.include_router(
    reservation_controller.router,
    tags=["Reservas"]
)
app.include_router(
    department_controller.router,
    tags=["Departamentos"]
)
app.include_router(
    report_controller.router,
    tags=["Relatórios"]
)

# Configuração do esquema OpenAPI personalizado
app.openapi = custom_openapi

# Log de conclusão da inicialização
logger.info("Aplicação SalasTech iniciada com sucesso!")
logger.info("Endpoints da API disponíveis diretamente na raiz")
logger.info("Health check disponível em: /health")
