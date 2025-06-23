"""
 Data Transfer Objects (estruturas para transferência de dados)
"""
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Any
import re

from pydantic import BaseModel, Field, validator, EmailStr, field_validator, model_validator
from pydantic_core import PydanticCustomError

from app.models.enums import UserRole, RoomStatus, ReservationStatus

# USUÁRIO
class UsuarioCriarDTO(BaseModel):
    """
    DTO (Data Transfer Object) para a criação de um usuário.

    Atributos:
        nome (str): Nome do usuário (mínimo 2, máximo 100 caracteres).
        sobrenome (str): Sobrenome do usuário (mínimo 2, máximo 100 caracteres).
        email (EmailStr): Endereço de email do usuário (formato validado).
        senha (str): Senha do usuário (mínimo 8 caracteres, requisitos de complexidade).
        departamento_id (Optional[int]): ID do departamento do usuário (opcional).
        papel (UserRole): Papel do usuário (padrão: UserRole.USER).
    """
    nome: str = Field(..., min_length=2, max_length=100)
    sobrenome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(..., min_length=8,
                        description="A senha deve ter no mínimo 8 caracteres, uma letra maiúscula, uma letra minúscula, um número e um caractere especial")
    departamento_id: Optional[int] = None
    papel: UserRole = UserRole.USER

    @field_validator('nome', 'sobrenome')
    @classmethod
    def validar_nome_sobrenome(cls, v: str) -> str:
        """
        Valida o nome e o sobrenome do usuário.

        Args:
            v (str): O valor a ser validado.

        Returns:
            str: O valor validado, com espaços extras removidos e capitalização correta.

        Raises:
            PydanticCustomError: Se a string for vazia ou contiver apenas espaços em branco.
        """
        if not v.strip():
            raise PydanticCustomError(
                'string_vazia', # Nome do erro customizado
                'A string não pode ser vazia ou conter apenas espaços em branco'
            )
        # Remove espaços extras e garante a capitalização correta
        return ' '.join(word.capitalize() for word in v.strip().split())

    @field_validator('email')
    @classmethod
    def validar_email(cls, v: str) -> str:
        """
        Valida o email do usuário.

        Args:
            v (str): O valor a ser validado.

        Returns:
            str: O valor validado (em minúsculas).
        """
        # Converte o email para minúsculas
        return v.lower()

class UsuarioDTO(BaseModel):
    """
    DTO para representar um usuário.

    Atributos:
        id (int): ID do usuário.
        nome (str): Nome do usuário.
        sobrenome (str): Sobrenome do usuário.
        papel (UserRole): Papel do usuário.
        email (EmailStr): Endereço de email do usuário.
        departamento_id (Optional[int]): ID do departamento do usuário (opcional).
        atualizado_em (datetime): Data e hora da última atualização.
        criado_em (datetime): Data e hora da criação.
    """
    id: int
    nome: str
    sobrenome: str
    papel: UserRole
    email: EmailStr
    departamento_id: Optional[int] = None
    atualizado_em: datetime
    criado_em: datetime

    class Config:
        """Configurações do Pydantic para este modelo."""
        from_attributes = True # Permite criar o modelo a partir de atributos de um objeto (ex: ORM model)

class UsuarioAtualizarNomeDTO(BaseModel):
    """
    DTO para atualizar o nome e sobrenome de um usuário.

    Atributos:
        nome (str): Novo nome do usuário (mínimo 2, máximo 100 caracteres).
        sobrenome (str): Novo sobrenome do usuário (mínimo 2, máximo 100 caracteres).
    """
    nome: str = Field(..., min_length=2, max_length=100)
    sobrenome: str = Field(..., min_length=2, max_length=100)

    @field_validator('nome', 'sobrenome')
    @classmethod
    def validar_nome_sobrenome(cls, v: str) -> str:
        """
        Valida o nome e o sobrenome do usuário.

        Args:
            v (str): O valor a ser validado.

        Returns:
            str: O valor validado, com espaços extras removidos e capitalização correta.

        Raises:
            PydanticCustomError: Se a string for vazia ou contiver apenas espaços em branco.
        """
        if not v.strip():
            raise PydanticCustomError(
                'string_vazia',
                'A string não pode ser vazia ou conter apenas espaços em branco'
            )
        # Remove espaços extras e garante a capitalização correta
        return ' '.join(word.capitalize() for word in v.strip().split())

