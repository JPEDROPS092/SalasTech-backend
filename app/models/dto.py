from datetime import datetime, timedelta, timezone
from typing import List, Optional, Any
import re

from pydantic import BaseModel, Field, validator, EmailStr, field_validator, model_validator
from pydantic_core import PydanticCustomError

from app.models.enums import UserRole, RoomStatus, ReservationStatus

# USER (Usuário)
class UserCreateDTO(BaseModel):
    """
    DTO (Data Transfer Object) para a criação de um usuário.

    Atributos:
        name (str): Nome do usuário (mínimo 2, máximo 100 caracteres).
        surname (str): Sobrenome do usuário (mínimo 2, máximo 100 caracteres).
        email (EmailStr): Endereço de email do usuário (formato validado).
        password (str): Senha do usuário (mínimo 8 caracteres, requisitos de complexidade).
        department_id (Optional[int]): ID do departamento do usuário (opcional).
        role (UserRole): Papel do usuário (padrão: UserRole.USER).
    """
    name: str = Field(..., min_length=2, max_length=100)
    surname: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, 
                        description="Password must have at least 8 characters, one uppercase letter, one lowercase letter, one number, and one special character")
    department_id: Optional[int] = None
    role: UserRole = UserRole.USER
    
    @field_validator('name', 'surname')
    @classmethod
    def validate_name(cls, v: str) -> str:
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
                'empty_string',
                'String cannot be empty or just whitespace'
            )
        # Remove espaços extras e garante a capitalização correta
        return ' '.join(word.capitalize() for word in v.strip().split())
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """
        Valida o email do usuário.

        Args:
            v (str): O valor a ser validado.

        Returns:
            str: O valor validado (em minúsculas).
        """
        # Converte o email para minúsculas
        return v.lower()

class UserDTO(BaseModel):
    """
    DTO para representar um usuário.

    Atributos:
        id (int): ID do usuário.
        name (str): Nome do usuário.
        surname (str): Sobrenome do usuário.
        role (UserRole): Papel do usuário.
        email (EmailStr): Endereço de email do usuário.
        department_id (Optional[int]): ID do departamento do usuário (opcional).
        updated_at (datetime): Data e hora da última atualização.
        created_at (datetime): Data e hora da criação.
    """
    id: int
    name: str
    surname: str
    role: UserRole
    email: EmailStr
    department_id: Optional[int] = None
    updated_at: datetime
    created_at: datetime
    
    class Config:
        """Configurações do Pydantic para este modelo."""
        from_attributes = True # Permite criar o modelo a partir de atributos de um objeto (ex: ORM model)

class UserUpdateNameDTO(BaseModel):
    """
    DTO para atualizar o nome e sobrenome de um usuário.

    Atributos:
        name (str): Novo nome do usuário (mínimo 2, máximo 100 caracteres).
        surname (str): Novo sobrenome do usuário (mínimo 2, máximo 100 caracteres).
    """
    name: str = Field(..., min_length=2, max_length=100)
    surname: str = Field(..., min_length=2, max_length=100)
    
    @field_validator('name', 'surname')
    @classmethod
    def validate_name(cls, v: str) -> str:
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
                'empty_string',
                'String cannot be empty or just whitespace'
            )
        # Remove espaços extras e garante a capitalização correta
        return ' '.join(word.capitalize() for word in v.strip().split())

class UserLoginDTO(BaseModel):
    """
    DTO para autenticação de usuário (login).

    Atributos:
        email (EmailStr): Endereço de email do usuário.
        password (str): Senha do usuário (mínimo 8 caracteres).
    """
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """
        Valida o email do usuário.

        Args:
            v (str): O valor a ser validado.

        Returns:
            str: O valor validado (em minúsculas).
        """
        # Converte o email para minúsculas
        return v.lower()

