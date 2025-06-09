from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    ADMINISTRADOR = "administrador"
    GESTOR = "gestor"
    USUARIO_AVANCADO = "usuario_avancado"


class RoomStatus(StrEnum):
    ATIVA = "ativa"
    INATIVA = "inativa"
    MANUTENCAO = "manutencao"


class ReservationStatus(StrEnum):
    PENDENTE = "pendente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    FINALIZADA = "finalizada"
    EM_ANDAMENTO = "em_andamento"