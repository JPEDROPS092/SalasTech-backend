# -*- coding: utf-8 -*-
"""
Controlador de Autenticação - SalasTech

Este módulo implementa os endpoints relacionados à autenticação e autorização
de usuários no sistema SalasTech. Inclui funcionalidades para:

- Registro de novos usuários
- Autenticação via login/senha
- Logout e invalidação de sessões
- Validação de tokens JWT
- Atualização de senhas
- Proteções contra ataques (rate limiting, CSRF)

Características de Segurança:
- Rate limiting para prevenir ataques de força bruta
- Logs de auditoria para tentativas de login
- Validação de tokens JWT
- Proteção CSRF
- Hashing seguro de senhas

Autor: Equipe SalasTech
Data: Junho 2025
Versão: 1.0.0
"""

from fastapi import APIRouter, Body, Path, Request, Depends
from fastapi import status
from fastapi import Response
import logging

# Importações dos modelos de dados
from SalasTech.app.models import dto

# Importações dos serviços
from SalasTech.app.services import user_service

# Importações de segurança
from SalasTech.app.core.security import session
from SalasTech.app.core.security import rate_limiter
from SalasTech.app.core.security import csrf

# Importações de dependências e utilitários
from SalasTech.app.core import dependencies
from SalasTech.app.exceptions.scheme import AppException

# Configuração do logger para auditoria
logger = logging.getLogger(__name__)

# Configuração do router com prefixo e tags
router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)

@router.post("/register", 
             status_code=status.HTTP_201_CREATED, 
             response_model=dto.UsuarioDTO,
             summary="Registrar Novo Usuário",
             description="Cria um novo usuário no sistema com as informações fornecidas")
async def registrar_usuario(usuario: dto.UsuarioCriarDTO, request: Request):
    """
    Endpoint para registro de novos usuários no sistema.
    
    Este endpoint permite a criação de novos usuários com validação completa
    dos dados fornecidos. Aplica limitação de taxa para prevenir abuso.
    
    Args:
        usuario (dto.UsuarioCriarDTO): Dados do usuário a ser criado
        request (Request): Objeto de requisição para controle de taxa
        
    Returns:
        dto.UsuarioDTO: Dados do usuário criado (sem senha)
        
    Raises:
        HTTPException: Em caso de dados inválidos ou email já em uso
        
    Security:
        - Rate limiting aplicado para prevenir spam
        - Validação de formato de email
        - Validação de complexidade de senha
        - Log de auditoria da tentativa de registro
    """
    # Aplica limitação de taxa para prevenir abuso do endpoint de registro
    rate_limiter.check_login_rate_limit(request)
    
    # Log da tentativa de registro para auditoria (sem dados sensíveis)
    logger.info(f"Tentativa de registro para email: {usuario.email}")
    
    # Cria o usuário através do serviço
    try:
        novo_usuario = user_service.create_user(usuario)
        logger.info(f"Usuário registrado com sucesso: {usuario.email}")
        return novo_usuario
    except Exception as e:
        logger.error(f"Erro no registro do usuário {usuario.email}: {str(e)}")
        raise


@router.post("/login", 
             status_code=status.HTTP_200_OK, 
             response_model=str,
             summary="Autenticar Usuário",
             description="Autentica um usuário e retorna um token JWT")
async def fazer_login(credenciais: dto.UsuarioLoginDTO, response: Response, request: Request):
    """
    Endpoint para autenticação de usuários.
    
    Valida as credenciais do usuário e, se corretas, gera um token JWT
    que será usado para autorização em endpoints protegidos.
    
    Args:
        credenciais (dto.UsuarioLoginDTO): Email e senha do usuário
        response (Response): Objeto de resposta para definir cookies
        request (Request): Objeto de requisição para controle de taxa
        
    Returns:
        str: Token JWT para autenticação
        
    Raises:
        HTTPException: Em caso de credenciais inválidas
        
    Security:
        - Rate limiting para prevenir ataques de força bruta
        - Hash seguro de senhas
        - Tokens JWT com expiração
        - Cookies seguros (HttpOnly, Secure, SameSite)
    """
    # Aplica limitação de taxa para tentativas de login
    rate_limiter.check_login_rate_limit(request)
    
    # Log da tentativa de login (sem senha para segurança)
    logger.info(f"Tentativa de login para email: {credenciais.email}")
    
    try:
        token = await session.login(credenciais, response)
        logger.info(f"Login realizado com sucesso para: {credenciais.email}")
        return token
    except Exception as e:
        logger.warning(f"Falha no login para {credenciais.email}: {str(e)}")
        raise


@router.get("/logout", 
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Fazer Logout",
            description="Encerra a sessão do usuário e invalida o token")
async def fazer_logout(response: Response):
    """
    Endpoint para logout de usuários.
    
    Remove o token de autenticação e encerra a sessão ativa do usuário,
    garantindo que o token não possa mais ser utilizado.
    
    Args:
        response (Response): Objeto de resposta para limpar cookies
        
    Returns:
        None: Status 204 No Content
        
    Security:
        - Remove cookies de autenticação
        - Invalida tokens do lado do servidor
    """
    await session.logout(response)
    logger.info("Logout realizado com sucesso")


@router.get("/validate", 
            response_model=dto.Token,
            summary="Validar Token",
            description="Valida um token JWT e retorna informações do usuário")