class UsuarioLoginDTO(BaseModel):
    """
    DTO para autenticação de usuário (login).

    Atributos:
        email (EmailStr): Endereço de email do usuário.
        senha (str): Senha do usuário (mínimo 8 caracteres).
    """
    email: EmailStr
    senha: str = Field(..., min_length=8)

    @field_validator('email')
    @classmethod
    def validar_email(cls, v: str) -> str:
        """
        Valida o email do usuário.

        Args:
            v (str): O valor a ser validado.

        Returns:
            str: O valor validado (em minúsculas).
        """
        # Converte o email para minúsculas
        return v.lower()

class UsuarioAtualizarSenhaDTO(BaseModel):
    """
    DTO para atualizar a senha de um usuário.

    Atributos:
        senha_antiga (str): Senha antiga do usuário (mínimo 8 caracteres).
        nova_senha (str): Nova senha do usuário (mínimo 8 caracteres, requisitos de complexidade).
    """
    senha_antiga: str = Field(..., min_length=8)
    nova_senha: str = Field(..., min_length=8,
                           description="A senha deve ter no mínimo 8 caracteres, uma letra maiúscula, uma letra minúscula, um número e um caractere especial")

    @field_validator('nova_senha')
    @classmethod
    def validar_nova_senha(cls, v: str) -> str:
        """
        Valida a nova senha do usuário.

        Args:
            v (str): O valor a ser validado.

        Returns:
            str: O valor validado.

        Raises:
            PydanticCustomError: Se a senha não atender aos requisitos de complexidade.
        """
        if len(v) < 8:
            raise PydanticCustomError('senha_muito_curta', 'A senha deve ter no mínimo 8 caracteres')

        has_lowercase = any(c.islower() for c in v)
        has_uppercase = any(c.isupper() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in '@$!%*?&#' for c in v)

        if not (has_lowercase and has_uppercase and has_digit and has_special):
            raise PydanticCustomError(
                'requisitos_senha',
                'A senha deve ter no mínimo uma letra maiúscula, uma letra minúscula, um número e um caractere especial'
            )
        return v

    @model_validator(mode='after')
    def verificar_senhas_diferentes(self) -> 'UsuarioAtualizarSenhaDTO':
        """
        Valida se a nova senha é diferente da senha antiga.

        Returns:
            UsuarioAtualizarSenhaDTO: O objeto DTO validado.

        Raises:
            ValueError: Se a nova senha for igual à senha antiga.
        """
        if self.senha_antiga == self.nova_senha:
            raise ValueError('A nova senha deve ser diferente da senha antiga')
        return self

# TOKEN
class TokenDTO(BaseModel):
    """
    DTO para representar um token de autenticação.

    Atributos:
        usuario_id (int): ID do usuário associado ao token.
        papel (str): Papel do usuário associado ao token.
    """
    usuario_id: int
    papel: str

# DEPARTAMENTO
class DepartamentoBaseDTO(BaseModel):
    """
    DTO base para representar um departamento.

    Atributos:
        nome (str): Nome do departamento (mínimo 2, máximo 100 caracteres).
        codigo (str): Código do departamento (mínimo 2, máximo 20 caracteres, formato alfanumérico com hífens).
        descricao (Optional[str]): Descrição do departamento (opcional, máximo 500 caracteres).
    """
    nome: str = Field(..., min_length=2, max_length=100)
    codigo: str = Field(..., min_length=2, max_length=20, pattern=r'^[A-Z0-9-]+$')
    descricao: Optional[str] = Field(None, max_length=500)

    @field_validator('nome')
    @classmethod
    def validar_nome(cls, v: str) -> str:
        """
        Valida o nome do departamento.

        Args:
            v (str): O valor a ser validado.

        Returns:
            str: O valor validado, com espaços extras removidos.

        Raises:
            ValueError: Se o nome do departamento for vazio.
        """
        if not v.strip():
            raise ValueError('O nome do departamento não pode ser vazio')
        return v.strip()

    @field_validator('codigo')
    @classmethod
    def validar_codigo(cls, v: str) -> str:
        """
        Valida o código do departamento.

        Args:
            v (str): O valor a ser validado.

        Returns:
            str: O valor validado (em maiúsculas).
        """
        # Converte para maiúsculas
        return v.upper()

