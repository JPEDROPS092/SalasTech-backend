"""
Testes para os serviços do sistema de gerenciamento de salas.
"""

import pytest
from datetime import datetime, timedelta

from models.db import (
    DepartmentDb, 
    UserDb, 
    RoomDb, 
    RoomResourceDb, 
    ReservationDb
)
from models.enums import UserRole, RoomStatus, ReservationStatus
from services.room_service import RoomService
from services.reservation_service import ReservationService
from services.user_service import UserService


class TestRoomService:
    """Testes para o serviço de salas."""
    
    def test_get_all_rooms(self, db_session, seed_test_data):
        """Testa a obtenção de todas as salas."""
        # Inicializa o serviço
        room_service = RoomService(db_session)
        
        # Obtém todas as salas
        rooms = room_service.get_all_rooms()
        
        # Verifica se as salas foram obtidas corretamente
        assert len(rooms) > 0
        assert all(isinstance(room, RoomDb) for room in rooms)
    
    def test_get_room_by_id(self, db_session, seed_test_data):
        """Testa a obtenção de uma sala por ID."""
        # Inicializa o serviço
        room_service = RoomService(db_session)
        
        # Obtém uma sala existente
        room_id = seed_test_data["rooms"][0].id
        room = room_service.get_room_by_id(room_id)
        
        # Verifica se a sala foi obtida corretamente
        assert room is not None
        assert room.id == room_id
    
    def test_get_available_rooms(self, db_session, seed_test_data):
        """Testa a obtenção de salas disponíveis."""
        # Inicializa o serviço
        room_service = RoomService(db_session)
        
        # Define o período para busca de disponibilidade
        now = datetime.now()
        start_datetime = now + timedelta(days=1)
        end_datetime = start_datetime + timedelta(hours=2)
        
        # Obtém salas disponíveis
        available_rooms = room_service.get_available_rooms(start_datetime, end_datetime)
        
        # Verifica se as salas disponíveis foram obtidas corretamente
        assert isinstance(available_rooms, list)
        # Salas inativas ou em manutenção não devem estar disponíveis
        assert all(room.status == RoomStatus.ATIVA for room in available_rooms)
    
    def test_create_room(self, db_session, seed_test_data):
        """Testa a criação de uma sala."""
        # Inicializa o serviço
        room_service = RoomService(db_session)
        
        # Define os dados da nova sala
        department_id = seed_test_data["departments"][0].id
        new_room_data = {
            "code": "TEST-999",
            "name": "Nova Sala de Teste",
            "capacity": 25,
            "building": "Bloco de Teste",
            "floor": "2º Andar",
            "department_id": department_id,
            "status": RoomStatus.ATIVA,
            "responsible": "Responsável de Teste",
            "description": "Nova sala para testes"
        }
        
        # Cria a sala
        new_room = room_service.create_room(new_room_data)
        
        # Verifica se a sala foi criada corretamente
        assert new_room is not None
        assert new_room.code == "TEST-999"
        assert new_room.name == "Nova Sala de Teste"
        assert new_room.capacity == 25
        assert new_room.department_id == department_id
    
    def test_update_room(self, db_session, seed_test_data):
        """Testa a atualização de uma sala."""
        # Inicializa o serviço
        room_service = RoomService(db_session)
        
        # Obtém uma sala existente
        room_id = seed_test_data["rooms"][0].id
        
        # Define os dados atualizados
        updated_data = {
            "name": "Sala Atualizada",
            "capacity": 40,
            "description": "Descrição atualizada"
        }
        
        # Atualiza a sala
        updated_room = room_service.update_room(room_id, updated_data)
        
        # Verifica se a sala foi atualizada corretamente
        assert updated_room is not None
        assert updated_room.id == room_id
        assert updated_room.name == "Sala Atualizada"
        assert updated_room.capacity == 40
        assert updated_room.description == "Descrição atualizada"
    
    def test_delete_room(self, db_session, seed_test_data):
        """Testa a exclusão de uma sala."""
        # Inicializa o serviço
        room_service = RoomService(db_session)
        
        # Obtém uma sala existente
        room_id = seed_test_data["rooms"][0].id
        
        # Exclui a sala
        result = room_service.delete_room(room_id)
        
        # Verifica se a sala foi excluída corretamente
        assert result is True
        
        # Verifica se a sala não existe mais
        deleted_room = room_service.get_room_by_id(room_id)
        assert deleted_room is None