async def validar_sessao(token: dependencies.token_dependency):
    """
    Endpoint para validação de tokens JWT.
    
    Verifica se um token JWT é válido e retorna as informações
    contidas no token, incluindo dados do usuário.
    
    Args:
        token: Token JWT obtido via dependência
        
    Returns:
        dto.Token: Informações do token validado
        
    Security:
        - Validação de assinatura JWT
        - Verificação de expiração
        - Autorização baseada em papéis
    """
    return token


@router.put("/password/update", 
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Atualizar Senha",
            description="Permite ao usuário autenticado atualizar sua senha")
async def atualizar_senha(dados_senha: dto.UsuarioAtualizarSenhaDTO, usuario: dependencies.user_dependency):
    """
    Endpoint para atualização de senha do usuário autenticado.
    
    Permite que um usuário autenticado altere sua senha atual,
    fornecendo a senha antiga para validação de segurança.
    
    Args:
        dados_senha (dto.UsuarioAtualizarSenhaDTO): Senha antiga e nova senha
        usuario: Usuário autenticado obtido via dependência
        
    Returns:
        None: Status 204 No Content
        
    Raises:
        HTTPException: Em caso de senha antiga incorreta
        
    Security:
        - Requer autenticação válida
        - Valida senha antiga antes da alteração
        - Hash seguro da nova senha
        - Log de auditoria da alteração
    """
    try:
        user_service.update_password(usuario, dados_senha)
        logger.info(f"Senha atualizada com sucesso para usuário ID: {usuario.id}")
    except Exception as e:
        logger.error(f"Erro na atualização de senha para usuário ID: {usuario.id}: {str(e)}")
        raise

@router.post("/password/reset", 
             status_code=status.HTTP_200_OK, 
             response_model=dict,
             summary="Solicitar Redefinição de Senha",
             description="Envia um token de redefinição de senha para o email informado")
async def solicitar_redefinicao_senha(request: Request, email: str = Body(..., embed=True)):
    """
    Endpoint para solicitação de redefinição de senha.
    
    Gera um token de redefinição de senha e o envia para o email
    informado, caso o email esteja registrado no sistema.
    
    Em produção, enviaria um email com link de redefinição.
    Para desenvolvimento, retorna o token que seria enviado.
    
    Args:
        request (Request): Objeto de requisição para controle de taxa
        email (str): Email do usuário que esqueceu a senha
        
    Returns:
        dict: Mensagem de confirmação (não revela se o email existe)
        
    Security:
        - Rate limiting para prevenir abuso
        - Não revela se o email existe no sistema
        - Token com expiração curta
        - Log de auditoria das tentativas
    """
    # Aplica limitação de taxa para tentativas de redefinição de senha
    rate_limiter.check_password_reset_rate_limit(request)
    
    # Log da tentativa de redefinição (sem revelar se o email existe)
    logger.info(f"Tentativa de redefinição de senha para email: {email}")
    
    token = user_service.reset_password(email)
    # Em produção, não retornar o token, apenas uma mensagem de sucesso
    return {
        "message": "Se o email existir no sistema, um link de redefinição será enviado.",
        "token": token  # Remover em produção
    }


@router.post("/password/reset/{token}", 
             status_code=status.HTTP_200_OK,
             summary="Confirmar Redefinição de Senha",
             description="Confirma a redefinição de senha usando o token recebido")
async def confirmar_redefinicao_senha(
    request: Request,
    token: str = Path(..., description="Token de redefinição de senha recebido"),
    nova_senha: str = Body(..., embed=True, min_length=8)
):
    """
    Endpoint para confirmação de redefinição de senha com token.
    
    Valida o token de redefinição e, se válido, define a nova senha
    para o usuário associado ao token.
    
    Args:
        request (Request): Objeto de requisição para controle de taxa
        token (str): Token de redefinição recebido por email
        nova_senha (str): Nova senha do usuário (mínimo 8 caracteres)
        
    Returns:
        dict: Mensagem de confirmação do sucesso
        
    Raises:
        AppException: Em caso de token inválido ou senha fraca
        
    Security:
        - Rate limiting para confirmação
        - Validação de força da senha
        - Verificação de senhas comuns
        - Expiração de token
        - Log de auditoria
    """
    # Aplica limitação de taxa para confirmação de redefinição
    rate_limiter.check_password_reset_rate_limit(request)
    
    # Validação de força da senha
    if len(nova_senha) < 8:
        raise AppException("A senha deve ter pelo menos 8 caracteres", 400)
    
    # Verificação de senhas comuns/fracas
    senhas_comuns = ["password", "123456", "qwerty", "admin", "12345678", "senha123"]
    if any(comum in nova_senha.lower() for comum in senhas_comuns):
        raise AppException("Senha muito comum ou facilmente descoberta. Use uma senha mais forte.", 400)
    
    # Log da tentativa de confirmação (sem mostrar token ou senha completos)
    logger.info(f"Tentativa de confirmação de redefinição com token: {token[:10]}...")
    
    sucesso = user_service.confirm_reset_password(token, nova_senha)
    if sucesso:
        logger.info("Redefinição de senha realizada com sucesso")
        return {"message": "Senha redefinida com sucesso"}
    else:
        logger.warning("Falha na redefinição - token inválido ou expirado")
        raise AppException("Falha na redefinição - token inválido ou expirado", 400)