class DepartamentoCriarDTO(DepartamentoBaseDTO):
    """
    DTO para a criação de um departamento.

    Atributos:
        gerente_id (Optional[int]): ID do gerente do departamento (opcional).
    """
    gerente_id: Optional[int] = None

class DepartamentoRespostaDTO(DepartamentoBaseDTO):
    """
    DTO para representar a resposta de um departamento.

    Atributos:
        id (int): ID do departamento.
        gerente_id (Optional[int]): ID do gerente do departamento (opcional).
        criado_em (datetime): Data e hora da criação.
        atualizado_em (datetime): Data e hora da última atualização.
    """
    id: int
    gerente_id: Optional[int] = None
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        """Configurações do Pydantic para este modelo."""
        from_attributes = True # Permite criar o modelo a partir de atributos de um objeto (ex: ORM model)

# RECURSO DA SALA
class RecursoSalaBaseDTO(BaseModel):
    """
    DTO base para representar um recurso de sala.

    Atributos:
        nome_recurso (str): Nome do recurso (mínimo 2, máximo 100 caracteres).
        quantidade (int): Quantidade do recurso (mínimo 1, máximo 1000).
        descricao (Optional[str]): Descrição do recurso (opcional, máximo 500 caracteres).
    """
    nome_recurso: str = Field(..., min_length=2, max_length=100)
    quantidade: int = Field(1, ge=1, le=1000)
    descricao: Optional[str] = Field(None, max_length=500)

    @field_validator('nome_recurso')
    @classmethod
    def validar_nome_recurso(cls, v: str) -> str:
        """
        Valida o nome do recurso.

        Args:
            v (str): O valor a ser validado.

        Returns:
            str: O valor validado, com a primeira letra de cada palavra em maiúscula.

        Raises:
            ValueError: Se o nome do recurso for vazio.
        """
        if not v.strip():
            raise ValueError('O nome do recurso não pode ser vazio')
        # Capitaliza a primeira letra de cada palavra
        return ' '.join(word.capitalize() for word in v.strip().split())

class RecursoSalaCriarDTO(RecursoSalaBaseDTO):
    """
    DTO para a criação de um recurso de sala.
    """
    pass

class RecursoSalaRespostaDTO(RecursoSalaBaseDTO):
    """
    DTO para representar a resposta de um recurso de sala.

    Atributos:
        id (int): ID do recurso.
        sala_id (int): ID da sala associada ao recurso.
        criado_em (datetime): Data e hora da criação.
        atualizado_em (datetime): Data e hora da última atualização.
    """
    id: int
    sala_id: int
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        """Configurações do Pydantic para este modelo."""
        from_attributes = True # Permite criar o modelo a partir de atributos de um objeto (ex: ORM model)