class UserUpdatePassDTO(BaseModel):
    """
    DTO para atualizar a senha de um usuário.

    Atributos:
        old_password (str): Senha antiga do usuário (mínimo 8 caracteres).
        new_password (str): Nova senha do usuário (mínimo 8 caracteres, requisitos de complexidade).
    """
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8, 
                           description="Password must have at least 8 characters, one uppercase letter, one lowercase letter, one number, and one special character")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """
        Valida a nova senha do usuário.

        Args:
            v (str): O valor a ser validado.

        Returns:
            str: O valor validado.

        Raises:
            PydanticCustomError: Se a senha não atender aos requisitos de complexidade.
        """
        # Validação manual da senha em vez de usar regex
        if len(v) < 8:
            raise PydanticCustomError('password_too_short', 'Password must be at least 8 characters')
            
        has_lowercase = any(c.islower() for c in v)
        has_uppercase = any(c.isupper() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in '@$!%*?&#' for c in v)
        
        if not (has_lowercase and has_uppercase and has_digit and has_special):
            raise PydanticCustomError(
                'password_requirements',
                'Password must have at least one uppercase letter, one lowercase letter, one number, and one special character'
            )
        return v

    @model_validator(mode='after')
    def check_passwords_different(self) -> 'UserUpdatePassDTO':
        """
        Valida se a nova senha é diferente da senha antiga.

        Returns:
            UserUpdatePassDTO: O objeto DTO validado.

        Raises:
            ValueError: Se a nova senha for igual à senha antiga.
        """
        if self.old_password == self.new_password:
            raise ValueError('New password must be different from the old password')
        return self

# Token
class Token(BaseModel):
    """
    DTO para representar um token de autenticação.

    Atributos:
        user_id (int): ID do usuário associado ao token.
        role (str): Papel do usuário associado ao token.
    """
    user_id: int
    role: str

# DEPARTMENT (Departamento)
class DepartmentBase(BaseModel):
    """
    DTO base para representar um departamento.

    Atributos:
        name (str): Nome do departamento (mínimo 2, máximo 100 caracteres).
        code (str): Código do departamento (mínimo 2, máximo 20 caracteres, formato alfanumérico com hífens).
        description (Optional[str]): Descrição do departamento (opcional, máximo 500 caracteres).
    """
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=20, pattern=r'^[A-Z0-9-]+$')
    description: Optional[str] = Field(None, max_length=500)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
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
            raise ValueError('Department name cannot be empty')
        return v.strip()
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        """
        Valida o código do departamento.

        Args:
            v (str): O valor a ser validado.

        Returns:
            str: O valor validado (em maiúsculas).
        """
        # Converte para maiúsculas
        return v.upper()

class DepartmentCreate(DepartmentBase):
    """
    DTO para a criação de um departamento.

    Atributos:
        manager_id (Optional[int]): ID do gerente do departamento (opcional).
    """
    manager_id: Optional[int] = None

class DepartmentResponse(DepartmentBase):
    """
    DTO para representar a resposta de um departamento.

    Atributos:
        id (int): ID do departamento.
        manager_id (Optional[int]): ID do gerente do departamento (opcional).
        created_at (datetime): Data e hora da criação.
        updated_at (datetime): Data e hora da última atualização.
    """
    id: int
    manager_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Configurações do Pydantic para este modelo."""
        from_attributes = True # Permite criar o modelo a partir de atributos de um objeto (ex: ORM model)

# ROOM RESOURCE (Recurso da Sala)
class RoomResourceBase(BaseModel):
    """
    DTO base para representar um recurso de sala.

    Atributos:
        resource_name (str): Nome do recurso (mínimo 2, máximo 100 caracteres).
        quantity (int): Quantidade do recurso (mínimo 1, máximo 1000).
        description (Optional[str]): Descrição do recurso (opcional, máximo 500 caracteres).
    """
    resource_name: str = Field(..., min_length=2, max_length=100)
    quantity: int = Field(1, ge=1, le=1000)
    description: Optional[str] = Field(None, max_length=500)
    
    @field_validator('resource_name')
    @classmethod
    def validate_resource_name(cls, v: str) -> str:
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
            raise ValueError('Resource name cannot be empty')
        # Capitaliza a primeira letra de cada palavra
        return ' '.join(word.capitalize() for word in v.strip().split())

class RoomResourceCreate(RoomResourceBase):
    """
    DTO para a criação de um recurso de sala.
    """
    pass

class RoomResourceResponse(RoomResourceBase):
    """
    DTO para representar a resposta de um recurso de sala.

    Atributos:
        id (int): ID do recurso.
        room_id (int): ID da sala associada ao recurso.
        created_at (datetime): Data e hora da criação.
        updated_at (datetime): Data e hora da última atualização.
    """
    id: int
    room_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Configurações do Pydantic para este modelo."""
        from_attributes = True # Permite criar o modelo a partir de atributos de um objeto (ex: ORM model)

