"""
Testes para os modelos do sistema de gerenciamento de salas.
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
from core.security.password import get_password_hash, verify_password


class TestModels:
    """Testes para os modelos do banco de dados."""
    
    def test_department_model(self, db_session):
        """Testa a criação e recuperação de um departamento."""
        # Cria um departamento
        department = DepartmentDb(
            name="Departamento de Teste",
            code="TEST",
            description="Departamento para testes"
        )
        db_session.add(department)
        db_session.commit()
        
        # Recupera o departamento
        saved_department = db_session.query(DepartmentDb).filter_by(code="TEST").first()
        
        # Verifica se o departamento foi salvo corretamente
        assert saved_department is not None
        assert saved_department.name == "Departamento de Teste"
        assert saved_department.code == "TEST"
        assert saved_department.description == "Departamento para testes"
    
    def test_user_model(self, db_session):
        """Testa a criação e recuperação de um usuário."""
        # Cria um departamento para o usuário
        department = DepartmentDb(
            name="Departamento de Teste",
            code="TEST",
            description="Departamento para testes"
        )
        db_session.add(department)
        db_session.commit()
        
        # Cria um usuário
        password_hash = get_password_hash("senha123")
        user = UserDb(
            name="Usuário",
            surname="Teste",
            role=UserRole.USER,
            email="usuario.teste@ifam.edu.br",
            password=password_hash,
            department_id=department.id
        )
        db_session.add(user)
        db_session.commit()
        
        # Recupera o usuário
        saved_user = db_session.query(UserDb).filter_by(email="usuario.teste@ifam.edu.br").first()
        
        # Verifica se o usuário foi salvo corretamente
        assert saved_user is not None
        assert saved_user.name == "Usuário"
        assert saved_user.surname == "Teste"
        assert saved_user.role == UserRole.USER
        assert saved_user.email == "usuario.teste@ifam.edu.br"
        assert verify_password("senha123", saved_user.password)
        assert saved_user.department_id == department.id
        
        # Verifica o relacionamento com o departamento
        assert saved_user.department.name == "Departamento de Teste"
    
    def test_room_model(self, db_session):
        """Testa a criação e recuperação de uma sala."""
        # Cria um departamento para a sala
        department = DepartmentDb(
            name="Departamento de Teste",
            code="TEST",
            description="Departamento para testes"
        )
        db_session.add(department)
        db_session.commit()
        
        # Cria uma sala
        room = RoomDb(
            code="TEST-001",
            name="Sala de Teste",
            capacity=30,
            building="Bloco de Teste",
            floor="1º Andar",
            department_id=department.id,
            status=RoomStatus.ATIVA,
            responsible="Responsável de Teste",
            description="Sala para testes"
        )
        db_session.add(room)
        db_session.commit()
        
        # Recupera a sala
        saved_room = db_session.query(RoomDb).filter_by(code="TEST-001").first()
        
        # Verifica se a sala foi salva corretamente
        assert saved_room is not None
        assert saved_room.code == "TEST-001"
        assert saved_room.name == "Sala de Teste"
        assert saved_room.capacity == 30
        assert saved_room.building == "Bloco de Teste"
        assert saved_room.floor == "1º Andar"
        assert saved_room.department_id == department.id
        assert saved_room.status == RoomStatus.ATIVA
        assert saved_room.responsible == "Responsável de Teste"
        assert saved_room.description == "Sala para testes"
        
        # Verifica o relacionamento com o departamento
        assert saved_room.department.name == "Departamento de Teste"
    
    def test_room_resource_model(self, db_session):
        """Testa a criação e recuperação de um recurso de sala."""
        # Cria um departamento para a sala
        department = DepartmentDb(
            name="Departamento de Teste",
            code="TEST",
            description="Departamento para testes"
        )
        db_session.add(department)
        db_session.commit()
        
        # Cria uma sala para o recurso
        room = RoomDb(
            code="TEST-001",
            name="Sala de Teste",
            capacity=30,
            building="Bloco de Teste",
            floor="1º Andar",
            department_id=department.id,
            status=RoomStatus.ATIVA,
            responsible="Responsável de Teste",
            description="Sala para testes"
        )
        db_session.add(room)
        db_session.commit()
        
        # Cria um recurso para a sala
        resource = RoomResourceDb(
            room_id=room.id,
            resource_name="Projetor de Teste",
            quantity=2,
            description="Projetor para testes"
        )
        db_session.add(resource)
        db_session.commit()
        
        # Recupera o recurso
        saved_resource = db_session.query(RoomResourceDb).filter_by(resource_name="Projetor de Teste").first()
        
        # Verifica se o recurso foi salvo corretamente
        assert saved_resource is not None
        assert saved_resource.room_id == room.id
        assert saved_resource.resource_name == "Projetor de Teste"
        assert saved_resource.quantity == 2
        assert saved_resource.description == "Projetor para testes"
        
        # Verifica o relacionamento com a sala
        assert saved_resource.room.code == "TEST-001"
    
    def test_reservation_model(self, db_session):
        """Testa a criação e recuperação de uma reserva."""
        # Cria um departamento
        department = DepartmentDb(
            name="Departamento de Teste",
            code="TEST",
            description="Departamento para testes"
        )
        db_session.add(department)
        db_session.commit()
        
        # Cria uma sala para a reserva
        room = RoomDb(
            code="TEST-001",
            name="Sala de Teste",
            capacity=30,
            building="Bloco de Teste",
            floor="1º Andar",
            department_id=department.id,
            status=RoomStatus.ATIVA,
            responsible="Responsável de Teste",
            description="Sala para testes"
        )
        db_session.add(room)
        
        # Cria um usuário para a reserva
        password_hash = get_password_hash("senha123")
        user = UserDb(
            name="Usuário",
            surname="Teste",
            role=UserRole.USER,
            email="usuario.teste@ifam.edu.br",
            password=password_hash,
            department_id=department.id
        )
        db_session.add(user)
        
        # Cria um administrador para aprovar a reserva
        admin = UserDb(
            name="Admin",
            surname="Teste",
            role=UserRole.ADMIN,
            email="admin.teste@ifam.edu.br",
            password=password_hash,
            department_id=department.id
        )
        db_session.add(admin)
        db_session.commit()
        
        # Define datas para a reserva
        now = datetime.now()
        start_datetime = now + timedelta(days=1)
        end_datetime = start_datetime + timedelta(hours=2)
        
        # Cria uma reserva
        reservation = ReservationDb(
            room_id=room.id,
            user_id=user.id,
            title="Reserva de Teste",
            description="Reserva para testes",
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            status=ReservationStatus.CONFIRMADA,
            approved_by=admin.id,
            approved_at=now
        )
        db_session.add(reservation)
        db_session.commit()
        
        # Recupera a reserva
        saved_reservation = db_session.query(ReservationDb).filter_by(title="Reserva de Teste").first()
        
        # Verifica se a reserva foi salva corretamente
        assert saved_reservation is not None
        assert saved_reservation.room_id == room.id
        assert saved_reservation.user_id == user.id
        assert saved_reservation.title == "Reserva de Teste"
        assert saved_reservation.description == "Reserva para testes"
        assert saved_reservation.start_datetime == start_datetime
        assert saved_reservation.end_datetime == end_datetime
        assert saved_reservation.status == ReservationStatus.CONFIRMADA
        assert saved_reservation.approved_by == admin.id
        assert saved_reservation.approved_at == now
        
        # Verifica os relacionamentos
        assert saved_reservation.room.code == "TEST-001"
        assert saved_reservation.user.email == "usuario.teste@ifam.edu.br"
        assert saved_reservation.approved_by_user.email == "admin.teste@ifam.edu.br"