# SALA
class SalaBaseDTO(BaseModel):
    """
    DTO base para representar uma sala.

    Atributos:
        codigo (str): Código da sala (mínimo 2, máximo 20 caracteres, formato alfanumérico com hífens).
        nome (str): Nome da sala (mínimo 2, máximo 100 caracteres).
        capacidade (int): Capacidade da sala (maior que 0, menor ou igual a 1000).
        predio (str): Edifício da sala (mínimo 1, máximo 100 caracteres).
        andar (str): Andar da sala (mínimo 1, máximo 20 caracteres).
        departamento_id (int): ID do departamento da sala (maior que 0).
        status (RoomStatus): Status da sala (padrão: RoomStatus.ATIVA).
        responsavel (Optional[str]): Responsável pela sala (opcional, mínimo 2, máximo 100 caracteres).
        descricao (Optional[str]): Descrição da sala (opcional, máximo 500 caracteres).
    """
    codigo: str = Field(..., min_length=2, max_length=20, pattern=r'^[A-Z0-9-]+$')
    nome: str = Field(..., min_length=2, max_length=100)
    capacidade: int = Field(..., gt=0, le=1000)
    predio: str = Field(..., min_length=1, max_length=100)
    andar: str = Field(..., min_length=1, max_length=20)
    departamento_id: int = Field(..., gt=0)
    status: RoomStatus = RoomStatus.ATIVA
    responsavel: Optional[str] = Field(None, min_length=2, max_length=100)
    descricao: Optional[str] = Field(None, max_length=500)

    @field_validator('codigo')
    @classmethod
    def validar_codigo(cls, v: str) -> str:
        """
        Valida o código da sala.

        Args:
            v (str): O valor a ser validado.

        Returns:
            str: O valor validado (em maiúsculas).
        """
        # Converte para maiúsculas
        return v.upper()

    @field_validator('nome', 'predio', 'responsavel')
    @classmethod
    def validar_campos_texto(cls, v: Optional[str], info: Any) -> Optional[str]:
        """
        Valida campos de texto da sala (nome, edifício, responsável).

        Args:
            v (Optional[str]): O valor a ser validado.
            info (Any): Informações sobre o campo.

        Returns:
            Optional[str]: O valor validado, com a primeira letra de cada palavra em maiúscula.

        Raises:
            ValueError: Se o campo for obrigatório e estiver vazio.
        """
        if v is None and info.field_name == 'responsible': # O nome 'responsible' aqui se refere ao nome do campo original, se ele ainda não foi traduzido para 'responsavel'
            return None
        # Usamos info.field_name para referenciar o nome do campo original (antes da tradução de Pydantic) para a mensagem de erro
        field_display_name = {
            'nome': 'Nome',
            'predio': 'Prédio',
            'responsavel': 'Responsável'
        }.get(info.field_name, info.field_name.capitalize()) # Adicionado mapeamento para nomes traduzidos

        if not v or not v.strip():
            raise ValueError(f'{field_display_name} não pode ser vazio')
        # Capitaliza a primeira letra de cada palavra
        return ' '.join(word.capitalize() for word in v.strip().split())

class SalaCriarDTO(SalaBaseDTO):
    """
    DTO para a criação de uma sala.

    Atributos:
        recursos (Optional[List[RecursoSalaCriarDTO]]): Lista de recursos da sala (opcional).
    """
    recursos: Optional[List[RecursoSalaCriarDTO]] = None

class SalaAtualizarDTO(BaseModel):
    """
    DTO para atualizar os dados de uma sala.

    Atributos:
        nome (Optional[str]): Novo nome da sala (mínimo 2, máximo 100 caracteres, opcional).
        capacidade (Optional[int]): Nova capacidade da sala (maior que 0, menor ou igual a 1000, opcional).
        predio (Optional[str]): Novo edifício da sala (mínimo 1, máximo 100 caracteres, opcional).
        andar (Optional[str]): Novo andar da sala (mínimo 1, máximo 20 caracteres, opcional).
        departamento_id (Optional[int]): Novo ID do departamento da sala (maior que 0, opcional).
        status (Optional[RoomStatus]): Novo status da sala (opcional).
        responsavel (Optional[str]): Novo responsável pela sala (mínimo 2, máximo 100 caracteres, opcional).
        descricao (Optional[str]): Nova descrição da sala (opcional, máximo 500 caracteres).
        recursos (Optional[List[RecursoSalaCriarDTO]]): Nova lista de recursos da sala (opcional).
    """
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    capacidade: Optional[int] = Field(None, gt=0, le=1000)
    predio: Optional[str] = Field(None, min_length=1, max_length=100)
    andar: Optional[str] = Field(None, min_length=1, max_length=20)
    departamento_id: Optional[int] = Field(None, gt=0)
    status: Optional[RoomStatus] = None
    responsavel: Optional[str] = Field(None, min_length=2, max_length=100)
    descricao: Optional[str] = Field(None, max_length=500)
    recursos: Optional[List[RecursoSalaCriarDTO]] = None

    @field_validator('nome', 'predio', 'responsavel')
    @classmethod
    def validar_campos_texto(cls, v: Optional[str], info: Any) -> Optional[str]:
        """
        Valida campos de texto da sala (nome, edifício, responsável) para atualização.

        Args:
            v (Optional[str]): O valor a ser validado.
            info (Any): Informações sobre o campo.

        Returns:
            Optional[str]: O valor validado, com a primeira letra de cada palavra em maiúscula.

        Raises:
            ValueError: Se o campo for fornecido e estiver vazio.
        """
        if v is None:
            return None
        # Usamos info.field_name para referenciar o nome do campo original (antes da tradução de Pydantic) para a mensagem de erro
        field_display_name = {
            'nome': 'Nome',
            'predio': 'Prédio',
            'responsavel': 'Responsável'
        }.get(info.field_name, info.field_name.capitalize())

        if not v.strip():
            raise ValueError(f'{field_display_name} não pode ser vazio quando fornecido')
        # Capitaliza a primeira letra de cada palavra
        return ' '.join(word.capitalize() for word in v.strip().split())