class TestReservationService:
    """Testes para o serviço de reservas."""
    
    def test_get_all_reservations(self, db_session, seed_test_data):
        """Testa a obtenção de todas as reservas."""
        # Inicializa o serviço
        reservation_service = ReservationService(db_session)
        
        # Obtém todas as reservas
        reservations = reservation_service.get_all_reservations()
        
        # Verifica se as reservas foram obtidas corretamente
        assert len(reservations) > 0
        assert all(isinstance(reservation, ReservationDb) for reservation in reservations)
    
    def test_get_reservation_by_id(self, db_session, seed_test_data):
        """Testa a obtenção de uma reserva por ID."""
        # Inicializa o serviço
        reservation_service = ReservationService(db_session)
        
        # Obtém uma reserva existente
        reservation_id = seed_test_data["reservations"][0].id
        reservation = reservation_service.get_reservation_by_id(reservation_id)
        
        # Verifica se a reserva foi obtida corretamente
        assert reservation is not None
        assert reservation.id == reservation_id
    
    def test_create_reservation(self, db_session, seed_test_data):
        """Testa a criação de uma reserva."""
        # Inicializa o serviço
        reservation_service = ReservationService(db_session)
        
        # Define os dados da nova reserva
        room_id = seed_test_data["rooms"][0].id
        user_id = seed_test_data["users"][0].id
        
        # Define datas para a reserva
        now = datetime.now()
        start_datetime = now + timedelta(days=2)
        end_datetime = start_datetime + timedelta(hours=3)
        
        new_reservation_data = {
            "room_id": room_id,
            "user_id": user_id,
            "title": "Nova Reserva de Teste",
            "description": "Nova reserva para testes",
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "status": ReservationStatus.PENDENTE
        }
        
        # Cria a reserva
        new_reservation = reservation_service.create_reservation(new_reservation_data)
        
        # Verifica se a reserva foi criada corretamente
        assert new_reservation is not None
        assert new_reservation.room_id == room_id
        assert new_reservation.user_id == user_id
        assert new_reservation.title == "Nova Reserva de Teste"
        assert new_reservation.status == ReservationStatus.PENDENTE
    
    def test_update_reservation(self, db_session, seed_test_data):
        """Testa a atualização de uma reserva."""
        # Inicializa o serviço
        reservation_service = ReservationService(db_session)
        
        # Obtém uma reserva existente
        reservation_id = seed_test_data["reservations"][0].id
        
        # Define os dados atualizados
        updated_data = {
            "title": "Reserva Atualizada",
            "description": "Descrição atualizada"
        }
        
        # Atualiza a reserva
        updated_reservation = reservation_service.update_reservation(reservation_id, updated_data)
        
        # Verifica se a reserva foi atualizada corretamente
        assert updated_reservation is not None
        assert updated_reservation.id == reservation_id
        assert updated_reservation.title == "Reserva Atualizada"
        assert updated_reservation.description == "Descrição atualizada"
    
    def test_approve_reservation(self, db_session, seed_test_data):
        """Testa a aprovação de uma reserva."""
        # Inicializa o serviço
        reservation_service = ReservationService(db_session)
        
        # Cria uma reserva pendente
        room_id = seed_test_data["rooms"][0].id
        user_id = seed_test_data["users"][0].id
        approver_id = seed_test_data["users"][1].id
        
        # Define datas para a reserva
        now = datetime.now()
        start_datetime = now + timedelta(days=3)
        end_datetime = start_datetime + timedelta(hours=2)
        
        new_reservation_data = {
            "room_id": room_id,
            "user_id": user_id,
            "title": "Reserva para Aprovação",
            "description": "Reserva para teste de aprovação",
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "status": ReservationStatus.PENDENTE
        }
        
        # Cria a reserva
        new_reservation = reservation_service.create_reservation(new_reservation_data)
        
        # Aprova a reserva
        approved_reservation = reservation_service.approve_reservation(new_reservation.id, approver_id)
        
        # Verifica se a reserva foi aprovada corretamente
        assert approved_reservation is not None
        assert approved_reservation.id == new_reservation.id
        assert approved_reservation.status == ReservationStatus.CONFIRMADA
        assert approved_reservation.approved_by == approver_id
        assert approved_reservation.approved_at is not None
    
    def test_cancel_reservation(self, db_session, seed_test_data):
        """Testa o cancelamento de uma reserva."""
        # Inicializa o serviço
        reservation_service = ReservationService(db_session)
        
        # Cria uma reserva confirmada
        room_id = seed_test_data["rooms"][0].id
        user_id = seed_test_data["users"][0].id
        approver_id = seed_test_data["users"][1].id
        
        # Define datas para a reserva
        now = datetime.now()
        start_datetime = now + timedelta(days=4)
        end_datetime = start_datetime + timedelta(hours=2)
        
        new_reservation_data = {
            "room_id": room_id,
            "user_id": user_id,
            "title": "Reserva para Cancelamento",
            "description": "Reserva para teste de cancelamento",
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "status": ReservationStatus.CONFIRMADA,
            "approved_by": approver_id,
            "approved_at": now
        }
        
        # Cria a reserva
        new_reservation = reservation_service.create_reservation(new_reservation_data)
        
        # Cancela a reserva
        cancellation_reason = "Teste de cancelamento"
        cancelled_reservation = reservation_service.cancel_reservation(new_reservation.id, cancellation_reason)
        
        # Verifica se a reserva foi cancelada corretamente
        assert cancelled_reservation is not None
        assert cancelled_reservation.id == new_reservation.id
        assert cancelled_reservation.status == ReservationStatus.CANCELADA
        assert cancelled_reservation.cancellation_reason == cancellation_reason