# ROOM (Sala)
class RoomBase(BaseModel):
    """
    DTO base para representar uma sala.

    Atributos:
        code (str): Código da sala (mínimo 2, máximo 20 caracteres, formato alfanumérico com hífens).
        name (str): Nome da sala (mínimo 2, máximo 100 caracteres).
        capacity (int): Capacidade da sala (maior que 0, menor ou igual a 1000).
        building (str): Edifício da sala (mínimo 1, máximo 100 caracteres).
        floor (str): Andar da sala (mínimo 1, máximo 20 caracteres).
        department_id (int): ID do departamento da sala (maior que 0).
        status (RoomStatus): Status da sala (padrão: RoomStatus.ATIVA).
        responsible (Optional[str]): Responsável pela sala (opcional, mínimo 2, máximo 100 caracteres).
        description (Optional[str]): Descrição da sala (opcional, máximo 500 caracteres).
    """
    code: str = Field(..., min_length=2, max_length=20, pattern=r'^[A-Z0-9-]+$')
    name: str = Field(..., min_length=2, max_length=100)
    capacity: int = Field(..., gt=0, le=1000)
    building: str = Field(..., min_length=1, max_length=100)
    floor: str = Field(..., min_length=1, max_length=20)
    department_id: int = Field(..., gt=0)
    status: RoomStatus = RoomStatus.ATIVA
    responsible: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        """
        Valida o código da sala.

        Args:
            v (str): O valor a ser validado.

        Returns:
            str: O valor validado (em maiúsculas).
        """
        # Converte para maiúsculas
        return v.upper()
    
    @field_validator('name', 'building', 'responsible')
    @classmethod
    def validate_text_fields(cls, v: Optional[str], info: Any) -> Optional[str]:
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
        if v is None and info.field_name == 'responsible':
            return None
        if not v or not v.strip():
            raise ValueError(f'{info.field_name.capitalize()} cannot be empty')
        # Capitaliza a primeira letra de cada palavra
        return ' '.join(word.capitalize() for word in v.strip().split())

class RoomCreate(RoomBase):
    """
    DTO para a criação de uma sala.

    Atributos:
        resources (Optional[List[RoomResourceCreate]]): Lista de recursos da sala (opcional).
    """
    resources: Optional[List[RoomResourceCreate]] = None

class RoomUpdate(BaseModel):
    """
    DTO para atualizar os dados de uma sala.

    Atributos:
        name (Optional[str]): Novo nome da sala (mínimo 2, máximo 100 caracteres, opcional).
        capacity (Optional[int]): Nova capacidade da sala (maior que 0, menor ou igual a 1000, opcional).
        building (Optional[str]): Novo edifício da sala (mínimo 1, máximo 100 caracteres, opcional).
        floor (Optional[str]): Novo andar da sala (mínimo 1, máximo 20 caracteres, opcional).
        department_id (Optional[int]): Novo ID do departamento da sala (maior que 0, opcional).
        status (Optional[RoomStatus]): Novo status da sala (opcional).
        responsible (Optional[str]): Novo responsável pela sala (mínimo 2, máximo 100 caracteres, opcional).
        description (Optional[str]): Nova descrição da sala (opcional, máximo 500 caracteres).
        resources (Optional[List[RoomResourceCreate]]): Nova lista de recursos da sala (opcional).
    """
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    capacity: Optional[int] = Field(None, gt=0, le=1000)
    building: Optional[str] = Field(None, min_length=1, max_length=100)
    floor: Optional[str] = Field(None, min_length=1, max_length=20)
    department_id: Optional[int] = Field(None, gt=0)
    status: Optional[RoomStatus] = None
    responsible: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    resources: Optional[List[RoomResourceCreate]] = None

    @field_validator('name', 'building', 'responsible')
    @classmethod
    def validate_text_fields(cls, v: Optional[str], info: Any) -> Optional[str]:
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
        if not v.strip():
            raise ValueError(f'{info.field_name.capitalize()} cannot be empty when provided')
        # Capitaliza a primeira letra de cada palavra
        return ' '.join(word.capitalize() for word in v.strip().split())