class SalaRespostaDTO(SalaBaseDTO):
    """
    DTO para representar a resposta de uma sala.

    Atributos:
        id (int): ID da sala.
        recursos (List[RecursoSalaRespostaDTO]): Lista de recursos da sala.
        criado_em (datetime): Data e hora da criação.
        atualizado_em (datetime): Data e hora da última atualização.
    """
    id: int
    recursos: List[RecursoSalaRespostaDTO] = []
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        """Configurações do Pydantic para este modelo."""
        from_attributes = True # Permite criar o modelo a partir de atributos de um objeto (ex: ORM model)

# RESERVA
class ReservaBaseDTO(BaseModel):
    """
    DTO base para representar uma reserva.

    Atributos:
        sala_id (int): ID da sala reservada (maior que 0).
        titulo (str): Título da reserva (mínimo 3, máximo 100 caracteres).
        descricao (Optional[str]): Descrição da reserva (opcional, máximo 500 caracteres).
        inicio_data_hora (datetime): Data e hora de início da reserva.
        fim_data_hora (datetime): Data e hora de término da reserva.
    """
    sala_id: int = Field(..., gt=0)
    titulo: str = Field(..., min_length=3, max_length=100)
    descricao: Optional[str] = Field(None, max_length=500)
    inicio_data_hora: datetime
    fim_data_hora: datetime

    @field_validator('titulo')
    @classmethod
    def validar_titulo(cls, v: str) -> str:
        """
        Valida o título da reserva.

        Args:
            v (str): O valor a ser validado.

        Returns:
            str: O valor validado, com a primeira letra em maiúscula.

        Raises:
            ValueError: Se o título for vazio.
        """
        if not v.strip():
            raise ValueError('O título não pode ser vazio')
        # Capitaliza a primeira letra
        return v.strip().capitalize()

    @field_validator('descricao')
    @classmethod
    def validar_descricao(cls, v: Optional[str]) -> Optional[str]:
        """
        Valida a descrição da reserva.

        Args:
            v (Optional[str]): O valor a ser validado.

        Returns:
            Optional[str]: O valor validado, com espaços extras removidos.
        """
        if v is None:
            return None
        return v.strip()

    @model_validator(mode='after')
    def validar_restricoes_data_hora(self) -> 'ReservaBaseDTO':
        """
        Valida as restrições de data e hora da reserva.

        Returns:
            ReservaBaseDTO: O objeto DTO validado.

        Raises:
            ValueError: Se as restrições de data e hora não forem atendidas (fim antes do início, duração mínima/máxima, tempo no passado, aviso prévio mínimo/máximo).
        """
        # Verifica se o horário de término é posterior ao horário de início
        if self.fim_data_hora <= self.inicio_data_hora:
            raise ValueError('A hora de término deve ser posterior à hora de início')

        # Verifica a duração mínima (30 minutos)
        min_duracao = timedelta(minutes=30)
        if self.fim_data_hora - self.inicio_data_hora < min_duracao:
            raise ValueError('A reserva deve ter duração mínima de 30 minutos')

        # Verifica a duração máxima (8 horas)
        max_duracao = timedelta(hours=8)
        if self.fim_data_hora - self.inicio_data_hora > max_duracao:
            raise ValueError('A reserva não pode exceder 8 horas')

        # Verifica se o horário de início é no futuro
        now = datetime.now(timezone.utc)
        if self.inicio_data_hora < now:
            raise ValueError('A hora de início deve ser no futuro')

        # Verifica o aviso prévio mínimo (2 horas)
        min_antecedencia = timedelta(hours=2)
        if self.inicio_data_hora - now < min_antecedencia:
            raise ValueError('As reservas devem ser feitas com no mínimo 2 horas de antecedência')

        # Verifica o aviso prévio máximo (30 dias)
        max_antecedencia = timedelta(days=30)
        if self.inicio_data_hora - now > max_antecedencia:
            raise ValueError('As reservas não podem ser feitas com mais de 30 dias de antecedência')

        return self

