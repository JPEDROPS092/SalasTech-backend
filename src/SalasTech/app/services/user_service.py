# -*- coding: utf-8 -*-
"""
Serviço de Usuários - SalasTech

Este módulo implementa a lógica de negócios para gerenciamento de usuários
no sistema SalasTech. Fornece operações CRUD completas e funcionalidades
relacionadas a autenticação, segurança e gestão de perfis.

Funcionalidades principais:
- Criação e validação de usuários
- Autenticação e autorização
- Gerenciamento de senhas e tokens de redefinição
- Operações de busca e listagem
- Mapeamento entre modelos de dados
- Validações de segurança

Características de Segurança:
- Hash seguro de senhas com bcrypt
- Tokens JWT para autenticação
- Validação de força de senhas
- Prevenção contra ataques de enumeração
- Logs de auditoria para operações críticas

Autor: Equipe SalasTech
Data: Junho 2025
Versão: 1.0.0
"""

import secrets
import string
import logging
from datetime import datetime, timedelta, timezone
from random import randint
from typing import List, Dict, Optional

# Importações dos modelos
from SalasTech.app.models import db
from SalasTech.app.models import dto
from SalasTech.app.models import enums

# Importações dos repositórios
from SalasTech.app.repos import user_repo

# Importações de segurança
from SalasTech.app.core.security import bcrypt_hashing
from SalasTech.app.core.security import jwt

# Importações de utilitários
from SalasTech.app.utils import formatting
from SalasTech.app.mappers import user_mapper
from SalasTech.app.exceptions.scheme import AppException

# Configuração do logger
logger = logging.getLogger(__name__)

# Constantes para compatibilidade com sistema legado
SENHA_MIN_LEGADO = 100000
SENHA_MAX_LEGADO = 999999

# Armazenamento temporário de tokens de redefinição de senha
# Formato: {"token": {"user_id": id, "expires": datetime}}
# NOTA: Em produção, deve ser armazenado em banco de dados ou cache Redis
TOKENS_REDEFINICAO_SENHA: Dict[str, Dict] = {}


def obter_todos(limite: int = 1000, offset: int = 0) -> List[dto.UsuarioDTO]:
    """
    Obtém todos os usuários do sistema com paginação.
    
    Retorna uma lista paginada de usuários, convertida para DTOs
    para exposição segura dos dados.
    
    Args:
        limite (int): Número máximo de usuários a retornar (padrão: 1000)
        offset (int): Número de registros a pular para paginação (padrão: 0)
        
    Returns:
        List[dto.UsuarioDTO]: Lista de usuários encontrados
        
    Notes:
        - Ordenação por ID crescente
        - Dados sensíveis como senhas não são incluídos
        - Performance otimizada para grandes volumes
    """
    logger.info(f"Buscando usuários - limite: {limite}, offset: {offset}")
    usuarios_db = user_repo.get(limite, offset)
    usuarios_dto = [user_mapper.db_to_get_dto(usuario) for usuario in usuarios_db]
    logger.info(f"Encontrados {len(usuarios_dto)} usuários")
    return usuarios_dto


def obter_por_id(id: int) -> db.UsuarioDb:
    """
    Busca um usuário específico pelo ID.
    
    Args:
        id (int): ID único do usuário
        
    Returns:
        db.UsuarioDb: Objeto do usuário encontrado
        
    Raises:
        AppException: 404 se o usuário não for encontrado
        
    Security:
        - Validação de existência do usuário
        - Log de auditoria para buscas
    """
    logger.info(f"Buscando usuário por ID: {id}")
    usuario = user_repo.get_by_id(id)
    if usuario is None:
        logger.warning(f"Usuário com ID {id} não encontrado")
        raise AppException(message="Usuário não encontrado", status_code=404)

    logger.info(f"Usuário encontrado: {usuario.email}")
    return usuario


def obter_por_id_dto(id: int) -> dto.UsuarioDTO:
    """
    Busca um usuário por ID e retorna como DTO.
    
    Combina busca por ID com conversão para DTO para
    exposição segura dos dados.
    
    Args:
        id (int): ID único do usuário
        
    Returns:
        dto.UsuarioDTO: Dados do usuário como DTO
        
    Raises:
        AppException: 404 se o usuário não for encontrado
    """
    usuario = obter_por_id(id)
    return user_mapper.db_to_get_dto(usuario)