class RoomResponse(RoomBase):
    """
    DTO para representar a resposta de uma sala.

    Atributos:
        id (int): ID da sala.
        resources (List[RoomResourceResponse]): Lista de recursos da sala.
        created_at (datetime): Data e hora da criação.
        updated_at (datetime): Data e hora da última atualização.
    """
    id: int
    resources: List[RoomResourceResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        """Configurações do Pydantic para este modelo."""
        from_attributes = True # Permite criar o modelo a partir de atributos de um objeto (ex: ORM model)

# RESERVATION (Reserva)
class ReservationBase(BaseModel):
    """
    DTO base para representar uma reserva.

    Atributos:
        room_id (int): ID da sala reservada (maior que 0).
        title (str): Título da reserva (mínimo 3, máximo 100 caracteres).
        description (Optional[str]): Descrição da reserva (opcional, máximo 500 caracteres).
        start_datetime (datetime): Data e hora de início da reserva.
        end_datetime (datetime): Data e hora de término da reserva.
    """
    room_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    start_datetime: datetime
    end_datetime: datetime

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
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
            raise ValueError('Title cannot be empty')
        # Capitaliza a primeira letra
        return v.strip().capitalize()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
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
    def validate_datetime_constraints(self) -> 'ReservationBase':
        """
        Valida as restrições de data e hora da reserva.

        Returns:
            ReservationBase: O objeto DTO validado.

        Raises:
            ValueError: Se as restrições de data e hora não forem atendidas (fim antes do início, duração mínima/máxima, tempo no passado, aviso prévio mínimo/máximo).
        """
        # Verifica se o horário de término é posterior ao horário de início
        if self.end_datetime <= self.start_datetime:
            raise ValueError('End time must be after start time')
        
        # Verifica a duração mínima (30 minutos)
        min_duration = timedelta(minutes=30)
        if self.end_datetime - self.start_datetime < min_duration:
            raise ValueError('Reservation must be at least 30 minutes long')
        
        # Verifica a duração máxima (8 horas)
        max_duration = timedelta(hours=8)
        if self.end_datetime - self.start_datetime > max_duration:
            raise ValueError('Reservation cannot exceed 8 hours')
        
        # Verifica se o horário de início é no futuro
        now = datetime.now(timezone.utc)
        if self.start_datetime < now:
            raise ValueError('Start time must be in the future')
        
        # Verifica o aviso prévio mínimo (2 horas)
        min_advance = timedelta(hours=2)
        if self.start_datetime - now < min_advance:
            raise ValueError('Reservations must be made at least 2 hours in advance')
        
        # Verifica o aviso prévio máximo (30 dias)
        max_advance = timedelta(days=30)
        if self.start_datetime - now > max_advance:
            raise ValueError('Reservations cannot be made more than 30 days in advance')
        
        return self

class ReservationCreate(ReservationBase):
    """
    DTO para a criação de uma reserva.
    """
    pass

class ReservationUpdate(BaseModel):
    """
    DTO para atualizar os dados de uma reserva.

    Atributos:
        title (Optional[str]): Novo título da reserva (mínimo 3, máximo 100 caracteres, opcional).
        description (Optional[str]): Nova descrição da reserva (opcional, máximo 500 caracteres).
        start_datetime (Optional[datetime]): Nova data e hora de início da reserva (opcional).
        end_datetime (Optional[datetime]): Nova data e hora de término da reserva (opcional).
        status (Optional[ReservationStatus]): Novo status da reserva (opcional).
        cancellation_reason (Optional[str]): Motivo do cancelamento (opcional, máximo 500 caracteres).
    """
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    status: Optional[ReservationStatus] = None
    cancellation_reason: Optional[str] = Field(None, max_length=500)
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
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
            raise ValueError('Title cannot be empty when provided')
        # Capitaliza a primeira letra
        return v.strip().capitalize()
    
    @field_validator('description', 'cancellation_reason')
    @classmethod
    def validate_text_fields(cls, v: Optional[str]) -> Optional[str]:
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
    def validate_datetime_constraints(self) -> 'ReservationUpdate':
        """
        Valida as restrições de data e hora da reserva para atualização.

        Returns:
            ReservationUpdate: O objeto DTO validado.

        Raises:
            ValueError: Se as restrições de data e hora não forem atendidas (fim antes do início, duração mínima/máxima, tempo no passado, aviso prévio mínimo/máximo).
        """
        # Ignora a validação se nem a data de início nem a data de término forem fornecidas
        if self.start_datetime is None and self.end_datetime is None:
            return self
        
        # Se apenas um for fornecido, não podemos validar o relacionamento
        if self.start_datetime is None or self.end_datetime is None:
            raise ValueError('Both start and end times must be provided together')
        
        # Verifica se o horário de término é posterior ao horário de início
        if self.end_datetime <= self.start_datetime:
            raise ValueError('End time must be after start time')
        
        # Verifica a duração mínima (30 minutos)
        min_duration = timedelta(minutes=30)
        if self.end_datetime - self.start_datetime < min_duration:
            raise ValueError('Reservation must be at least 30 minutes long')
        
        # Verifica a duração máxima (8 horas)
        max_duration = timedelta(hours=8)
        if self.end_datetime - self.start_datetime > max_duration:
            raise ValueError('Reservation cannot exceed 8 hours')
        
        # Verifica se o horário de início é no futuro
        now = datetime.now(timezone.utc)
        if self.start_datetime < now:
            raise ValueError('Start time must be in the future')
        
        # Verifica o aviso prévio mínimo (2 horas)
        min_advance = timedelta(hours=2)
        if self.start_datetime - now < min_advance:
            raise ValueError('Reservations must be made at least 2 hours in advance')
        
        # Verifica o aviso prévio máximo (30 dias)
        max_advance = timedelta(days=30)
        if self.start_datetime - now > max_advance:
            raise ValueError('Reservations cannot be made more than 30 days in advance')
        
        return self

class ReservationResponse(ReservationBase):
    """
    DTO para representar a resposta de uma reserva.

    Atributos:
        id (int): ID da reserva.
        user_id (int): ID do usuário que fez a reserva.
        status (ReservationStatus): Status da reserva.
        approved_by (Optional[int]): ID do usuário que aprovou a reserva (opcional).
        approved_at (Optional[datetime]): Data e hora da aprovação (opcional).
        cancellation_reason (Optional[str]): Motivo do cancelamento (opcional).
        created_at (datetime): Data e hora da criação.
        updated_at (datetime): Data e hora da última atualização.
    """
    id: int
    user_id: int
    status: ReservationStatus
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Configurações do Pydantic para este modelo."""
        from_attributes = True # Permite criar o modelo a partir de atributos de um objeto (ex: ORM model)

# REPORT (Relatório)
class RoomOccupancyReport(BaseModel):
    """
    DTO para representar um relatório de ocupação de sala.

    Atributos:
        room_id (int): ID da sala.
        room_code (str): Código da sala.
        room_name (str): Nome da sala.
        total_reservations (int): Total de reservas da sala.
        total_hours (float): Total de horas reservadas na sala.
        occupancy_rate (float): Taxa de ocupação da sala (percentual).
    """
    room_id: int
    room_code: str
    room_name: str
    total_reservations: int
    total_hours: float
    occupancy_rate: float  # Percentual de ocupação

class DepartmentUsageReport(BaseModel):
    """
    DTO para representar um relatório de uso de departamento.

    Atributos:
        department_id (int): ID do departamento.
        department_name (str): Nome do departamento.
        total_rooms (int): Total de salas no departamento.
        total_reservations (int): Total de reservas feitas pelo departamento.
        rooms_usage (List[RoomOccupancyReport]): Lista de relatórios de ocupação de salas do departamento.
    """
    department_id: int
    department_name: str
    total_rooms: int
    total_reservations: int
    rooms_usage: List[RoomOccupancyReport]

class UserActivityReport(BaseModel):
    """
    DTO para representar um relatório de atividade de usuário.

    Atributos:
        user_id (int): ID do usuário.
        user_name (str): Nome do usuário.
        total_reservations (int): Total de reservas feitas pelo usuário.
        total_hours (float): Total de horas reservadas pelo usuário.
        reservations_by_status (dict): Contagem de reservas por status.
    """
    user_id: int
    user_name: str
    total_reservations: int
    total_hours: float
    reservations_by_status: dict  # Contagem por status