class ReservaCriarDTO(ReservaBaseDTO):
    """
    DTO para a criação de uma reserva.
    """
    pass

class ReservaAtualizarDTO(BaseModel):
    """
    DTO para atualizar os dados de uma reserva.

    Atributos:
        titulo (Optional[str]): Novo título da reserva (mínimo 3, máximo 100 caracteres, opcional).
        descricao (Optional[str]): Nova descrição da reserva (opcional, máximo 500 caracteres).
        inicio_data_hora (Optional[datetime]): Nova data e hora de início da reserva (opcional).
        fim_data_hora (Optional[datetime]): Nova data e hora de término da reserva (opcional).
        status (Optional[ReservationStatus]): Novo status da reserva (opcional).
        motivo_cancelamento (Optional[str]): Motivo do cancelamento (opcional, máximo 500 caracteres).
    """
    titulo: Optional[str] = Field(None, min_length=3, max_length=100)
    descricao: Optional[str] = Field(None, max_length=500)
    inicio_data_hora: Optional[datetime] = None
    fim_data_hora: Optional[datetime] = None
    status: Optional[ReservationStatus] = None
    motivo_cancelamento: Optional[str] = Field(None, max_length=500)

    @field_validator('titulo')
    @classmethod
    def validar_titulo(cls, v: Optional[str]) -> Optional[str]:
        """
        Valida o título da reserva para atualização.

        Args:
            v (Optional[str]): O valor a ser validado.

        Returns:
            Optional[str]: O valor validado, com a primeira letra em maiúscula.

        Raises:
            ValueError: Se o título for fornecido e estiver vazio.
        """
        if v is None:
            return None
        if not v.strip():
            raise ValueError('O título não pode ser vazio quando fornecido')
        # Capitaliza a primeira letra
        return v.strip().capitalize()

    @field_validator('descricao', 'motivo_cancelamento')
    @classmethod
    def validar_campos_texto(cls, v: Optional[str]) -> Optional[str]:
        """
        Valida campos de texto da reserva (descrição, motivo do cancelamento) para atualização.

        Args:
            v (Optional[str]): O valor a ser validado.

        Returns:
            Optional[str]: O valor validado, com espaços extras removidos.
        """
        if v is None:
            return None
        return v.strip()

    @model_validator(mode='after')
    def validar_restricoes_data_hora(self) -> 'ReservaAtualizarDTO':
        """
        Valida as restrições de data e hora da reserva para atualização.

        Returns:
            ReservaAtualizarDTO: O objeto DTO validado.

        Raises:
            ValueError: Se as restrições de data e hora não forem atendidas (fim antes do início, duração mínima/máxima, tempo no passado, aviso prévio mínimo/máximo).
        """
        # Ignora a validação se nem a data de início nem a data de término forem fornecidas
        if self.inicio_data_hora is None and self.fim_data_hora is None:
            return self

        # Se apenas um for fornecido, não podemos validar o relacionamento
        if self.inicio_data_hora is None or self.fim_data_hora is None:
            raise ValueError('Ambas as datas e horas de início e fim devem ser fornecidas juntas')

        # Verifica se o horário de término é posterior ao horário de início
        if self.fim_data_hora <= self.inicio_data_hora:
            raise ValueError('A hora de término deve ser posterior à hora de início')

        # Verifica a duração mínima (30 minutos)
        min_duracao = timedelta(minutes=30)
        if self.fim_data_hora - self.inicio_data_hora < min_duracao:
            raise ValueError('A reserva deve ter duração mínima de 30 minutos')

        # Verifica a duração máxima (8 horas)
        max_duracao = timedelta(hours=8)
        if self.fim_data_hora - self.inicio_data_hora > max_duracao:
            raise ValueError('A reserva não pode exceder 8 horas')

        # Verifica se o horário de início é no futuro (apenas se o status não for para um estado final como CANCELADA ou CONCLUIDA)
        # O ideal seria permitir datas passadas para atualizações de status para CONCLUIDA, por exemplo.
        # Para simplificar e manter a lógica original de "criação/edição para o futuro":
        now = datetime.now(timezone.utc)
        if self.inicio_data_hora < now and self.status not in [ReservationStatus.CONCLUIDA, ReservationStatus.CANCELADA]:
            raise ValueError('A hora de início deve ser no futuro para novas reservas ou atualizações pendentes/aprovadas')

        # As validações de aviso prévio mínimo e máximo fazem mais sentido na criação,
        # mas podem ser mantidas aqui se a intenção for garantir que edições ainda sigam essas regras.
        # Caso contrário, pode-se remover para updates que alteram apenas o status, por exemplo.
        # Mantendo para consistência com o ReservationBase:
        min_antecedencia = timedelta(hours=2)
        if self.inicio_data_hora - now < min_antecedencia:
            raise ValueError('As reservas devem ser feitas com no mínimo 2 horas de antecedência')

        max_antecedencia = timedelta(days=30)
        if self.inicio_data_hora - now > max_antecedencia:
            raise ValueError('As reservas não podem ser feitas com mais de 30 dias de antecedência')

        return self