class TestUserService:
    """Testes para o serviço de usuários."""
    
    def test_get_all_users(self, db_session, seed_test_data):
        """Testa a obtenção de todos os usuários."""
        # Inicializa o serviço
        user_service = UserService(db_session)
        
        # Obtém todos os usuários
        users = user_service.get_all_users()
        
        # Verifica se os usuários foram obtidos corretamente
        assert len(users) > 0
        assert all(isinstance(user, UserDb) for user in users)
    
    def test_get_user_by_id(self, db_session, seed_test_data):
        """Testa a obtenção de um usuário por ID."""
        # Inicializa o serviço
        user_service = UserService(db_session)
        
        # Obtém um usuário existente
        user_id = seed_test_data["users"][0].id
        user = user_service.get_user_by_id(user_id)
        
        # Verifica se o usuário foi obtido corretamente
        assert user is not None
        assert user.id == user_id
    
    def test_get_user_by_email(self, db_session, seed_test_data):
        """Testa a obtenção de um usuário por email."""
        # Inicializa o serviço
        user_service = UserService(db_session)
        
        # Obtém um usuário existente
        user_email = seed_test_data["users"][0].email
        user = user_service.get_user_by_email(user_email)
        
        # Verifica se o usuário foi obtido corretamente
        assert user is not None
        assert user.email == user_email
    
    def test_create_user(self, db_session, seed_test_data):
        """Testa a criação de um usuário."""
        # Inicializa o serviço
        user_service = UserService(db_session)
        
        # Define os dados do novo usuário
        department_id = seed_test_data["departments"][0].id
        new_user_data = {
            "name": "Novo",
            "surname": "Usuário",
            "role": UserRole.USER,
            "email": "novo.usuario@ifam.edu.br",
            "password": "senha123",
            "department_id": department_id
        }
        
        # Cria o usuário
        new_user = user_service.create_user(new_user_data)
        
        # Verifica se o usuário foi criado corretamente
        assert new_user is not None
        assert new_user.name == "Novo"
        assert new_user.surname == "Usuário"
        assert new_user.role == UserRole.USER
        assert new_user.email == "novo.usuario@ifam.edu.br"
        assert new_user.department_id == department_id
    
    def test_update_user(self, db_session, seed_test_data):
        """Testa a atualização de um usuário."""
        # Inicializa o serviço
        user_service = UserService(db_session)
        
        # Obtém um usuário existente
        user_id = seed_test_data["users"][0].id
        
        # Define os dados atualizados
        updated_data = {
            "name": "Nome Atualizado",
            "surname": "Sobrenome Atualizado"
        }
        
        # Atualiza o usuário
        updated_user = user_service.update_user(user_id, updated_data)
        
        # Verifica se o usuário foi atualizado corretamente
        assert updated_user is not None
        assert updated_user.id == user_id
        assert updated_user.name == "Nome Atualizado"
        assert updated_user.surname == "Sobrenome Atualizado"
    
    def test_authenticate_user(self, db_session, seed_test_data):
        """Testa a autenticação de um usuário."""
        # Inicializa o serviço
        user_service = UserService(db_session)
        
        # Cria um usuário para teste de autenticação
        from core.security.password import get_password_hash
        
        department_id = seed_test_data["departments"][0].id
        email = "auth.test@ifam.edu.br"
        password = "auth123"
        
        user = UserDb(
            name="Auth",
            surname="Test",
            role=UserRole.USER,
            email=email,
            password=get_password_hash(password),
            department_id=department_id
        )
        db_session.add(user)
        db_session.commit()
        
        # Testa autenticação com credenciais corretas
        authenticated_user = user_service.authenticate_user(email, password)
        assert authenticated_user is not None
        assert authenticated_user.email == email
        
        # Testa autenticação com senha incorreta
        authenticated_user = user_service.authenticate_user(email, "senha_errada")
        assert authenticated_user is None
        
        # Testa autenticação com email incorreto
        authenticated_user = user_service.authenticate_user("email_errado@ifam.edu.br", password)
        assert authenticated_user is None
