"""
Módulo de Definição de Enums para a Aplicação SalasTech.

Este módulo contém as definições de enumeradores (enums) utilizados
em várias partes do sistema, especialmente nos modelos de banco de dados.
Os enums garantem que certos campos possuam um conjunto restrito e
predefinido de valores, promovendo a integridade dos dados e a clareza
do código.
"""

from enum import StrEnum

class UserRole(StrEnum):
    """
    Enumeração para os diferentes papéis (roles) que um usuário pode ter no sistema.

    Define os níveis de permissão e acesso de um usuário, permitindo
    controlar funcionalidades e visibilidade de informações.
    """
    ADMIN = "admin" # Papel de administrador principal do sistema, com acesso total e irrestrito.
    USER = "user" # Papel de usuário padrão, com permissões básicas para realizar operações comuns (ex: fazer reservas).
    GUEST = "guest" # Papel de convidado, com permissões muito limitadas (ex: apenas visualizar salas, sem poder reservar).
    ADMINISTRADOR = "administrador" # Um papel de administrador, possivelmente uma alternativa ou sinônimo para 'ADMIN'.
    GESTOR = "gestor" # Papel de gestor, com permissões elevadas para gerenciar recursos ou departamentos (ex: aprovar reservas).
    USUARIO_AVANCADO = "usuario_avancado" # Papel para usuários com mais privilégios que um 'USER', mas não um 'GESTOR' ou 'ADMIN'.


class RoomStatus(StrEnum):
    """
    Enumeração para o status atual de uma sala.

    Indica a disponibilidade e a condição operacional da sala para uso e reservas.
    """
    ATIVA = "ativa" # A sala está em condições normais de uso e disponível para reservas.
    INATIVA = "inativa" # A sala está fora de serviço permanentemente ou por um longo período, não disponível para reservas.
    MANUTENCAO = "manutencao" # A sala está temporariamente indisponível devido a atividades de manutenção ou reparos.


class ReservationStatus(StrEnum):
    """
    Enumeração para o status do ciclo de vida de uma reserva de sala.

    Detalha em que fase uma reserva se encontra, desde sua criação até sua conclusão ou cancelamento.
    """
    PENDENTE = "pendente" # A reserva foi solicitada e está aguardando aprovação de um gestor ou sistema.
    CONFIRMADA = "confirmada" # A reserva foi aprovada e está agendada para ocorrer.
    CANCELADA = "cancelada" # A reserva foi cancelada, seja pelo usuário que a fez ou por um gestor.
    CONCLUIDA = "concluida" # O período da reserva já se encerrou, indicando que o uso da sala foi concluído.
    EM_ANDAMENTO = "em_andamento" # A reserva está ocorrendo no momento atual.