class ReservaRespostaDTO(ReservaBaseDTO):
    """
    DTO para representar a resposta de uma reserva.

    Atributos:
        id (int): ID da reserva.
        usuario_id (int): ID do usuário que fez a reserva.
        status (ReservationStatus): Status da reserva.
        aprovado_por (Optional[int]): ID do usuário que aprovou a reserva (opcional).
        aprovado_em (Optional[datetime]): Data e hora da aprovação (opcional).
        motivo_cancelamento (Optional[str]): Motivo do cancelamento (opcional).
        criado_em (datetime): Data e hora da criação.
        atualizado_em (datetime): Data e hora da última atualização.
    """
    id: int
    usuario_id: int
    status: ReservationStatus
    aprovado_por: Optional[int] = None
    aprovado_em: Optional[datetime] = None
    motivo_cancelamento: Optional[str] = None
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        """Configurações do Pydantic para este modelo."""
        from_attributes = True # Permite criar o modelo a partir de atributos de um objeto (ex: ORM model)

# RELATÓRIO
class RelatorioOcupacaoSalaDTO(BaseModel):
    """
    DTO para representar um relatório de ocupação de sala.

    Atributos:
        sala_id (int): ID da sala.
        codigo_sala (str): Código da sala.
        nome_sala (str): Nome da sala.
        total_reservas (int): Total de reservas da sala.
        total_horas (float): Total de horas reservadas na sala.
        taxa_ocupacao (float): Taxa de ocupação da sala (percentual).
    """
    sala_id: int
    codigo_sala: str
    nome_sala: str
    total_reservas: int
    total_horas: float
    taxa_ocupacao: float  # Percentual de ocupação

class RelatorioUsoDepartamentoDTO(BaseModel):
    """
    DTO para representar um relatório de uso de departamento.

    Atributos:
        departamento_id (int): ID do departamento.
        nome_departamento (str): Nome do departamento.
        total_salas (int): Total de salas no departamento.
        total_reservas (int): Total de reservas feitas pelo departamento.
        uso_salas (List[RelatorioOcupacaoSalaDTO]): Lista de relatórios de ocupação de salas do departamento.
    """
    departamento_id: int
    nome_departamento: str
    total_salas: int
    total_reservas: int
    uso_salas: List[RelatorioOcupacaoSalaDTO]

class RelatorioAtividadeUsuarioDTO(BaseModel):
    """
    DTO para representar um relatório de atividade de usuário.

    Atributos:
        usuario_id (int): ID do usuário.
        nome_usuario (str): Nome do usuário.
        total_reservas (int): Total de reservas feitas pelo usuário.
        total_horas (float): Total de horas reservadas pelo usuário.
        reservas_por_status (dict): Contagem de reservas por status.
    """
    usuario_id: int
    nome_usuario: str
    total_reservas: int
    total_horas: float
    reservas_por_status: dict  # Contagem por status