def obter_por_email(email: str) -> db.UsuarioDb:
    """
    Busca um usuário específico pelo email.
    
    Args:
        email (str): Endereço de email do usuário
        
    Returns:
        db.UsuarioDb: Objeto do usuário encontrado
        
    Raises:
        AppException: 404 se o usuário não for encontrado
        
    Security:
        - Normalização do formato do email
        - Validação de existência
        - Log de auditoria
    """
    logger.info(f"Buscando usuário por email: {email}")
    email_formatado = formatting.format_string(email)
    usuario = user_repo.get_by_email(email_formatado)
    if usuario is None:
        logger.warning(f"Usuário com email {email} não encontrado")
        raise AppException(message="Usuário não encontrado", status_code=404)

    return usuario


def obter_por_email_dto(email: str) -> dto.UsuarioDTO:
    """
    Busca um usuário por email e retorna como DTO.
    
    Args:
        email (str): Endereço de email do usuário
        
    Returns:
        dto.UsuarioDTO: Dados do usuário como DTO
    """
    user = obter_por_email(email)
    return user_mapper.db_to_get_dto(user)


def criar_usuario(obj: dto.UsuarioCriarDTO) -> dto.UsuarioDTO:
    """
    Cria um novo usuário comum no sistema.
    
    Args:
        obj (dto.UsuarioCriarDTO): Dados do usuário a ser criado
        
    Returns:
        dto.UsuarioDTO: Usuário criado (sem dados sensíveis)
    """
    user = _criar(obj, enums.UserRole.USER)
    return user_mapper.db_to_get_dto(user)


def criar_admin(obj: dto.UsuarioCriarDTO) -> dto.UsuarioDTO:
    """
    Cria um novo usuário administrador no sistema.
    
    Args:
        obj (dto.UsuarioCriarDTO): Dados do usuário a ser criado
        
    Returns:
        dto.UsuarioDTO: Usuário criado (sem dados sensíveis)
    """
    user = _criar(obj, enums.UserRole.ADMIN)
    return user_mapper.db_to_get_dto(user)


def atualizar_nome(user: db.UsuarioDb, obj: dto.UsuarioAtualizarNomeDTO) -> None:
    """
    Atualiza o nome e sobrenome de um usuário.
    
    Args:
        user (db.UsuarioDb): Usuário a ser atualizado
        obj (dto.UsuarioAtualizarNomeDTO): Novos dados de nome
    """
    user.nome = formatting.format_string(obj.nome)
    user.sobrenome = formatting.format_string(obj.sobrenome)
    user_repo.update(user)


def atualizar_senha(user: dto.UsuarioDTO, obj: dto.UsuarioAtualizarSenhaDTO) -> None:
    """
    Atualiza a senha de um usuário.
    
    Args:
        user (dto.UsuarioDTO): Usuário que terá a senha alterada
        obj (dto.UsuarioAtualizarSenhaDTO): Dados da atualização de senha
    """
    user_db = obter_por_id(user.id)
    if bcrypt_hashing.validate(obj.senha_antiga, user_db.senha) is False:
        raise AppException(message="Senha incorreta", status_code=422)

    _atualizar_senha(user_db, obj.nova_senha)


def redefinir_senha(email: str) -> str:
    """
    Gera um token de redefinição de senha e envia instruções de redefinição.
    
    Em um ambiente de produção, isso enviaria um email com um link de redefinição.
    Por enquanto, retorna o token que seria enviado no email.
    
    Args:
        email (str): Endereço de email do usuário
        
    Returns:
        str: Token de redefinição de senha (para fins de teste)
        
    Raises:
        AppException: Se o usuário não for encontrado
    """
    try:
        user = obter_por_email(email)
        
        # Gerar um token aleatório seguro
        token = secrets.token_urlsafe(32)
        
        # Definir expiração do token (1 hora a partir de agora)
        expiration = datetime.now(timezone.utc) + timedelta(hours=1)
        
        # Armazenar token com ID do usuário e expiração
        TOKENS_REDEFINICAO_SENHA[token] = {
            "user_id": user.id,
            "expires": expiration
        }
        
        # Em uma aplicação real, enviaria um email com um link de redefinição
        reset_link = f"/auth/senha/redefinir/{token}"
        
        logger.info(f"Redefinição de senha solicitada para {email}. Token: {token}")
        
        # Retornar o token para fins de teste
        # Em produção, isso retornaria None e enviaria um email
        return token
    except Exception as e:
        logger.error(f"Erro na redefinição de senha para {email}: {str(e)}")
        # Não expor se o email existe ou não
        raise AppException("Se o email existir, um link de redefinição de senha será enviado.", 200)


def excluir(id: int) -> None:
    """
    Exclui um usuário do sistema.
    
    Args:
        id (int): ID do usuário a ser excluído
    """
    user_repo.delete(id)


def _criar(obj: dto.UsuarioCriarDTO, role: enums.UserRole) -> db.UsuarioDb:
    """
    Função interna para criar um usuário com um papel específico.
    
    Args:
        obj (dto.UsuarioCriarDTO): Dados do usuário
        role (enums.UserRole): Papel a ser atribuído ao usuário
        
    Returns:
        db.UsuarioDb: Usuário criado
    """
    nome_formatado = formatting.format_string(obj.nome)
    sobrenome_formatado = formatting.format_string(obj.sobrenome)
    email_formatado = formatting.format_string(obj.email)

    if nome_formatado == "":
        raise AppException(message="Nome não é válido", status_code=422)

    if sobrenome_formatado == "":
        raise AppException(message="Sobrenome não é válido", status_code=422)

    if email_formatado == "":
        raise AppException(message="Email não é válido", status_code=422)

    if user_repo.get_by_email(email_formatado) is not None:
        raise AppException(message="Email já existe", status_code=422)

    usuario_para_db = db.UsuarioDb()
    usuario_para_db.nome = nome_formatado
    usuario_para_db.sobrenome = sobrenome_formatado
    usuario_para_db.papel = role
    usuario_para_db.email = email_formatado
    usuario_para_db.senha = bcrypt_hashing.hash(obj.senha)

    return user_repo.add(usuario_para_db)


def _atualizar_senha(user: db.UsuarioDb, nova_senha: str) -> None:
    """
    Atualiza a senha de um usuário com hash adequado.
    
    Args:
        user (db.UsuarioDb): Objeto do usuário no banco de dados
        nova_senha (str): Nova senha (texto simples)
    """
    # Validar força da senha
    if len(nova_senha) < 8:
        raise AppException("A senha deve ter pelo menos 8 caracteres", 400)
        
    # Hash da nova senha
    novo_hash_senha = bcrypt_hashing.hash(nova_senha)
    user.senha = novo_hash_senha
    user_repo.update(user)


def confirmar_redefinicao_senha(token: str, nova_senha: str) -> bool:
    """
    Confirma a redefinição de senha com token e define nova senha.
    
    Args:
        token (str): Token de redefinição de senha
        nova_senha (str): Nova senha a ser definida
        
    Returns:
        bool: True se a senha foi redefinida com sucesso
        
    Raises:
        AppException: Se o token for inválido ou expirado
    """
    # Verificar se o token existe
    if token not in TOKENS_REDEFINICAO_SENHA:
        logger.warning(f"Token de redefinição de senha inválido tentado: {token}")
        raise AppException("Token de redefinição inválido ou expirado", 400)
    
    # Obter dados do token
    token_data = TOKENS_REDEFINICAO_SENHA[token]
    
    # Verificar se o token expirou
    if token_data["expires"] < datetime.now(timezone.utc):
        # Remover token expirado
        del TOKENS_REDEFINICAO_SENHA[token]
        logger.warning(f"Token de redefinição de senha expirado tentado: {token}")
        raise AppException("Token de redefinição inválido ou expirado", 400)
    
    try:
        # Obter usuário e atualizar senha
        user = obter_por_id(token_data["user_id"])
        _atualizar_senha(user, nova_senha)
        
        # Remover token usado
        del TOKENS_REDEFINICAO_SENHA[token]
        
        logger.info(f"Redefinição de senha bem-sucedida para usuário ID: {user.id}")
        return True
    except Exception as e:
        logger.error(f"Erro durante confirmação de redefinição de senha: {str(e)}")
        raise AppException("Redefinição de senha falhou", 500)


def _redefinir_senha_legado(user: db.UsuarioDb) -> str:
    """
    Função de redefinição de senha legada - gera uma senha aleatória.
    
    Isso é mantido para compatibilidade com versões anteriores, mas deve ser depreciado.
    
    Args:
        user (db.UsuarioDb): Objeto do usuário no banco de dados
        
    Returns:
        str: Nova senha aleatória
    """
    nova_senha = str(randint(SENHA_MIN_LEGADO, SENHA_MAX_LEGADO))
    _atualizar_senha(user, nova_senha)

    return nova_senha
